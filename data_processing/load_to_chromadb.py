#!/usr/bin/env python3
"""
PropBot ChromaDB Loader
Loads all cleaned CSV files into separate ChromaDB collections
"""

import pandas as pd
import chromadb
from chromadb.config import Settings
from pathlib import Path
import json
from typing import List, Dict
import hashlib
from sentence_transformers import SentenceTransformer
import numpy as np

print("="*60)
print("🚀 PROPBOT CHROMADB LOADER")
print("="*60)

class ChromaDBLoader:
    def __init__(self, host="localhost", port=8000):
        """Initialize ChromaDB client and embedding model"""
        print("\n📡 Connecting to ChromaDB...")
        
        # Try to connect to ChromaDB
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(anonymized_telemetry=False)
            )
            print("✅ Connected to ChromaDB")
        except Exception as e:
            print(f"❌ Could not connect to ChromaDB. Make sure it's running!")
            print(f"   Run: docker-compose up -d chromadb")
            raise e
        
        # Initialize embedding model
        print("🤖 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
        
        self.collections = {}
        
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        if not texts:
            return []
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def determine_collection_name(self, filename: str) -> str:
        """Determine collection name based on filename"""
        name = filename.lower()
        
        if 'crime' in name:
            return 'boston_crime'
        elif 'propert' in name and 'assessment' in name:
            return 'property_assessment'
        elif 'propert' in name:
            return 'boston_properties'
        elif 'demographic' in name:
            return 'demographics'
        elif 'school' in name or 'college' in name:
            return 'schools'
        elif 'mbta' in name or 'station' in name:
            return 'transit'
        elif 'hospital' in name:
            return 'hospitals'
        elif 'neighborhood' in name:
            return 'neighborhoods'
        elif 'open_space' in name or 'park' in name:
            return 'parks'
        elif 'police' in name:
            return 'police_stations'
        elif 'fire' in name:
            return 'fire_stations'
        else:
            # Generic name based on file
            return filename.replace('cleaned_', '').replace('.csv', '').lower()
    
    def prepare_documents(self, df: pd.DataFrame, collection_name: str) -> tuple:
        """Prepare documents, embeddings, and metadata for ChromaDB"""
        documents = []
        metadatas = []
        ids = []
        
        # Select key columns based on collection type
        if collection_name == 'boston_properties':
            text_cols = ['full_address', 'owner_name', 'land_use_code', 'LU_DESC']
            meta_cols = ['property_id', 'zip_code', 'TOTAL_VALUE', 'year_built', 
                        'BED_RMS', 'FULL_BTH', 'living_square_feet']
        elif collection_name == 'property_assessment':
            text_cols = ['Location', 'Owner', 'Building Class Description']
            meta_cols = ['Total Assessed Value', 'Year Built', 'Building Area', 'Parcel ID']
        elif collection_name == 'boston_crime':
            text_cols = ['OFFENSE_DESCRIPTION', 'STREET', 'Location']
            meta_cols = ['YEAR', 'MONTH', 'DAY_OF_WEEK', 'HOUR', 'DISTRICT']
        elif collection_name == 'schools':
            text_cols = ['school_name', 'school_name_clean', 'NAME', 'SCH_NAME', 'Address', 'ADDRESS']
            meta_cols = ['school_type', 'GRADES', 'ZIPCODE']
        elif collection_name == 'transit':
            text_cols = ['station_name', 'municipality']
            meta_cols = ['latitude', 'longitude', 'wheelchair_accessible']
        else:
            # Generic approach: use all string columns for text
            text_cols = df.select_dtypes(include=['object']).columns.tolist()[:5]
            meta_cols = df.columns.tolist()[:10]
        
        # Process each row
        for idx, row in df.iterrows():
            # Create text from available columns
            text_parts = []
            for col in text_cols:
                if col in row.index and pd.notna(row[col]):
                    text_parts.append(str(row[col]))
            
            if not text_parts:
                continue
                
            doc_text = " | ".join(text_parts)
            
            # Create metadata
            metadata = {}
            for col in meta_cols:
                if col in row.index and pd.notna(row[col]):
                    val = row[col]
                    # ChromaDB requires specific types
                    if isinstance(val, (bool, str)):
                        metadata[col] = val
                    elif isinstance(val, (int, float)):
                        if not np.isnan(val) and not np.isinf(val):
                            metadata[col] = float(val)
                    else:
                        metadata[col] = str(val)
            
            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(f"{collection_name}_{idx}")
            
            # Process in batches of 5000
            if len(documents) >= 5000:
                yield documents, metadatas, ids
                documents = []
                metadatas = []
                ids = []
        
        # Yield remaining documents
        if documents:
            yield documents, metadatas, ids
    
    def load_file_to_chromadb(self, filepath: Path) -> bool:
        """Load a single CSV file into ChromaDB"""
        try:
            filename = filepath.name
            collection_name = self.determine_collection_name(filename)
            
            print(f"\n📂 Loading {filename}")
            print(f"   Collection: {collection_name}")
            
            # Read CSV
            df = pd.read_csv(filepath, low_memory=False)
            print(f"   Rows: {len(df)}")
            
            # Create or get collection
            try:
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"   ✅ Created new collection: {collection_name}")
            except:
                collection = self.client.get_collection(name=collection_name)
                print(f"   📦 Using existing collection: {collection_name}")
            
            # Process and add documents in batches
            total_added = 0
            for batch_docs, batch_meta, batch_ids in self.prepare_documents(df, collection_name):
                if batch_docs:
                    # Create embeddings
                    embeddings = self.create_embeddings(batch_docs)
                    
                    # Add to ChromaDB
                    collection.add(
                        documents=batch_docs,
                        embeddings=embeddings,
                        metadatas=batch_meta,
                        ids=batch_ids
                    )
                    total_added += len(batch_docs)
                    print(f"   Added {total_added} documents...")
            
            print(f"   ✅ Total documents added: {total_added}")
            self.collections[collection_name] = collection
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def load_all_files(self):
        """Load all cleaned CSV files"""
        cleaned_dir = Path("cleaned_data")
        csv_files = list(cleaned_dir.glob("cleaned_*.csv"))
        
        print(f"\n📊 Found {len(csv_files)} cleaned files to load")
        
        success_count = 0
        failed_files = []
        
        for filepath in csv_files:
            if self.load_file_to_chromadb(filepath):
                success_count += 1
            else:
                failed_files.append(filepath.name)
        
        # Summary
        print("\n" + "="*60)
        print("📊 LOADING SUMMARY")
        print("="*60)
        print(f"✅ Successfully loaded: {success_count}/{len(csv_files)} files")
        print(f"📦 Collections created: {len(self.collections)}")
        
        if failed_files:
            print(f"❌ Failed files: {failed_files}")
        
        # List all collections
        print("\n📚 Available Collections:")
        for name in self.collections.keys():
            count = self.collections[name].count()
            print(f"   - {name}: {count} documents")
        
        return self.collections

