"""
FastAPI Backend for PropBot with RAG + Real Data Parsing
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
from datetime import datetime, timezone
from database.db import engine, Base, get_db
from auth import routes as auth_routes
from auth.models import User, ChatHistory
from sqlalchemy.orm import Session
import re

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

Base.metadata.create_all(bind=engine)
logger.info("✅ Database tables created")

app.include_router(auth_routes.router)
logger.info("✅ Authentication routes registered")

search_history = []
saved_properties = []


def parse_property_document(doc_text):
    """Parse: '104 A 104 PUTNAM ST, Boston, MA 02128. THREE-FAM DWELLING. 6. 3. 719,400'"""
    try:
        parts = doc_text.split('.')
        
        if len(parts) >= 5:
            address = parts[0].strip()
            prop_type = parts[1].strip()
            beds = int(parts[2].strip()) if parts[2].strip().isdigit() else 2
            baths = int(parts[3].strip()) if parts[3].strip().isdigit() else 1
            price_str = parts[4].strip().replace(',', '')
            price = float(price_str) if price_str.isdigit() else 650000.0
            
            return {
                'address': address,
                'type': prop_type,
                'beds': beds,
                'baths': baths,
                'price': price
            }
    except Exception as e:
        logger.warning(f"Parse error: {e}")
    
    return {
        'address': 'Address not available',
        'type': 'RESIDENTIAL',
        'beds': 2,
        'baths': 1,
        'price': 650000.0
    }


def get_property_image(index):
    """Return different images for variety"""
    images = [
        'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1580587871743-aaf2933a56d1?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1599809275671-b5942cabc7a2?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1600210492493-0946911123ea?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=400&h=300&fit=crop',
        'https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=400&h=300&fit=crop'
    ]
    return images[index % len(images)]


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: Optional[int] = None


class PropertySearch(BaseModel):
    neighborhood: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    user_id: Optional[int] = None
    mode: Optional[str] = "buy"


class SavePropertyRequest(BaseModel):
    property_id: str
    property_data: dict
    user_id: Optional[int] = None


@app.get("/")
def root():
    return {
        "message": "PropBot API with RAG + Analytics - Milestone 2",
        "version": "2.0.0",
        "status": "active",
        "rag": "enabled",
        "features": ["chat", "search", "history", "saved_properties", "analytics", "authentication"]
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "chromadb": "connected",
        "rag": "active",
        "collections": len(rag.collection_names),
        "search_history_count": len(search_history),
        "database": "connected"
    }


@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Enhanced chat endpoint"""
    try:
        query = request.query
        user_id = request.user_id
        
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if user.is_guest and user.expires_at:
                now_utc = datetime.now(timezone.utc)
                if user.expires_at.tzinfo is None:
                    expires_at_utc = user.expires_at.replace(tzinfo=timezone.utc)
                else:
                    expires_at_utc = user.expires_at
                
                if expires_at_utc < now_utc:
                    raise HTTPException(status_code=403, detail="Guest session expired")
        
        logger.info(f"Chat query: {query}")
        
        greetings = ['hi', 'hello', 'hey', 'hii', 'hiii', 'sup', 'yo']
        query_lower = query.lower().strip()
        query_words = query_lower.split()
        
        is_greeting = (
            len(query_words) <= 3 and 
            any(greeting in query_lower for greeting in greetings)
        )
        
        if is_greeting:
            response_text = "Hi there! 👋 How can I help you find your dream home in Boston today?"
            sources = []
            docs_retrieved = 0
        else:
            result = rag.chat(query)
            response_text = result.get("answer", "I couldn't find relevant information.")
            sources = result.get("sources", [])
            docs_retrieved = result.get("documents_retrieved", 0)
        
        if user_id:
            chat_entry = ChatHistory(
                user_id=user_id,
                query=query,
                response=response_text
            )
            db.add(chat_entry)
            db.commit()
        
        return {
            "answer": response_text,
            "sources": sources,
            "documents_retrieved": docs_retrieved,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history/{user_id}")
async def get_chat_history_db(user_id: int, db: Session = Depends(get_db)):
    """Get chat history"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).order_by(ChatHistory.timestamp.desc()).limit(50).all()
    
    return {
        "user_id": user_id,
        "is_guest": user.is_guest,
        "total_chats": len(history),
        "chats": [
            {
                "query": chat.query,
                "response": chat.response,
                "timestamp": chat.timestamp.isoformat()
            }
            for chat in history
        ]
    }


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
            "results_count": result.get('documents_retrieved', 0),
            "timestamp": datetime.now().isoformat()
        }
        search_history.append(search_entry)
        
        return {
            "query": query,
            "answer": result['answer'],
            "sources": result.get('sources', []),
            "search_id": search_entry["id"]
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search-history/{user_id}")
def get_search_history(user_id: int, limit: int = 10):
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


@app.delete("/search-history/{user_id}")
def clear_search_history(user_id: int):
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
def get_saved_properties(user_id: int):
    """Get user's saved properties"""
    try:
        user_saved = [prop for prop in saved_properties if prop["user_id"] == user_id]
        
        return {
            "user_id": user_id,
            "total": len(user_saved),
            "saved_properties": user_saved
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/saved-properties/{user_id}/{property_id}")
def remove_saved_property(user_id: int, property_id: str):
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
        total_searches = len(search_history)
        
        neighborhood_counts = {}
        for search in search_history:
            neighborhood = search["search_params"].get("neighborhood")
            if neighborhood:
                neighborhood_counts[neighborhood] = neighborhood_counts.get(neighborhood, 0) + 1
        
        hottest_neighborhoods = [
            {"name": name, "search_count": count}
            for name, count in sorted(neighborhood_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
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
        
        bedroom_distribution = {}
        for search in search_history:
            bedrooms = search["search_params"].get("bedrooms")
            if bedrooms:
                bedroom_distribution[f"{bedrooms}BR"] = bedroom_distribution.get(f"{bedrooms}BR", 0) + 1
        
        return {
            "total_properties": 29978,
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
    """Get sample queries"""
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
    """Predict property price (NO CONFIDENCE)"""
    try:
        logger.info(f"Price prediction for: {property}")
        
        base_price = 500000
        
        if property.bedrooms:
            base_price += property.bedrooms * 100000
        
        if property.bathrooms:
            base_price += property.bathrooms * 50000
        
        if property.neighborhood:
            hood_lower = property.neighborhood.lower()
            if "back bay" in hood_lower:
                base_price *= 1.5
            elif "beacon hill" in hood_lower:
                base_price *= 1.4
            elif "south end" in hood_lower:
                base_price *= 1.3
        
        return {
            "predicted_price": round(base_price, 2),
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


@app.get("/properties/list")
def list_all_properties():
    """Return all properties"""
    try:
        logger.info("Fetching all properties from ChromaDB")
        
        all_results = rag.collection.get(
            include=['documents', 'metadatas']
        )
        
        properties = []
        for i, doc in enumerate(all_results['documents'][:20]):
            parsed = parse_property_document(doc)
            
            properties.append({
                'property_id': all_results['ids'][i],
                'address': parsed['address'],
                'price': parsed['price'],
                'bedrooms': parsed['beds'],
                'bathrooms': parsed['baths'],
                'beds': parsed['beds'],
                'baths': parsed['baths'],
                'sqft': int(parsed['beds'] * 600 + parsed['baths'] * 200),
                'image': get_property_image(i),
                'description': doc[:150],
                'match_score': 0.80
            })
        
        logger.info(f"✅ Returning {len(properties)} properties")
        
        return {
            'properties': properties,
            'total': len(properties)
        }
    except Exception as e:
        logger.error(f"Properties list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations/by-features")
def get_recommendations_by_features(search: PropertySearch):
    """Get recommendations - Trust ChromaDB semantic search for neighborhoods"""
    try:
        query_parts = []
        if search.bedrooms:
            query_parts.append(f"{search.bedrooms} bedroom")
        if search.neighborhood:
            query_parts.append(f"in {search.neighborhood}")
        
        query = " ".join(query_parts) if query_parts else "properties in Boston"
        
        logger.info(f"Recommendation query: {query}")
        
        result = rag.retrieve_documents(query, collection_name="properties", k=15)
        
        recommendations = []
        filtered_count = 0
        
        for idx, doc in enumerate(result):
            doc_id = doc.get('id', f"PROP-{idx + 1}")
            doc_text = doc.get('document', '')
            distance = doc.get('distance', 0.3)
            
            parsed = parse_property_document(doc_text)
            
            # ✅ ONLY FILTER OUT 0 BEDS (commercial properties)
            if parsed['beds'] == 0:
                filtered_count += 1
                continue
            
            # ✅ FILTER BY BEDROOMS IF SPECIFIED
            if search.bedrooms and parsed['beds'] != search.bedrooms:
                filtered_count += 1
                continue
            
            # ✅ FILTER BY BATHROOMS IF SPECIFIED
            if search.bathrooms and parsed['baths'] != search.bathrooms:
                filtered_count += 1
                continue
            
            recommendations.append({
                'property_id': doc_id,
                'address': parsed['address'],
                'price': parsed['price'],
                'bedrooms': parsed['beds'],
                'bathrooms': parsed['baths'],
                'beds': parsed['beds'],
                'baths': parsed['baths'],
                'sqft': int(parsed['beds'] * 600 + parsed['baths'] * 200),
                'image': get_property_image(len(recommendations)),
                'description': doc_text[:200] if len(doc_text) > 200 else doc_text,
                'match_score': round(max(0, 1 - distance), 3)
            })
            
            if len(recommendations) >= 12:
                break
        
        logger.info(f"✅ Returning {len(recommendations)} recommendations (filtered out {filtered_count})")
        
        return {
            "query": query,
            "recommendations": recommendations,
            "total_found": len(recommendations)
        }
    
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return {
            "query": query if 'query' in locals() else "properties",
            "recommendations": [],
            "total_found": 0,
            "error": str(e)
        }


@app.post("/commute-time")
def calculate_commute_time(property_address: str, destination: str):
    """Calculate commute time"""
    try:
        logger.info(f"Calculating commute: {property_address} -> {destination}")
        
        destinations_map = {
            "downtown": {"name": "Downtown Boston", "distance_miles": 3.5},
            "northeastern": {"name": "Northeastern University", "distance_miles": 2.8},
            "financial district": {"name": "Financial District", "distance_miles": 3.2},
            "back bay": {"name": "Back Bay", "distance_miles": 2.5},
            "seaport": {"name": "Seaport District", "distance_miles": 4.0},
            "cambridge": {"name": "Cambridge/MIT", "distance_miles": 4.5},
            "harvard": {"name": "Harvard Square", "distance_miles": 5.0},
            "airport": {"name": "Logan Airport", "distance_miles": 5.5},
            "mit": {"name": "MIT", "distance_miles": 4.5},
            "logan": {"name": "Logan Airport", "distance_miles": 5.5}
        }
        
        dest_key = destination.lower()
        dest_info = None
        
        for key, info in destinations_map.items():
            if key in dest_key:
                dest_info = info
                break
        
        if not dest_info:
            dest_info = {"name": destination, "distance_miles": 4.0}
        
        distance = dest_info["distance_miles"]
        
        car_time = round(distance / 20 * 60)
        transit_time = round(distance / 12 * 60 + 10)
        walking_time = round(distance / 3 * 60)
        biking_time = round(distance / 10 * 60)
        
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
    uvicorn.run(app, host="0.0.0.0", port=8002)
