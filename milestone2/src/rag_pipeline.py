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
        
        self.chroma_client = chromadb.HttpClient(
            host=os.getenv('CHROMADB_HOST', 'localhost'),
            port=int(os.getenv('CHROMADB_PORT', '8000'))
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
        
        # FEATURE 1: Conversation memory
        self.conversation_context = {}
    
    def correct_spelling(self, text: str) -> str:
        """Auto-correct spelling mistakes"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            if not word.isalpha():
                corrected_words.append(word)
                continue
            
            lower_word = word.lower()
            
            if any(hood in lower_word for hood in self.boston_neighborhoods):
                corrected_words.append(word)
                continue
            
            correction = self.spell.correction(lower_word)
            if correction and correction != lower_word:
                logger.info(f"📝 Corrected: '{word}' → '{correction}'")
                corrected_words.append(correction)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def extract_intent(self, query: str, conversation_id: str = None) -> Dict:
        """Extract user intent with conversation context"""
        query_lower = query.lower()
        
        intent = {
            'type': 'general',
            'action': None,
            'filters': {},
            'context_used': False
        }
        
        # Check conversation context for missing info
        if conversation_id and conversation_id in self.conversation_context:
            context = self.conversation_context[conversation_id]
            
            # If user says "cheaper" or "more affordable", use previous filters
            if any(word in query_lower for word in ['cheaper', 'affordable', 'less expensive', 'lower price']):
                if 'last_filters' in context:
                    intent['filters'] = context['last_filters'].copy()
                    if 'max_price' in intent['filters']:
                        intent['filters']['max_price'] *= 0.8  # Reduce by 20%
                    intent['context_used'] = True
                    logger.info("🧠 Using conversation context for 'cheaper'")
            
            # If user says "similar", use previous neighborhood
            if any(word in query_lower for word in ['similar', 'like that', 'same area']):
                if 'last_neighborhood' in context:
                    intent['filters']['neighborhood'] = context['last_neighborhood']
                    intent['context_used'] = True
                    logger.info("🧠 Using conversation context for 'similar'")
        
        # Detect rental vs buy
        if any(word in query_lower for word in ['rent', 'rental', 'lease', 'apartment']):
            intent['type'] = 'rental'
            intent['action'] = 'search_rentals'
        elif any(word in query_lower for word in ['buy', 'purchase', 'sale', 'for sale']):
            intent['type'] = 'buy'
            intent['action'] = 'search_sales'
        
        # Detect comparison
        if any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            intent['type'] = 'compare'
            intent['action'] = 'compare_properties'
        
        # Extract bedrooms
        bedroom_match = re.search(r'(\d+)\s*(br|bed|bedroom)', query_lower)
        if bedroom_match:
            intent['filters']['bedrooms'] = int(bedroom_match.group(1))
        
        # Extract price
        price_match = re.search(r'\$?(\d+)k', query_lower)
        if price_match:
            intent['filters']['max_price'] = int(price_match.group(1)) * 1000
        
        # Extract neighborhood
        for neighborhood in self.boston_neighborhoods:
            if neighborhood in query_lower:
                intent['filters']['neighborhood'] = neighborhood.title()
                break
        
        logger.info(f"🎯 Intent: {intent}")
        return intent
    
    def update_conversation_context(self, conversation_id: str, intent: Dict, query: str):
        """Update conversation memory"""
        if not conversation_id:
            return
        
        if conversation_id not in self.conversation_context:
            self.conversation_context[conversation_id] = {
                'queries': [],
                'last_filters': {},
                'last_neighborhood': None,
                'search_count': 0
            }
        
        context = self.conversation_context[conversation_id]
        context['queries'].append(query)
        context['search_count'] += 1
        
        if intent['filters']:
            context['last_filters'] = intent['filters']
            if 'neighborhood' in intent['filters']:
                context['last_neighborhood'] = intent['filters']['neighborhood']
    
    def generate_follow_up_suggestions(self, intent: Dict, documents: List[Dict]) -> str:
        """Generate helpful follow-up suggestions"""
        suggestions = []
        
        if documents:
            suggestions.append("💡 What would you like to do next?\n")
            
            if intent['filters'].get('neighborhood'):
                suggestions.append("   • Calculate commute times to downtown")
                suggestions.append("   • See crime rates for this area")
            
            suggestions.append("   • Compare these properties side-by-side")
            suggestions.append("   • Get mortgage payment estimates")
            suggestions.append("   • Save properties to favorites")
            
            if intent['type'] == 'rental':
                suggestions.append("   • See similar properties to buy instead")
            else:
                suggestions.append("   • Check rental prices in this area")
        
        return "\n".join(suggestions)
    
    def validate_query(self, query: str) -> Dict:
        """Validate query with friendly responses"""
        if not query or len(query.strip()) < 3:
            return {
                'valid': False,
                'message': "I'm here to help! 🏠 Try asking me something like:\n• 'Show me 3 bedroom properties in Back Bay'\n• 'What are rentals under $3000?'\n• 'Compare Beacon Hill vs South End'"
            }
        
        vague_queries = ['hi', 'hello', 'hey', 'help', 'what', 'huh', 'ok', 'yes', 'no']
        if query.lower().strip() in vague_queries:
            return {
                'valid': False,
                'message': "Hi there! 👋 I'm PropBot, your Boston real estate expert!\n\nI can help you:\n• Find properties to buy or rent\n• Compare neighborhoods\n• Predict prices\n• Calculate commute times\n\nWhat would you like to know about Boston real estate?"
            }
        
        return {'valid': True}
    
    def retrieve_documents(self, query: str, collection_name: str = None) -> List[Dict]:
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
                    n_results=self.top_k
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
        return all_results[:self.top_k]
    
    def generate_response_with_gpt(self, query: str, documents: List[Dict], intent: Dict, conversation_id: str = None) -> str:
        """Generate friendly, specific response with GPT"""
        
        if not documents:
            if intent['type'] == 'rental':
                return """I couldn't find rentals matching your criteria right now. 😊

Let me help you search better:
- Try adjusting your budget (most Boston rentals are $2,000-$4,000/month)
- Consider different neighborhoods (Allston and Brighton are more affordable!)
- Change bedroom requirements

Or ask: "What's the average rent in Boston?" """
            else:
                return """I couldn't find properties matching those exact criteria. 🏠

Here's what you can try:
- Explore different neighborhoods (I know all of Boston!)
- Adjust your price range
- Try different bedroom/bathroom combinations

Ask me: "What neighborhoods are available?" or "Show me all 3 bedroom properties" """
        
        context = "\n\n".join([f"Property {i+1}: {doc['document']}" for i, doc in enumerate(documents)])
        
        # Context-aware system prompt
        context_note = ""
        if conversation_id and conversation_id in self.conversation_context:
            ctx = self.conversation_context[conversation_id]
            if ctx['search_count'] > 1:
                context_note = f"\n\nNOTE: This is the user's {ctx['search_count']} search. Reference previous searches naturally if relevant."
        
        system_prompt = f"""You are PropBot, a friendly and knowledgeable Boston real estate expert! 🏠

YOUR PERSONALITY:
- Warm, enthusiastic, and helpful
- Use emojis sparingly (1-2 per response)
- Be conversational and natural
- Show excitement about great properties
- Empathetic when properties are out of budget

YOUR RESPONSE STYLE:
1. Start with a friendly acknowledgment
2. Give SPECIFIC details (addresses, exact prices, features)
3. Use bullet points for multiple properties
4. Compare properties when showing multiple
5. Highlight the BEST option
6. End with a helpful suggestion or question

FORMATTING:
- Use line breaks for readability
- Bold important numbers (in markdown)
- Keep responses concise but complete (300-400 words max)
{context_note}"""

        user_prompt = f"""User Question: {query}

Boston Real Estate Data:
{context}

Provide a helpful, well-formatted response."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=600
            )
            
            answer = response.choices[0].message.content
            logger.info("✅ Generated friendly GPT response")
            return answer
            
        except Exception as e:
            logger.error(f"❌ OpenAI error: {e}")
            return f"I found {len(documents)} great options! Here's the first:\n\n{documents[0]['document'][:300]}..."
    
    def chat(self, query: str, conversation_id: Optional[str] = None) -> Dict:
        """Main chat with memory and personality"""
        logger.info(f"💬 Query: {query}")
        
        # Validate
        validation = self.validate_query(query)
        if not validation['valid']:
            return {
                'answer': validation['message'],
                'sources': [],
                'documents_retrieved': 0,
                'follow_up_suggestions': []
            }
        
        # Correct spelling
        corrected_query = self.correct_spelling(query)
        if corrected_query != query:
            logger.info(f"📝 Corrected: {query} → {corrected_query}")
        
        # Extract intent (with conversation memory)
        intent = self.extract_intent(corrected_query, conversation_id)
        
        # Update conversation context
        self.update_conversation_context(conversation_id, intent, query)
        
        # Retrieve documents
        documents = self.retrieve_documents(corrected_query)
        
        # Generate response
        answer = self.generate_response_with_gpt(corrected_query, documents, intent, conversation_id)
        
        # Generate follow-up suggestions
        follow_ups = self.generate_follow_up_suggestions(intent, documents)
        
        # Add follow-ups to answer
        if follow_ups:
            answer = f"{answer}\n\n{follow_ups}"
        
        # Format sources
        sources = [
            {
                'collection': doc['collection'],
                'relevance': round(1 - doc['distance'], 3),
                'snippet': doc['document'][:200] + "..."
            }
            for doc in documents
        ]
        
        return {
            'answer': answer,
            'sources': sources,
            'documents_retrieved': len(documents),
            'corrected_query': corrected_query if corrected_query != query else None,
            'intent_detected': intent['type'],
            'context_used': intent.get('context_used', False)
        }

def test_rag():
    """Test enhanced RAG"""
    logger.info("🧪 Testing Enhanced RAG...")
    
    rag = PropBotRAG()
    conv_id = "test_conv_123"
    
    test_queries = [
        "Show me 3 bedroom properties in Back Bay",
        "What about cheaper options?",  # Uses context!
        "Tell me about rentals under $3000"
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"💬 Query: {query}")
        print('='*70)
        
        result = rag.chat(query, conversation_id=conv_id)
        
        if result.get('corrected_query'):
            print(f"✏️  Corrected to: {result['corrected_query']}")
        
        if result.get('context_used'):
            print(f"🧠 Used conversation memory!")
        
        print(f"\n{result['answer']}\n")

if __name__ == "__main__":
    test_rag()