def test_search(loader):
    """Test search across collections"""
    print("\n" + "="*60)
    print("🔍 TESTING SEARCH")
    print("="*60)
    
    test_queries = [
        "2 bedroom apartment near subway",
        "safe neighborhood low crime",
        "house with parking near school"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        query_embedding = loader.create_embeddings([query])[0]
        
        # Search in properties collection if it exists
        if 'boston_properties' in loader.collections:
            results = loader.collections['boston_properties'].query(
                query_embeddings=[query_embedding],
                n_results=2
            )
            if results['documents'][0]:
                print(f"  Found in properties: {results['documents'][0][0][:100]}...")

if __name__ == "__main__":
    # Check if ChromaDB is accessible
    print("\n⚠️  Make sure ChromaDB is running!")
    print("   If not, run: docker-compose up -d chromadb")
    input("\nPress Enter to continue...")
    
    try:
        # Initialize loader
        loader = ChromaDBLoader(host="localhost", port=8000)
        
        # Load all files
        collections = loader.load_all_files()
        
        # Test search
        test_search(loader)
        
        print("\n🎉 ALL DATA LOADED TO CHROMADB!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure:")
        print("1. ChromaDB is running (docker-compose up -d chromadb)")
        print("2. You have installed: pip install chromadb sentence-transformers")
