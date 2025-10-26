# PropBot: AI-Powered Real Estate Chatbot for Boston

**MLOps Course Final Project - Group 18**  
**IE 7374 - Northeastern University**  
**MLOps Innovation Expo: December 12, 2024**

##  Team Members
1. Dhanush Manoharan
2. Pranav Rangbulla
3. Gayatri Nair
4. Priyanka Raj Rajendran
5. Nishchay Gowda
6. Shivakumar Hassan Lokesh

##  Project Overview
PropBot is an intelligent conversational AI assistant for Boston real estate search. It combines:
- **RAG (Retrieval-Augmented Generation)** for natural language understanding
- **Comprehensive Boston data** across all 23 neighborhoods
- **Crime trend analysis** with 5-year historical data
- **Real-time semantic search** using vector embeddings

**Coverage:** All Boston neighborhoods + 31 ZIP codes  
**Data Scale:** 40,000+ properties with crime, demographics, transit, and amenities  
**Tech Stack:** Python, Airflow, PostgreSQL, Chroma Vector DB, FastAPI, GPT-3.5

##  Key Features
- Natural language property search
- Crime trend analysis and predictions
- Multi-criteria filtering (price, safety, commute, amenities)
- Personalized recommendations
- Support for students, families, professionals, and business owners

##  Project Structure
```
propbot-mlops-boston/
├── data/              # Data storage (DVC tracked)
├── scripts/           # Data collection scripts
├── airflow/           # Pipeline orchestration
├── database/          # Database schemas
├── app/               # FastAPI chatbot
├── tests/             # Testing suite
├── evaluation/        # RAG quality evaluation
└── monitoring/        # Performance tracking
```

##  Data Sources (All FREE APIs)
- **Properties:** Kaggle + Boston Open Data Portal
- **Crime:** Boston Police Department API
- **Demographics:** US Census Bureau API
- **Transportation:** MBTA API
- **Amenities:** Yelp Fusion API

##  Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git
- Docker (for Week 3+)

### Installation
```bash
# Clone repository
git clone https://github.com/pranav240602/propbot-ai-real-estate-assistant.git
cd propbot-mlops-boston

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Week 1-2: Data Collection
```bash
# Collect all Boston data
python scripts/collect_all_data.py

# Or collect individually:
python scripts/collect_crime.py
python scripts/collect_properties.py
python scripts/collect_demographics.py
```

##  Timeline
- **Week 1-2:** Data collection (APIs)
- **Week 3-4:** Airflow pipeline setup
- **Week 5-6:** Database setup & data loading
- **Week 7-8:** RAG implementation & FastAPI
- **Week 9-10:** Testing & evaluation
- **Week 11-12:** Polish & demo preparation

##  Success Metrics
- **Retrieval Accuracy:** 85%+ precision
- **Response Speed:** < 200ms average
- **Data Coverage:** All 23 Boston neighborhoods
- **User Satisfaction:** 90%+ in testing

##  MLOps Innovation Expo
**Date:** December 12, 2024  
**Evaluation:** Google representatives  
**Grade Weight:** 90% of final grade

##  License
MIT License - Academic Project

##  Contact
Dhanush Manoharan - manoharan.dh@northeastern.edu  
Pranav Rangbulla -
Gayatri Nair -
Priyanka Raj Rajendran -
Nishchay Gowda - 
Shivakumar Hassan Lokesh - 
GitHub: https://github.com/pranav240602/propbot-ai-real-estate-assistant
```

