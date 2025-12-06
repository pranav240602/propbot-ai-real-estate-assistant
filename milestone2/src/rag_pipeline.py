"""
Enhanced RAG Pipeline - Interactive & User-Friendly
"""

import os
from chromadb import HttpClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional
from spellchecker import SpellChecker
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class PropBotRAG:
    """Enhanced RAG with conversation memory and personality"""
    
    def __init__(self):
        logger.info("🔧 Initializing Enhanced RAG Pipeline...")
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Loaded embedding model")
        
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        logger.info("✅ Connected to OpenAI")
        
        self.chroma_client = HttpClient(
            host='localhost',
            port=8000
        )
        logger.info("✅ Connected to ChromaDB")
        
        self.spell = SpellChecker()
        
        try:
            collections = self.chroma_client.list_collections()
            self.collection_names = [c.name for c in collections]
            logger.info(f"✅ Found {len(self.collection_names)} collections")
        except Exception as e:
            logger.error(f"❌ Failed to load collections: {e}")
            self.collection_names = []
        
        self.top_k = 5
        self.temperature = 0.7
        self.conversation_context = {}
    
    def retrieve_documents(self, query: str, collection_name: str = None, k: int = 5) -> List[Dict]:
        """Retrieve relevant documents from ChromaDB"""
        logger.info(f"🔍 Retrieving documents for: {query}")
        
        query_embedding = self.embedding_model.encode(query).tolist()
        all_results = []
        collections_to_search = [collection_name] if collection_name else self.collection_names
        
        for coll_name in collections_to_search:
            try:
                collection = self.chroma_client.get_collection(coll_name)
                
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k
                )
                
                if results['documents'][0]:
                    for idx, doc in enumerate(results['documents'][0]):
                        all_results.append({
                            'collection': coll_name,
                            'document': doc,
                            'metadata': results['metadatas'][0][idx] if results['metadatas'] else {},
                            'distance': results['distances'][0][idx] if results['distances'] else 0
                        })
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to search {coll_name}: {e}")
        
        all_results.sort(key=lambda x: x['distance'])
        logger.info(f"✅ Retrieved {len(all_results)} documents")
        return all_results[:k]
    
    def chat(self, query: str, conversation_id: str = None) -> dict:
        """Enhanced chat with greeting detection and data extraction"""
        try:
            logger.info(f"Processing query: {query}")
            
            # STEP 1: Detect greetings
            query_lower = query.lower().strip()
            greeting_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'sup', 'yo', 'hii', 'hiii']
            intro_patterns = ['my name is', 'i am', "i'm", 'this is', 'im', 'i m']
            
            is_greeting = any(query_lower.startswith(word) for word in greeting_words)
            is_intro = any(pattern in query_lower for pattern in intro_patterns)
            
            property_keywords = ['property', 'properties', 'home', 'house', 'apartment', 'condo', 'bedroom', 'bathroom', 
                               'rent', 'rental', 'lease', 'buy', 'purchase', 'price', 'neighborhood', 'area', 'location',
                               'show', 'find', 'search', 'looking']
            has_property_intent = any(keyword in query_lower for keyword in property_keywords)
            
            # Greeting response
            if (is_greeting or is_intro) and not has_property_intent and len(query.split()) < 20:
                name = None
                for pattern in intro_patterns:
                    if pattern in query_lower:
                        parts = query_lower.split(pattern)
                        if len(parts) > 1:
                            name_part = parts[1].strip()
                            name_part = re.sub(r'[^\w\s]', '', name_part)
                            name = name_part.split()[0] if name_part else None
                            if name:
                                name = name.capitalize()
                            break
                
                if name:
                    greeting_response = f"Hi {name}! 👋 How can I help you today?"
                else:
                    greeting_response = "Hi there! 👋 How can I help you today?"
                
                logger.info(f"✅ Greeting detected")
                
                return {
                    "answer": greeting_response,
                    "sources": [],
                    "documents_retrieved": 0
                }
            
            # STEP 2: Search for properties
            logger.info("🔍 Property question detected")
            
            all_results = []
            for collection in self.collection_names[:5]:
                try:
                    results = self.retrieve_documents(query, collection, k=3)
                    all_results.extend(results)
                except Exception as e:
                    logger.warning(f"Failed to search {collection}: {e}")
                    continue
            
            all_results.sort(key=lambda x: x['distance'])
            top_results = all_results[:10]
            
            # STEP 3: Parse property data from CSV format
            parsed_properties = []
            for doc in top_results:
                raw_text = doc['document']
                
                # Extract fields from CSV-like string
                price_match = re.search(r'property\.price\.value,(\d+\.?\d*)', raw_text)
                bedrooms_match = re.search(r'property\.bedrooms,(\d+\.?\d*)', raw_text)
                bathrooms_match = re.search(r'property\.bathrooms,(\d+\.?\d*)', raw_text)
                address_match = re.search(r'property\.address\.streetAddress,([^,]+)', raw_text)
                city_match = re.search(r'property\.address\.city,([^,]+)', raw_text)
                sqft_match = re.search(r'property\.livingArea,(\d+\.?\d*)', raw_text)
                
                parsed_prop = {
                    'raw': raw_text[:500],
                    'price': float(price_match.group(1)) if price_match else None,
                    'bedrooms': int(float(bedrooms_match.group(1))) if bedrooms_match else None,
                    'bathrooms': float(bathrooms_match.group(1)) if bathrooms_match else None,
                    'address': address_match.group(1).strip() if address_match else 'Address not available',
                    'city': city_match.group(1).strip() if city_match else '',
                    'sqft': int(float(sqft_match.group(1))) if sqft_match else None,
                    'collection': doc['collection']
                }
                parsed_properties.append(parsed_prop)
            
            # Build structured context for OpenAI
            context_parts = []
            for i, prop in enumerate(parsed_properties[:5]):
                prop_text = f"Property {i+1}:\n"
                prop_text += f"- Address: {prop['address']}, {prop['city']}\n"
                if prop['price']:
                    prop_text += f"- Price: ${prop['price']:,.0f}\n"
                if prop['bedrooms']:
                    prop_text += f"- Bedrooms: {prop['bedrooms']}\n"
                if prop['bathrooms']:
                    prop_text += f"- Bathrooms: {prop['bathrooms']}\n"
                if prop['sqft']:
                    prop_text += f"- Square Feet: {prop['sqft']:,}\n"
                context_parts.append(prop_text)
            
            context = "\n\n".join(context_parts)
            
            # Enhanced system prompt
            system_prompt = """You are PropBot, a friendly Boston real estate AI assistant.

The property data is already parsed and formatted for you with exact prices and features.

When showing properties:
- Display the EXACT price as given (already in dollars)
- Show bedrooms, bathrooms, and square footage
- Format nicely with bullet points
- Highlight the best value option
- Be enthusiastic about great deals
- Keep responses concise (2-4 paragraphs)"""

            if len(parsed_properties) > 0:
                user_message = f"""User Query: {query}

Properties Found:
{context}

Provide a helpful, well-formatted response with these specific properties."""
            else:
                user_message = f"""User Query: {query}

No properties found. Suggest they try different criteria."""
            
            # Get OpenAI response
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            sources = [
                {
                    "collection": doc['collection'],
                    "relevance": round(1 - doc['distance'], 3),
                    "snippet": doc['document'][:800]
                }
                for doc in top_results[:5]
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "documents_retrieved": len(top_results)
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "answer": "I apologize, but I encountered an error. Please try rephrasing your question! 🏠",
                "sources": [],
                "documents_retrieved": 0
            }

def test_rag():
    """Test RAG"""
    logger.info("🧪 Testing RAG...")
    rag = PropBotRAG()
    result = rag.chat("Show me properties in Back Bay")
    print(result['answer'])

if __name__ == "__main__":
    test_rag()
