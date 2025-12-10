"""
Data Loader for PropBot Milestone 2
Loads data from Milestone 1 (CSV files + ChromaDB)
"""

import os
import pandas as pd
import chromadb
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class PropBotDataLoader:
    """Load and prepare data from Milestone 1"""
    
    def __init__(self):
        self.data_path = os.getenv('DATA_PATH', '../data/processed')
        self.chromadb_host = os.getenv('CHROMADB_HOST', 'localhost')
        self.chromadb_port = int(os.getenv('CHROMADB_PORT', '8000'))
        
        logger.info("🔧 Initializing PropBot Data Loader...")
        logger.info(f" Data path: {self.data_path}")
        logger.info(f"  ChromaDB: {self.chromadb_host}:{self.chromadb_port}")
        
        # Connect to ChromaDB
        try:
            self.chroma_client = chromadb.HttpClient(
                host=self.chromadb_host,
                port=self.chromadb_port
            )
            logger.info(" Connected to ChromaDB")
        except Exception as e:
            logger.error(f" ChromaDB connection failed: {e}")
            self.chroma_client = None
    
    def load_csv_data(self):
        """Load all CSV files from processed data folder"""
        logger.info(" Loading CSV data...")
        
        data_dir = self.data_path
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        datasets = {}
        total_rows = 0
        
        for file in csv_files:
            try:
                file_path = os.path.join(data_dir, file)
                df = pd.read_csv(file_path)
                dataset_name = file.replace('.csv', '')
                datasets[dataset_name] = df
                total_rows += len(df)
                logger.info(f" Loaded {file}: {len(df)} rows")
            except Exception as e:
                logger.error(f" Failed to load {file}: {e}")
        
        logger.info(f" Total datasets loaded: {len(datasets)}")
        logger.info(f" Total rows: {total_rows}")
        
        return datasets
    
    def get_chromadb_collections(self):
        """Get all ChromaDB collections"""
        if not self.chroma_client:
            logger.error(" ChromaDB not connected")
            return []
        
        try:
            logger.info("  Fetching ChromaDB collections...")
            collections = self.chroma_client.list_collections()
            
            collection_info = []
            for collection in collections:
                count = collection.count()
                collection_info.append({
                    'name': collection.name,
                    'count': count
                })
                logger.info(f" Collection '{collection.name}': {count} documents")
            
            return collection_info
        except Exception as e:
            logger.error(f" Failed to fetch collections: {e}")
            return []
    
    def load_all_data(self):
        """Load both CSV and ChromaDB data"""
        logger.info("="*60)
        logger.info(" LOADING ALL DATA FROM MILESTONE 1")
        logger.info("="*60)
        
        # Load CSV data
        csv_datasets = self.load_csv_data()
        
        # Load ChromaDB collections
        chroma_collections = self.get_chromadb_collections()
        
        logger.info("="*60)
        logger.info(" DATA LOADING COMPLETE")
        logger.info("="*60)
        
        return {
            'csv_datasets': csv_datasets,
            'chroma_collections': chroma_collections
        }


# Test function
def test_data_loader():
    """Test the data loader"""
    logger.info(" Testing Data Loader...")
    
    loader = PropBotDataLoader()
    data = loader.load_all_data()
    
    logger.info("\n SUMMARY:")
    logger.info(f"   CSV Datasets: {len(data['csv_datasets'])}")
    logger.info(f"   ChromaDB Collections: {len(data['chroma_collections'])}")
    
    return data


if __name__ == "__main__":
    test_data_loader()
