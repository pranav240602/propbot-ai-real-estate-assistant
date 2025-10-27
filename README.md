# PropBot - AI Real Estate Assistant for Boston

MLOps Course Final Project - Group 18  
IE 7374 - Northeastern University  
**Milestone 1: Data Pipeline Submission**

## Team Members
- Dhanush Manoharan
- Pranav Rangbulla
- Gayatri Nair
- Priyanka Raj Rajendran
- Nishchay Gowda
- Shivakumar Hassan Lokesh

## Project Overview

PropBot is an intelligent conversational AI assistant for Boston real estate search, combining RAG (Retrieval-Augmented Generation) with comprehensive Boston data across all 23 neighborhoods.

**Data Scale:**
- 29,978 properties
- 316,467 crime records
- 2,055 amenities
- 3,016 transit stops
- 30 demographic records
- **Total: 351,546+ documents**

## Tech Stack
- **Orchestration:** Apache Airflow
- **Data Versioning:** DVC
- **Vector Database:** ChromaDB
- **Data Processing:** Python, Pandas
- **Testing:** pytest
- **Logging:** Python logging

---

## Project Structure
```
propbot-ai-real-estate-assistant/
├── airflow/
│   └── dags/
│       └── propbot_pipeline.py      # Main data pipeline DAG
├── data/
│   ├── raw/                         # Raw scraped data (DVC tracked)
│   ├── processed/                   # Cleaned data (DVC tracked)
│   └── database/
│       ├── chroma_ingest_all.py     # ChromaDB ingestion script
│       └── inspect_all_collections.py
├── scripts/
│   ├── Boston/
│   │   ├── collect_properties.py    # Property data scraping
│   │   ├── collect_crime_2023-2025.py
│   │   ├── collect_demographics.py
│   │   ├── collect_amenities.py
│   │   ├── collect_transit.py
│   │   └── clean_all_datasets.py    # Data preprocessing
│   ├── datasets_validation.py       # Data validation
│   ├── anomaly_detection.py         # Anomaly detection
│   └── bias_detection.py            # Bias detection via data slicing
├── tests/
│   └── test_data_pipeline.py        # Pipeline unit tests
├── logs/                            # Pipeline logs
├── chroma_backup/                   # ChromaDB data (DVC tracked)
├── dvc.yaml                         # DVC pipeline configuration
├── requirements.txt                 # Python dependencies
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip
- Git
- 10GB+ free disk space

### 1. Clone Repository
```bash
git clone https://github.com/pranav240602/propbot-ai-real-estate-assistant.git
cd propbot-ai-real-estate-assistant
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### 4. Setup DVC and Pull Data
```bash
# Initialize DVC (already done in repo)
dvc pull

# This will download:
# - data/ (raw and processed datasets)
# - chroma_backup/ (ChromaDB vector database)
```

### 5. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env and add your API keys if needed
```

---

## Running the Data Pipeline

### Option 1: Run with Airflow (Recommended)
```bash
# Initialize Airflow
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@propbot.com

# Start Airflow webserver
airflow webserver --port 8080 &

# Start Airflow scheduler
airflow scheduler &

# Access UI at http://localhost:8080
# Username: admin, Password: (what you set)

# Trigger the pipeline
airflow dags trigger propbot_data_pipeline
```

### Option 2: Run Individual Scripts
```bash
# 1. Data Acquisition
python scripts/Boston/collect_properties.py
python scripts/Boston/collect_crime_2023-2025.py
python scripts/Boston/collect_demographics.py
python scripts/Boston/collect_amenities.py
python scripts/Boston/collect_transit.py

# 2. Data Preprocessing
python scripts/Boston/clean_all_datasets.py
python scripts/datasets_validation.py

# 3. ChromaDB Ingestion
python data/database/chroma_ingest_all.py

# 4. Anomaly Detection
python scripts/anomaly_detection.py

