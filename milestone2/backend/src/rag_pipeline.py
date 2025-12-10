"""
COMPLETE Enhanced RAG Pipeline - Multi-Collection Smart Search
"""

import os
import chromadb 
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import logging
from typing import List, Dict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class PropBotRAG:
    """Enhanced RAG with multi-collection search and conversation memory"""
    
    def __init__(self):
        logger.info("🔧 Initializing Enhanced RAG Pipeline...")
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")        
        try:
            collections = self.chroma_client.list_collections()
            self.collection_names = [c.name for c in collections]
            self.collection = self.chroma_client.get_collection("properties")
            logger.info(f"✅ Found {len(self.collection_names)} collections")
        except Exception as e:
            logger.error(f"❌ Failed to load collections: {e}")
            self.collection_names = []
        
        self.conversation_memory = {}
    
    def parse_property_document(self, doc_text: str) -> dict:
        """Parse: '104 PUTNAM ST, Boston, MA 02128. THREE-FAM DWELLING. 6. 3. 719,400'"""
        try:
            parts = doc_text.split('.')
            
            if len(parts) >= 5:
                address = parts[0].strip()
                prop_type = parts[1].strip()
                beds = int(parts[2].strip()) if parts[2].strip().isdigit() else None
                baths = int(parts[3].strip()) if parts[3].strip().isdigit() else None
                price_str = parts[4].strip().replace(',', '')
                price = float(price_str) if price_str.replace('.', '').isdigit() else None
                
                return {
                    'address': address,
                    'type': prop_type,
                    'beds': beds,
                    'baths': baths,
                    'price': price
                }
        except:
            pass
        
        return {'address': None, 'type': None, 'beds': None, 'baths': None, 'price': None}
    
    def get_relevant_collections(self, query: str) -> List[str]:
        """Select collections based on query intent"""
        query_lower = query.lower()
        collections = []
        
        # Crime queries
        if any(w in query_lower for w in ['crime', 'safety', 'safe', 'dangerous']):
            collections.extend(['crime', 'boston_crime'])
        
        # Neighborhood queries
        if any(w in query_lower for w in ['neighborhood', 'area', 'community', 'best place']):
            collections.append('neighborhoods')
        
        # School queries
        if any(w in query_lower for w in ['school', 'education']):
            collections.append('schools')
        
        # Amenity queries  
        if any(w in query_lower for w in ['restaurant', 'shop', 'park', 'gym', 'cafe']):
            collections.extend(['amenities', 'yelp_businesses_20251024_185237', 'parks'])
        
        # Transit queries
        if any(w in query_lower for w in ['transit', 'subway', 'train', 'bus', 'mbta']):
            collections.append('transit')
        
        # Property queries - use ALL property collections for best coverage
        if any(w in query_lower for w in ['property', 'home', 'house', 'condo', 'rent', 'buy', 'bedroom', 'price']):
            collections.extend([
                'properties',
                'boston_properties',
                'zillow_working_boston_all_max_20251127_181854',
                'zillow_working_boston_listings_20251127_174724_flat'
            ])
        
        # Default to property collections if nothing matches
        if not collections:
            collections = ['properties', 'boston_properties']
        
        # Remove duplicates, keep only existing collections
        return [c for c in dict.fromkeys(collections) if c in self.collection_names][:6]
    
    def retrieve_documents(self, query: str, collection_name: str = None, k: int = 5) -> List[Dict]:
        """Retrieve from ChromaDB"""
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
                            'id': results['ids'][0][idx] if results['ids'] else f"doc_{idx}",
                            'metadata': results['metadatas'][0][idx] if results['metadatas'] else {},
                            'distance': results['distances'][0][idx] if results['distances'] else 0
                        })
            except Exception as e:
                logger.warning(f"⚠️  Failed {coll_name}: {e}")
        
        all_results.sort(key=lambda x: x['distance'])
        return all_results[:k]
    
    def chat(self, query: str, conversation_id: str = "default", user_id: int = None) -> dict:
        """Enhanced conversational chat"""
        try:
            logger.info(f"💬 Query: {query}")
            
            if conversation_id not in self.conversation_memory:
                self.conversation_memory[conversation_id] = []
            
            conv_history = self.conversation_memory[conversation_id]
            query_lower = query.lower().strip()
            
            # ✅ GREETING DETECTION
            greetings = ['hi', 'hello', 'hey', 'hii', 'hiii', 'sup', 'yo']
            intro_patterns = ['my name is', 'i am', "i'm", 'im', 'i m']
            
            is_greeting = any(query_lower.startswith(g) for g in greetings) and len(query.split()) <= 5
            is_intro = any(p in query_lower for p in intro_patterns) and len(query.split()) <= 8
            
            has_property_keywords = any(w in query_lower for w in 
                ['property', 'home', 'house', 'bedroom', 'rent', 'buy', 'show', 'find', 'price'])
            
            if (is_greeting or is_intro) and not has_property_keywords:
                name = None
                for pattern in intro_patterns:
                    if pattern in query_lower:
                        parts = query_lower.split(pattern)
                        if len(parts) > 1:
                            name_part = re.sub(r'[^\w\s]', '', parts[1].strip())
                            name = name_part.split()[0].capitalize() if name_part else None
                            break
                
                response = f"Hi {name}! 👋 Great to meet you! I'm PropBot. I can help you find homes, answer neighborhood questions, check crime rates, and more!" if name else "Hi there! 👋 I'm PropBot, your Boston real estate assistant. How can I help you today?"
                
                conv_history.append({"role": "user", "content": query})
                conv_history.append({"role": "assistant", "content": response})
                
                return {"answer": response, "sources": [], "documents_retrieved": 0}
            
            # ✅ MULTI-COLLECTION SEARCH
            relevant_collections = self.get_relevant_collections(query)
            logger.info(f"🔍 Searching: {relevant_collections}")
            
            all_results = []
            for coll in relevant_collections:
                try:
                    results = self.retrieve_documents(query, coll, k=3)
                    all_results.extend(results)
                except Exception as e:
                    logger.warning(f"Search failed for {coll}: {e}")
            
            all_results.sort(key=lambda x: x['distance'])
            top_results = all_results[:10]
            
            # ✅ PARSE PROPERTIES
            parsed_props = []
            for doc in top_results:
                parsed = self.parse_property_document(doc['document'])
                if parsed['address'] or parsed['price']:
                    parsed['collection'] = doc['collection']
                    parsed['distance'] = doc['distance']
                    parsed_props.append(parsed)
            
            # ✅ BUILD CONTEXT
            context_parts = []
            
            # Add conversation history
            if len(conv_history) > 0:
                recent = conv_history[-6:]
                context_parts.append("Previous conversation:")
                for msg in recent:
                    context_parts.append(f"{msg['role']}: {msg['content'][:80]}...")
            
            # Add current query
            context_parts.append(f"\nCurrent question: {query}")
            
            # Add property data
            if parsed_props:
                context_parts.append("\nRelevant Data Found:")
                for i, prop in enumerate(parsed_props[:5]):
                    prop_info = f"\n{i+1}. "
                    if prop['address']:
                        prop_info += f"{prop['address']}"
                    if prop['price']:
                        prop_info += f" - ${prop['price']:,.0f}"
                    if prop['beds']:
                        prop_info += f" - {prop['beds']}BR/{prop['baths']}BA"
                    if prop['type']:
                        prop_info += f" ({prop['type']})"
                    context_parts.append(prop_info)
            else:
                # Include raw documents for non-property queries (crime, schools, etc.)
                context_parts.append("\nRelevant Information:")
                for i, doc in enumerate(top_results[:3]):
                    context_parts.append(f"\n{i+1}. {doc['document'][:200]}...")
            
            full_context = "\n".join(context_parts)
            
            # ✅ SMART SYSTEM PROMPT
            system_prompt = """You are PropBot, a warm, intelligent Boston real estate assistant.

CRITICAL INTERACTION RULES:

1. ALWAYS ASK BUY OR RENT FIRST (if not mentioned):
   - If user doesn't specify "rent" or "buy" → Ask: "Are you looking to rent or buy? 🏠"
   - Don't show properties until you know this!

2. BE CONTEXTUALLY SMART:
   Examples:
   • "Just moved from NYC" → "Welcome to Boston! 🎉 Congrats on your move!"
   • "Office in downtown" → "Great! I'll prioritize easy commutes to downtown 🚇"
   • "New to Boston" → Be extra helpful, explain neighborhoods
   • "Family/kids" → Ask about schools and safety
   • "Student" → Ask about university proximity
   • "Budget conscious" → Be empathetic, show value options

3. ASK QUESTIONS PROGRESSIVELY (one at a time):
   Don't ask: "What's your budget, bedrooms, and neighborhood?"
   Instead:
   Turn 1: "Are you looking to rent or buy?"
   Turn 2: "What's your monthly budget?"
   Turn 3: "How many bedrooms?"
   Turn 4: NOW show properties!

4. EXAMPLE INTERACTION:
   User: "I just moved to Boston from NYC for full time job, office is downtown, looking for places to rent"
   
   YOU: "Welcome to Boston, Pranav! 🎉 Exciting move from NYC!
   
   Since you're renting with an office downtown, I'll help you find places with easy commutes. Quick questions:
   
   1️⃣ What's your monthly rent budget?
   2️⃣ How many bedrooms do you need?
   
   Once I know this, I'll show you the best options with short commutes to downtown! 🚇"

5. WHEN SHOWING PROPERTIES:
   - Show ADDRESS and PRICE clearly
   - NO match scores, NO confidence percentages
   - Explain WHY each property fits their needs
   - Use emojis naturally (not excessively)

6. BE CONVERSATIONAL:
   - Use "you" and "your"
   - Show enthusiasm with emojis
   - Reference what they told you earlier
   - Feel like talking to a knowledgeable friend

Remember: You're helpful and human-like, not robotic!"""            
            # ✅ GET RESPONSE
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_context}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            answer = response.choices[0].message.content
            
            # ✅ SAVE TO MEMORY
            conv_history.append({"role": "user", "content": query})
            conv_history.append({"role": "assistant", "content": answer})
            
            if len(conv_history) > 20:
                self.conversation_memory[conversation_id] = conv_history[-20:]
            
            # ✅ BUILD SOURCES
            sources = []
            for doc in top_results[:5]:
                relevance = max(0, (1 - doc['distance']) * 100)
                sources.append({
                    "collection": doc['collection'],
                    "relevance": round(relevance, 1),
                    "snippet": doc['document'][:150]
                })
            
            logger.info(f"✅ Response with {len(sources)} sources")
            
            return {
                "answer": answer,
                "sources": sources,
                "documents_retrieved": len(top_results)
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "answer": "I apologize, I encountered an error. Please try rephrasing! 🏠",
                "sources": [],
                "documents_retrieved": 0
            }
    
    def clear_conversation(self, conversation_id: str = "default"):
        """Clear conversation memory"""
        if conversation_id in self.conversation_memory:
            del self.conversation_memory[conversation_id]


if __name__ == "__main__":
    rag = PropBotRAG()
    
    # Test greeting
    r1 = rag.chat("hi i'm pranav", "test")
    print("Greeting:", r1['answer'], "\n")
    
    # Test property search
    r2 = rag.chat("show me properties in roxbury", "test")
    print("Properties:", r2['answer'], "\n")
    
    # Test follow-up
    r3 = rag.chat("what are the prices?", "test")
    print("Follow-up:", r3['answer'])
