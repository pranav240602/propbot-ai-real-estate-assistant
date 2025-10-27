from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'propbot-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'propbot_data_pipeline',
    default_args=default_args,
    description='PropBot Boston Real Estate Data Pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 10, 1),
    catchup=False,
    tags=['propbot', 'boston', 'real-estate'],
)
def data_acquisition():
    """Task 1: Data Acquisition"""
    logger.info("="*50)
    logger.info("TASK 1: Data Acquisition Started")
    logger.info("="*50)
    
    try:
        import subprocess
        
        scripts = [
            'scripts/Boston/collect_properties.py',
            'scripts/Boston/collect_crime_2023-2025.py',
            'scripts/Boston/collect_demographics.py',
            'scripts/Boston/collect_amenities.py',
            'scripts/Boston/collect_transit.py'
        ]
        
        for script in scripts:
            logger.info(f"Running {script}...")
            result = subprocess.run(['python', script], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ {script} completed")
            else:
                logger.error(f"❌ {script} failed")
                raise Exception(f"Script {script} failed")
        
        logger.info("✅ Data acquisition completed")
        return "Success"
        
    except Exception as e:
        logger.error(f"❌ Failed: {str(e)}")
        raise

def data_preprocessing():
    """Task 2: Data Preprocessing"""
    logger.info("="*50)
    logger.info("TASK 2: Preprocessing Started")
    logger.info("="*50)
    
    try:
        import subprocess
        
        logger.info("Running data cleaning...")
        result = subprocess.run(['python', 'scripts/Boston/clean_all_datasets.py'], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Cleaning completed")
        else:
            raise Exception("Cleaning failed")
        
        logger.info("Running validation...")
        subprocess.run(['python', 'scripts/datasets_validation.py'], capture_output=True, text=True)
        
        logger.info("✅ Preprocessing completed")
        return "Success"
        
    except Exception as e:
        logger.error(f"❌ Failed: {str(e)}")
        raise

def chromadb_ingestion():
    """Task 3: ChromaDB Ingestion"""
    logger.info("="*50)
    logger.info("TASK 3: ChromaDB Ingestion Started")
    logger.info("="*50)
    
    try:
        import subprocess
        
        logger.info("Loading into ChromaDB...")
        result = subprocess.run(['python', 'data/database/chroma_ingest_all.py'], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ ChromaDB ingestion completed")
        else:
            raise Exception("ChromaDB failed")
        
        logger.info("Inspecting collections...")
        subprocess.run(['python', 'data/database/inspect_all_collections.py'], capture_output=True, text=True)
        
        logger.info("✅ ChromaDB completed")
        return "Success"
        
    except Exception as e:
        logger.error(f"❌ Failed: {str(e)}")
        raise

def data_validation():
    """Task 4: Final Validation"""
    logger.info("="*50)
    logger.info("TASK 4: Validation Started")
    logger.info("="*50)
    
    try:
        import pandas as pd
        
        processed_dir = 'data/processed'
        files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
        logger.info(f"Found {len(files)} files")
        
        total = 0
        for file in files:
            df = pd.read_csv(os.path.join(processed_dir, file))
            total += len(df)
            logger.info(f"✅ {file}: {len(df)} rows")
        
        logger.info(f"✅ Total: {total} rows")
        
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_data")
        collections = client.list_collections()
        logger.info(f"✅ ChromaDB: {len(collections)} collections")
        
        return "Success"
        
    except Exception as e:
        logger.error(f"❌ Failed: {str(e)}")
        raise
# Define Airflow tasks
task1 = PythonOperator(
    task_id='data_acquisition',
    python_callable=data_acquisition,
    dag=dag,
)

task2 = PythonOperator(
    task_id='data_preprocessing',
    python_callable=data_preprocessing,
    dag=dag,
)

task3 = PythonOperator(
    task_id='chromadb_ingestion',
    python_callable=chromadb_ingestion,
    dag=dag,
)

task4 = PythonOperator(
    task_id='data_validation',
    python_callable=data_validation,
    dag=dag,
)

# Set task dependencies - creates the pipeline flow
task1 >> task2 >> task3 >> task4
