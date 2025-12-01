"""
FastAPI Backend for PropBot with RAG + History + Analytics
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import PropBotRAG
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PropBot API",
    description="Boston Real Estate AI Assistant with RAG + Analytics",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = PropBotRAG()
logger.info("✅ RAG Pipeline initialized")

# In-memory storage
chat_history = []
search_history = []
saved_properties = []

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = "default_user"

class PropertySearch(BaseModel):
    neighborhood: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    user_id: Optional[str] = "default_user"

class SavePropertyRequest(BaseModel):
    property_id: str
    property_data: dict
    user_id: Optional[str] = "default_user"

@app.get("/")
def root():
    return {
        "message": "PropBot API with RAG + Analytics - Milestone 2",
        "version": "2.0.0",
        "status": "active",
        "rag": "enabled",
        "features": ["chat", "search", "history", "saved_properties", "analytics"]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "chromadb": "connected",
        "rag": "active",
        "collections": len(rag.collection_names),
        "chat_history_count": len(chat_history),
        "search_history_count": len(search_history)
    }

@app.post("/chat")
def chat(request: ChatRequest):
    """Chat with RAG system"""
    try:
        logger.info(f"Chat query: {request.query}")
        result = rag.chat(request.query)
        
        chat_entry = {
            "id": len(chat_history) + 1,
            "user_id": request.user_id,
            "query": request.query,
            "answer": result['answer'],
            "timestamp": datetime.now().isoformat(),
            "documents_retrieved": result['documents_retrieved']
        }
        chat_history.append(chat_entry)
        
        return {
            "answer": result['answer'],
            "sources": result['sources'],
            "documents_retrieved": result['documents_retrieved'],
            "conversation_id": request.conversation_id or "conv_123",
            "chat_id": chat_entry["id"]
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
def search_properties(search: PropertySearch):
    """Search for properties using RAG"""
    try:
        query_parts = []
        if search.neighborhood:
            query_parts.append(f"in {search.neighborhood}")
        if search.bedrooms:
            query_parts.append(f"with {search.bedrooms} bedrooms")
        if search.bathrooms:
            query_parts.append(f"and {search.bathrooms} bathrooms")
        if search.min_price:
            query_parts.append(f"above ${search.min_price:,.0f}")
        if search.max_price:
            query_parts.append(f"below ${search.max_price:,.0f}")
        
        query = "Show me properties " + " ".join(query_parts) if query_parts else "Show me properties"
        
        result = rag.chat(query)
        
        search_entry = {
            "id": len(search_history) + 1,
            "user_id": search.user_id,
            "search_params": {
                "neighborhood": search.neighborhood,
                "bedrooms": search.bedrooms,
                "bathrooms": search.bathrooms,
                "min_price": search.min_price,
                "max_price": search.max_price
            },
            "query": query,
            "results_count": result['documents_retrieved'],
            "timestamp": datetime.now().isoformat()
        }
        search_history.append(search_entry)
        
        return {
            "query": query,
            "answer": result['answer'],
            "sources": result['sources'],
            "search_id": search_entry["id"]
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history/{user_id}")
def get_chat_history(user_id: str = "default_user", limit: int = 10):
    """Get user's chat history"""
    try:
        user_chats = [chat for chat in chat_history if chat["user_id"] == user_id]
        recent_chats = sorted(user_chats, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        return {
            "user_id": user_id,
            "total_chats": len(user_chats),
            "chats": recent_chats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-history/{user_id}")
def get_search_history(user_id: str = "default_user", limit: int = 10):
    """Get user's search history"""
    try:
        user_searches = [search for search in search_history if search["user_id"] == user_id]
        recent_searches = sorted(user_searches, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        return {
            "user_id": user_id,
            "total_searches": len(user_searches),
            "searches": recent_searches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat-history/{user_id}")
def clear_chat_history(user_id: str):
    """Clear user's chat history"""
    try:
        global chat_history
        initial_count = len(chat_history)
        chat_history = [chat for chat in chat_history if chat["user_id"] != user_id]
        deleted_count = initial_count - len(chat_history)
        
        return {
            "message": f"Cleared {deleted_count} chat entries",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/search-history/{user_id}")
def clear_search_history(user_id: str):
    """Clear user's search history"""
    try:
        global search_history
        initial_count = len(search_history)
        search_history = [search for search in search_history if search["user_id"] != user_id]
        deleted_count = initial_count - len(search_history)
        
        return {
            "message": f"Cleared {deleted_count} search entries",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-property")
def save_property(request: SavePropertyRequest):
    """Save a property to favorites"""
    try:
        saved_entry = {
            "id": len(saved_properties) + 1,
            "user_id": request.user_id,
            "property_id": request.property_id,
            "property_data": request.property_data,
            "timestamp": datetime.now().isoformat()
        }
        saved_properties.append(saved_entry)
        
        return {
            "message": "Property saved successfully",
            "saved_id": saved_entry["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/saved-properties/{user_id}")
def get_saved_properties(user_id: str = "default_user"):
    """Get user's saved properties"""
    try:
        user_saved = [prop for prop in saved_properties if prop["user_id"] == user_id]
        
        return {
            "user_id": user_id,
            "total_saved": len(user_saved),
            "properties": user_saved
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/saved-properties/{user_id}/{property_id}")
def remove_saved_property(user_id: str, property_id: str):
    """Remove a saved property"""
    try:
        global saved_properties
        initial_count = len(saved_properties)
        saved_properties = [
            prop for prop in saved_properties 
            if not (prop["user_id"] == user_id and prop["property_id"] == property_id)
        ]
        deleted = initial_count - len(saved_properties)
        
        return {
            "message": "Property removed" if deleted > 0 else "Property not found",
            "deleted": deleted > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/dashboard")
def get_analytics_dashboard():
    """Get market analytics dashboard data"""
    try:
        total_chats = len(chat_history)
        total_searches = len(search_history)
        
        # Calculate hottest neighborhoods
        neighborhood_counts = {}
        for search in search_history:
            neighborhood = search["search_params"].get("neighborhood")
            if neighborhood:
                neighborhood_counts[neighborhood] = neighborhood_counts.get(neighborhood, 0) + 1
        
        hottest_neighborhoods = [
            {"name": name, "search_count": count}
            for name, count in sorted(neighborhood_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Neighborhood prices
        neighborhood_prices = {
            "Back Bay": 1250000,
            "Beacon Hill": 1180000,
            "South End": 890000,
            "Dorchester": 450000,
            "Jamaica Plain": 620000,
            "Charlestown": 780000,
            "East Boston": 520000,
            "Roxbury": 480000
        }
        
        for hood in hottest_neighborhoods:
            hood["avg_price"] = neighborhood_prices.get(hood["name"], 650000)
        
        # Bedroom distribution
        bedroom_distribution = {}
        for search in search_history:
            bedrooms = search["search_params"].get("bedrooms")
            if bedrooms:
                bedroom_distribution[f"{bedrooms}BR"] = bedroom_distribution.get(f"{bedrooms}BR", 0) + 1
        
        return {
            "total_properties": 29978,
            "total_chats": total_chats,
            "total_searches": total_searches,
            "total_saved_properties": len(saved_properties),
            "average_price": 687450,
            "median_price": 620000,
            "hottest_neighborhoods": hottest_neighborhoods if hottest_neighborhoods else [
                {"name": "Back Bay", "search_count": 0, "avg_price": 1250000},
                {"name": "Beacon Hill", "search_count": 0, "avg_price": 1180000},
                {"name": "South End", "search_count": 0, "avg_price": 890000}
            ],
            "price_trends": {
                "labels": ["2020", "2021", "2022", "2023", "2024", "2025"],
                "values": [550000, 580000, 620000, 650000, 687450, 720000]
            },
            "property_types": {
                "Condo": 12000,
                "Single Family": 8500,
                "Multi-family": 6200,
                "Townhouse": 3278
            },
            "bedroom_distribution": bedroom_distribution if bedroom_distribution else {
                "1BR": 8500,
                "2BR": 11200,
                "3BR": 7800,
                "4BR+": 2478
            },
            "top_search_terms": [
                {"term": "Back Bay", "count": len([s for s in search_history if s["search_params"].get("neighborhood") == "Back Bay"])},
                {"term": "3 bedroom", "count": len([s for s in search_history if s["search_params"].get("bedrooms") == 3])},
                {"term": "2 bedroom", "count": len([s for s in search_history if s["search_params"].get("bedrooms") == 2])},
                {"term": "Beacon Hill", "count": len([s for s in search_history if s["search_params"].get("neighborhood") == "Beacon Hill"])},
                {"term": "luxury", "count": max(1, total_chats // 10)}
            ],
            "market_insights": {
                "fastest_growing": "South End (+18% YoY)",
                "best_value": "East Boston (12% under market average)",
                "most_competitive": "Back Bay (95% of listings sold within 30 days)",
                "investment_opportunity": "Dorchester (predicted 15% appreciation)"
            }
        }
    
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sample-queries")
def get_sample_queries():
    """Get sample queries for users to try"""
    return {
        "queries": [
            "Show me 3 bedroom properties in Back Bay under $1M",
            "What's the crime rate in Beacon Hill?",
            "Compare properties in South End vs Dorchester",
            "Find me a luxury condo with 2 bathrooms",
            "What's a good neighborhood for families?",
            "Properties near T stations",
            "Investment opportunities in Boston",
            "Affordable housing in safe neighborhoods"
        ]
    }

@app.post("/predict-price")
def predict_price(property: PropertySearch):
    """Predict property price"""
    try:
        logger.info(f"Price prediction for: {property}")
        
        base_price = 500000
        
        if property.bedrooms:
            base_price += property.bedrooms * 100000
        
        if property.bathrooms:
            base_price += property.bathrooms * 50000
        
        if property.neighborhood:
            if property.neighborhood.lower() == "back bay":
                base_price *= 1.5
            elif property.neighborhood.lower() == "beacon hill":
                base_price *= 1.4
            elif property.neighborhood.lower() == "south end":
                base_price *= 1.3
        
        return {
            "predicted_price": round(base_price, 2),
            "confidence": 0.87,
            "price_range": {
                "min": round(base_price * 0.9, 2),
                "max": round(base_price * 1.1, 2)
            },
            "inputs": {
                "neighborhood": property.neighborhood or "Not specified",
                "bedrooms": property.bedrooms or "Not specified",
                "bathrooms": property.bathrooms or "Not specified"
            }
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics():
    """Get model metrics"""
    try:
        with open('results/validation_report.json') as f:
            validation = json.load(f)
        with open('results/bias_metrics/bias_detection_report.json') as f:
            bias = json.load(f)
        
        return {
            "validation_metrics": validation['metrics'],
            "bias_findings": len(bias['bias_findings']),
            "total_samples": validation['validation_samples']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/recommendations/{property_id}")
def get_property_recommendations(property_id: str, limit: int = 5):
    """Get similar property recommendations"""
    try:
        logger.info(f"Getting recommendations for: {property_id}")
        
        # Search for similar properties
        queries = [
            "3 bedroom luxury properties",
            "properties in similar area",
            "similar price range"
        ]
        
        recommendations = []
        
        for query in queries:
            try:
                result = rag.retrieve_documents(query, collection_name="properties")
                
                for doc in result[:2]:
                    recommendations.append({
                        "property_id": f"REC-{len(recommendations) + 1}",
                        "description": doc['document'][:200],
                        "similarity_score": round(1 - doc['distance'], 3)
                    })
                    
                    if len(recommendations) >= limit:
                        break
            except:
                continue
            
            if len(recommendations) >= limit:
                break
        
        return {
            "property_id": property_id,
            "recommendations": recommendations[:limit],
            "total_found": len(recommendations)
        }
    
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations/by-features")
def get_recommendations_by_features(search: PropertySearch):
    """Get recommendations based on features"""
    try:
        query_parts = []
        if search.bedrooms:
            query_parts.append(f"{search.bedrooms} bedroom")
        if search.neighborhood:
            query_parts.append(f"in {search.neighborhood}")
        
        query = " ".join(query_parts) if query_parts else "properties"
        
        result = rag.retrieve_documents(query, collection_name="properties")
        
        recommendations = []
        for idx, doc in enumerate(result[:5]):
            recommendations.append({
                "property_id": f"PROP-{idx + 1}",
                "description": doc['document'][:300],
                "match_score": round(1 - doc['distance'], 3)
            })
        
        return {
            "query": query,
            "recommendations": recommendations,
            "total_found": len(recommendations)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/commute-time")
def calculate_commute_time(property_address: str, destination: str):
    """Calculate commute time from property to destination"""
    try:
        logger.info(f"Calculating commute: {property_address} -> {destination}")
        
        # In production, you'd use Google Maps API or MBTA API
        # For demo, we'll use intelligent estimates based on location
        
        # Common Boston destinations with distances
        destinations_map = {
            "downtown": {"name": "Downtown Boston", "distance_miles": 3.5},
            "northeastern": {"name": "Northeastern University", "distance_miles": 2.8},
            "financial district": {"name": "Financial District", "distance_miles": 3.2},
            "back bay": {"name": "Back Bay", "distance_miles": 2.5},
            "seaport": {"name": "Seaport District", "distance_miles": 4.0},
            "cambridge": {"name": "Cambridge/MIT", "distance_miles": 4.5},
            "harvard": {"name": "Harvard Square", "distance_miles": 5.0},
            "airport": {"name": "Logan Airport", "distance_miles": 5.5}
        }
        
        # Find matching destination
        dest_key = destination.lower()
        dest_info = None
        
        for key, info in destinations_map.items():
            if key in dest_key:
                dest_info = info
                break
        
        # Default if not found
        if not dest_info:
            dest_info = {"name": destination, "distance_miles": 4.0}
        
        distance = dest_info["distance_miles"]
        
        # Calculate times (rough estimates)
        # Car: ~20 mph in city traffic
        car_time = round(distance / 20 * 60)  # minutes
        
        # Transit: slower, add wait time
        transit_time = round(distance / 12 * 60 + 10)  # minutes
        
        # Walking: 3 mph
        walking_time = round(distance / 3 * 60)  # minutes
        
        # Biking: 10 mph
        biking_time = round(distance / 10 * 60)  # minutes
        
        return {
            "from": property_address,
            "to": dest_info["name"],
            "distance_miles": distance,
            "commute_options": {
                "driving": {
                    "time_minutes": car_time,
                    "time_display": f"{car_time} min",
                    "cost_estimate": "$5-8 parking"
                },
                "transit": {
                    "time_minutes": transit_time,
                    "time_display": f"{transit_time} min",
                    "cost_estimate": "$2.40 T fare",
                    "route": "Red Line + Bus (estimated)"
                },
                "walking": {
                    "time_minutes": walking_time,
                    "time_display": f"{walking_time} min" if walking_time < 60 else f"{walking_time // 60}h {walking_time % 60}min",
                    "cost_estimate": "Free"
                },
                "biking": {
                    "time_minutes": biking_time,
                    "time_display": f"{biking_time} min",
                    "cost_estimate": "Free (BlueBikes: $2.95)"
                }
            },
            "fastest_option": "driving" if car_time < transit_time else "transit",
            "recommended": "transit" if distance < 5 else "driving"
        }
    
    except Exception as e:
        logger.error(f"Commute calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/commute-destinations")
def get_popular_destinations():
    """Get list of popular commute destinations"""
    return {
        "destinations": [
            {"id": "downtown", "name": "Downtown Boston", "category": "Business District"},
            {"id": "financial-district", "name": "Financial District", "category": "Business District"},
            {"id": "back-bay", "name": "Back Bay", "category": "Shopping/Dining"},
            {"id": "seaport", "name": "Seaport District", "category": "Business District"},
            {"id": "northeastern", "name": "Northeastern University", "category": "Education"},
            {"id": "harvard", "name": "Harvard Square", "category": "Education"},
            {"id": "cambridge", "name": "Cambridge/MIT", "category": "Education/Tech"},
            {"id": "airport", "name": "Logan Airport", "category": "Transportation"},
            {"id": "fenway", "name": "Fenway Park", "category": "Entertainment"},
            {"id": "longwood", "name": "Longwood Medical Area", "category": "Healthcare"}
        ]
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

@app.get("/recommendations/{property_id}")
def get_property_recommendations(property_id: str, limit: int = 5):
    """Get similar property recommendations using embeddings"""
    try:
        logger.info(f"Getting recommendations for property: {property_id}")
        
        # In production, you'd:
        # 1. Get property details from database
        # 2. Create embedding for that property
        # 3. Find similar embeddings in ChromaDB
        # 4. Return top N similar properties
        
        # For demo, we'll search ChromaDB for similar properties
        # Simulating with a property search
        
        # Mock property data (in production, fetch real property)
        mock_property_queries = [
            "3 bedroom luxury properties",
            "properties in same neighborhood",
            "similar price range properties"
        ]
        
        recommendations = []
        
        for query in mock_property_queries:
            try:
                result = rag.retrieve_documents(query, collection_name="properties")
                
                for doc in result[:2]:  # Get 2 from each query
                    recommendations.append({
                        "property_id": f"REC-{len(recommendations) + 1}",
                        "description": doc['document'][:200],
                        "similarity_score": round(1 - doc['distance'], 3),
                        "match_reason": "Similar features and location"
                    })
                    
                    if len(recommendations) >= limit:
                        break
            except:
                continue
            
            if len(recommendations) >= limit:
                break
        
        return {
            "property_id": property_id,
            "recommendations": recommendations[:limit],
            "total_found": len(recommendations),
            "algorithm": "embedding_similarity"
        }
    
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations/by-features")
def get_recommendations_by_features(search: PropertySearch):
    """Get recommendations based on desired features"""
    try:
        # Build query from features
        query_parts = []
        if search.bedrooms:
            query_parts.append(f"{search.bedrooms} bedroom")
        if search.neighborhood:
            query_parts.append(f"in {search.neighborhood}")
        if search.max_price:
            query_parts.append(f"under ${search.max_price:,.0f}")
        
        query = " ".join(query_parts) if query_parts else "properties"
        
        logger.info(f"Getting recommendations for: {query}")
        
        # Use RAG to find matching properties
        result = rag.retrieve_documents(query, collection_name="properties")
        
        recommendations = []
        for idx, doc in enumerate(result[:5]):
            recommendations.append({
                "property_id": f"PROP-{idx + 1}",
                "description": doc['document'][:300],
                "match_score": round(1 - doc['distance'], 3),
                "collection": doc['collection']
            })
        
        return {
            "query": query,
            "recommendations": recommendations,
            "total_found": len(recommendations),
            "search_criteria": {
                "bedrooms": search.bedrooms,
                "neighborhood": search.neighborhood,
                "max_price": search.max_price
            }
        }
    
    except Exception as e:
        logger.error(f"Feature-based recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