# 5. Bias Detection
python scripts/bias_detection.py
```

---

## Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_data_pipeline.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## Data Pipeline Components

### 1. Data Acquisition
- **Sources:** Kaggle, Boston Open Data Portal, Boston PD API, US Census API, MBTA API, Yelp Fusion API
- **Output:** Raw CSV files in `data/raw/Boston/`
- **Logging:** All API calls and download status logged

### 2. Data Preprocessing
- **Tasks:** 
  - Remove duplicates
  - Handle missing values
  - Standardize formats
  - Data type conversions
  - Feature engineering
- **Output:** Cleaned CSV files in `data/processed/Boston/`

### 3. Data Validation
- **Checks:**
  - Schema validation
  - Data type verification
  - Range checks
  - Null value detection
- **Output:** Validation logs in `logs/`

### 4. ChromaDB Ingestion
- **Process:**
  - Generate embeddings using OpenAI `text-embedding-3-small`
  - Load into 5 collections: properties, crime, demographics, amenities, transit
  - Create vector indices for semantic search
- **Output:** `chroma_backup/` directory with vector database

### 5. Anomaly Detection
- **Detects:**
  - Missing values
  - Outliers (IQR method)
  - Invalid formats
  - Future dates
  - Negative values
- **Output:** `logs/anomaly_detection.log` and `logs/anomalies_report.txt`
- **Alerts:** Logged warnings for critical anomalies

### 6. Bias Detection
- **Data Slicing by:**
  - Neighborhoods (23 Boston neighborhoods)
  - Price ranges (<300K, 300-500K, 500-750K, 750K-1M, >1M)
  - Crime districts
  - Demographics
- **Metrics:**
  - Data coverage per slice
  - Price distribution variance
  - Missing data patterns
  - Underrepresentation detection
- **Output:** `logs/bias_detection.log` and `logs/bias_detection_report.txt`

---

## Data Versioning with DVC

### Track Data Changes
```bash
# Add new data
dvc add data/new_dataset.csv

# Commit to Git
git add data/new_dataset.csv.dvc .gitignore
git commit -m "Add new dataset"
git push

# Push data to DVC remote (if configured)
dvc push
```

### Pull Latest Data
```bash
git pull
dvc pull
```

---

## Pipeline Flow & Optimization

### Task Dependencies
```
Data Acquisition → Data Preprocessing → ChromaDB Ingestion → Data Validation
```

### Performance Metrics
- **Total Pipeline Runtime:** ~45 minutes
- **Data Acquisition:** ~15 minutes
- **Preprocessing:** ~10 minutes
- **ChromaDB Ingestion:** ~15 minutes
- **Validation:** ~5 minutes

### Bottleneck Analysis
View Airflow Gantt chart at: `http://localhost:8080/gantt?dag_id=propbot_data_pipeline`

**Identified Bottlenecks:**
1. API rate limits during data acquisition
2. Embedding generation during ChromaDB ingestion

**Optimizations Applied:**
1. Parallel API calls where possible
2. Batch processing for embeddings
3. Caching of repeated API calls

---

## Logging & Monitoring

All pipeline activities are logged to:
- `logs/pipeline.log` - Main pipeline log
- `logs/anomaly_detection.log` - Anomaly detection results
- `logs/bias_detection.log` - Bias detection analysis
- Airflow logs - Available in Airflow UI

**Log Levels:**
- INFO: Normal operations
- WARNING: Anomalies detected, non-critical issues
- ERROR: Critical failures requiring attention

---

## Error Handling

The pipeline includes comprehensive error handling:

1. **API Failures:** Automatic retries with exponential backoff
2. **Data Quality Issues:** Logged as warnings, pipeline continues
3. **ChromaDB Errors:** Pipeline fails, requires manual intervention
4. **Missing Files:** Clear error messages with resolution steps

---

## Reproducibility

### On a New Machine
```bash
# 1. Clone repo
git clone https://github.com/pranav240602/propbot-ai-real-estate-assistant.git
cd propbot-ai-real-estate-assistant

# 2. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Pull data with DVC
dvc pull

# 4. Run pipeline
airflow dags trigger propbot_data_pipeline
```

**Result:** Identical pipeline execution with same data and results.

---

## Milestone 1 Deliverables Checklist

- [x] Data Acquisition code
- [x] Data Preprocessing module
- [x] Test Modules (pytest)
- [x] Pipeline Orchestration (Airflow DAGs)
- [x] Data Versioning with DVC
- [x] Tracking and Logging
- [x] Data Schema & Statistics Generation
- [x] Anomaly Detection & Alerts
- [x] Pipeline Flow Optimization
- [x] Bias Detection (Data Slicing)
- [x] Proper Documentation (this README)
- [x] Modular Code (PEP 8 compliant)
- [x] Error Handling
- [x] Reproducibility

---

## Known Issues & Limitations

1. **API Rate Limits:** Some data sources have rate limits; pipeline includes retry logic
2. **Large File Size:** ChromaDB backup is 3.8GB; requires DVC for versioning
3. **Processing Time:** Full pipeline takes ~45 minutes on standard hardware

---

## Future Improvements

1. Implement real-time data streaming
2. Add more sophisticated bias mitigation techniques
3. Expand to more Boston neighborhoods
4. Add data quality dashboards
5. Implement automated retraining pipeline

---

## License

MIT License - Academic Project

## Contact

For questions or issues, please contact:
- Pranav Rangbulla - rangbulla.p@northeastern.edu
- Dhanush Manoharan - manoharan.dh@northeastern.edu

---

**Last Updated:** October 27, 2024  
**Milestone:** Data Pipeline (Milestone 1)  
**Status:**  Complete
