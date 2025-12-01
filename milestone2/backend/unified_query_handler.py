"""
PropBot Unified Query Handler
Searches across ALL ChromaDB collections and returns comprehensive results
"""

import chromadb
from chromadb.config import Settings
from typing import Dict, List, Any
import json
from datetime import datetime
import hashlib

class UnifiedQueryHandler:
    def __init__(self, chroma_host="localhost", chroma_port=8000):
        """Initialize connection to ChromaDB"""
        self.client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Define all collections and their purposes
        self.collection_map = {
            # Primary property/rental data
            'boston_properties': 'property_listings',
            'zillow_working_boston_all_max_20251127_181854': 'rental_listings',
            'zillow_working_boston_listings_20251127_174724_flat': 'rental_details',
            'property_assessment': 'tax_assessment',
            
            # Location context
            'neighborhoods': 'neighborhood_info',
            'demographics': 'demographic_data',
            
            # Amenities
            'schools': 'education',
            'transit': 'transportation',
            'hospitals': 'healthcare',
            'parks': 'recreation',
            'yelp_businesses_20251024_185237': 'local_businesses',
            
            # Safety
            'boston_crime': 'crime_data'
        }
        
        # Load all collections
        self.collections = {}
        for collection_name, purpose in self.collection_map.items():
            try:
                self.collections[collection_name] = self.client.get_collection(collection_name)
                print(f"✅ Loaded collection: {collection_name}")
            except:
                print(f"⚠️  Collection not found: {collection_name}")
    
    def create_simple_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Create embedding for query (same as used during indexing)"""
        hash_object = hashlib.sha256(text.encode())
        hash_hex = hash_object.hexdigest()
        
        embedding = []
        for i in range(0, min(len(hash_hex), dim * 2), 2):
            value = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(value)
        
        while len(embedding) < dim:
            embedding.append(0.0)
        
        return embedding[:dim]
    
    def search_all_collections(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search across ALL collections and return unified results"""
        print(f"\n🔍 Searching for: '{query}'")
        
        query_embedding = self.create_simple_embedding(query)
        
        all_results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'results': {}
        }
        
        for collection_name, collection in self.collections.items():
            try:
                result = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                
                if result['documents'][0]:
                    all_results['results'][collection_name] = {
                        'purpose': self.collection_map.get(collection_name, 'unknown'),
                        'count': len(result['documents'][0]),
                        'documents': result['documents'][0],
                        'metadatas': result['metadatas'][0],
                        'distances': result['distances'][0]
                    }
                    print(f"  ✓ {collection_name}: {len(result['documents'][0])} results")
            except Exception as e:
                print(f"  ✗ Error searching {collection_name}: {str(e)}")
        
        return all_results
    
    def get_property_with_context(self, query: str) -> Dict[str, Any]:
        """Get property/rental results with full neighborhood context"""
        
        raw_results = self.search_all_collections(query, n_results=5)
        
        structured_response = {
            'query': query,
            'timestamp': raw_results['timestamp'],
            'properties': [],
            'rentals': [],
            'context': {}
        }
        
        for collection_name, data in raw_results['results'].items():
            if 'property' in collection_name or 'boston_properties' in collection_name:
                structured_response['properties'].extend(data['documents'])
            elif 'zillow' in collection_name or 'rental' in collection_name:
                structured_response['rentals'].extend(data['documents'])
            else:
                structured_response['context'][collection_name] = data['documents'][:3]
        
        return structured_response

if __name__ == "__main__":
    handler = UnifiedQueryHandler()
    
    test_queries = [
        "2 bedroom apartment near MIT",
        "safe family neighborhood with good schools",
        "rental near subway station"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing: {query}")
        print('='*60)
        result = handler.get_property_with_context(query)
        print(f"Found {len(result['properties'])} properties")
        print(f"Found {len(result['rentals'])} rentals")
        print(f"Context collections: {list(result['context'].keys())}")
