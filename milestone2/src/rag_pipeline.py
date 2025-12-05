"""
Enhanced RAG Pipeline - Interactive & User-Friendly
Features: Conversation Memory, Follow-ups, Personality
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional
from pyspellchecker import SpellChecker
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
        
        self.chroma_client = chromadb.HttpClient(
            host='localhost',
            port=8000
        )
        logger.info("✅ Connected to ChromaDB")
        
        self.spell = SpellChecker()
        self.spell.word_frequency.load_words([
            'back', 'bay', 'beacon', 'hill', 'south', 'end', 'dorchester',
            'roxbury', 'jamaica', 'plain', 'charlestown', 'allston', 'brighton',
            'fenway', 'seaport', 'bedroom', 'bathroom', 'condo', 'townhouse'
        ])
        
        try:
            collections = self.chroma_client.list_collections()
            self.collection_names = [c.name for c in collections]
            logger.info(f"✅ Found {len(self.collection_names)} collections")
        except Exception as e:
            logger.error(f"❌ Failed to load collections: {e}")
            self.collection_names = []
        
        self.top_k = 5
        self.temperature = 0.7
        
        self.boston_neighborhoods = [
            'back bay', 'beacon hill', 'south end', 'north end', 'dorchester',
            'roxbury', 'jamaica plain', 'charlestown', 'east boston', 'allston',
            'brighton', 'fenway', 'south boston', 'seaport', 'west end'
        ]
        
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
        """
        Enhanced chat with greeting detection and OpenAI responses
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # STEP 1: Detect greetings and introductions
            query_lower = query.lower().strip()
            greeting_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'sup', 'yo', 'hii', 'hiii']
            intro_patterns = ['my name is', 'i am', "i'm", 'this is', 'im', 'i m']
            
            is_greeting = any(query_lower.startswith(word) for word in greeting_words)
            is_intro = any(pattern in query_lower for pattern in intro_patterns)
            
            # Check if it's ONLY a greeting (not a property question)
            property_keywords = ['property', 'properties', 'home', 'house', 'apartment', 'condo', 'bedroom', 'bathroom', 
                               'rent', 'rental', 'lease', 'buy', 'purchase', 'price', 'neighborhood', 'area', 'location',
                               'show', 'find', 'search', 'looking']
            has_property_intent = any(keyword in query_lower for keyword in property_keywords)
            
            # If it's just a greeting/intro without property questions
            if (is_greeting or is_intro) and not has_property_intent and len(query.split()) < 20:
                # Extract name if provided
                name = None
                for pattern in intro_patterns:
                    if pattern in query_lower:
                        parts = query_lower.split(pattern)
                        if len(parts) > 1:
                            name_part = parts[1].strip()
                            # Remove punctuation and get first word
                            name_part = re.sub(r'[^\w\s]', '', name_part)
                            name = name_part.split()[0] if name_part else None
                            if name:
                                name = name.capitalize()
                            break
                
                # Simple, friendly greeting response
                if name:
                    greeting_response = f"Hi {name}! 👋 How can I help you today?"
                else:
                    greeting_response = "Hi there! 👋 How can I help you today?"
                
                logger.info(f"✅ Greeting detected, responding without property search")
                
                return {
                    "answer": greeting_response,
                    "sources": [],
                    "documents_retrieved": 0
                }
            
            # STEP 2: If not just a greeting, search for properties
            logger.info("🔍 Property question detected, searching ChromaDB...")
            
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
            
            # Build context
            context = "\n\n".join([
                f"Source {i+1} ({doc['collection']}):\n{doc['document'][:500]}"
                for i, doc in enumerate(top_results)
            ])
            
            # System prompt for property questions
            system_prompt = """You are PropBot, a friendly Boston real estate AI assistant.

When answering property questions:
- Be specific with addresses, prices, and features
- Use emojis sparingly (1-2 per response)
- Format property details clearly with bullet points
- Highlight the best option
- Keep responses concise (2-3 paragraphs)
- Suggest relevant follow-up actions"""

            if len(top_results) > 0:
                user_message = f"""User Query: {query}

Boston Real Estate Data:
{context}

Provide a helpful response with specific property recommendations."""
            else:
                user_message = f"""User Query: {query}

No property data found. Politely suggest they rephrase or try different criteria."""
            
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
                    "snippet": doc['document'][:200] + "..."
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
    """Test enhanced RAG"""
    logger.info("🧪 Testing Enhanced RAG...")
    
    rag = PropBotRAG()
    
    test_queries = [
        "Hi I am Pranav",
        "Show me 3 bedroom properties in Back Bay",
        "Tell me about rentals under $3000"
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"💬 Query: {query}")
        print('='*70)
        
        result = rag.chat(query)
        print(f"\n{result['answer']}\n")

if __name__ == "__main__":
    test_rag()
