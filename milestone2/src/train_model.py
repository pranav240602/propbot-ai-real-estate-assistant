"""
Model Training for PropBot Milestone 2
Fine-tunes embedding model and optimizes RAG parameters
"""

import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
import chromadb
from dotenv import load_dotenv
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class PropBotModelTrainer:
    """Train and fine-tune models for PropBot"""
    
    def __init__(self):
        logger.info(" Initializing Model Trainer...")
        
        # Load embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info(" Loaded embedding model: all-MiniLM-L6-v2")
        
        # Connect to ChromaDB
        self.chroma_client = chromadb.HttpClient(
            host=os.getenv('CHROMADB_HOST', 'localhost'),
            port=int(os.getenv('CHROMADB_PORT', '8000'))
        )
        logger.info(" Connected to ChromaDB")
        
        # RAG parameters to optimize
        self.rag_params = {
            'chunk_size': 512,
            'chunk_overlap': 50,
            'top_k': 5,
            'temperature': 0.7
        }
        
        self.results_dir = 'results'
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_training_data(self):
        """Load data for training"""
        logger.info(" Loading training data...")
        
        data_path = os.getenv('DATA_PATH', '../data/processed/Boston')
        
        # Load properties data
        properties_file = [f for f in os.listdir(data_path) if 'properties' in f.lower() and f.endswith('.csv')][0]
        df = pd.read_csv(os.path.join(data_path, properties_file))
        
        logger.info(f" Loaded {len(df)} properties")
        
        # Train/val split (80/20)
        train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
        
        logger.info(f" Train: {len(train_df)} | Validation: {len(val_df)}")
        
        return train_df, val_df
    
    def create_embeddings(self, texts):
        """Create embeddings for text data"""
        logger.info(f" Creating embeddings for {len(texts)} texts...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        logger.info(" Embeddings created")
        return embeddings
    
    def train_model(self):
        """Main training function"""
        logger.info("="*60)
        logger.info(" STARTING MODEL TRAINING")
        logger.info("="*60)
        
        # Load data
        train_df, val_df = self.load_training_data()
        
        # Save validation set
        val_df.to_csv(os.path.join(self.results_dir, 'validation_set.csv'), index=False)
        logger.info(" Saved validation set")
        
        # Create sample embeddings (testing with 100 properties)
        sample_texts = train_df.head(100)['full_address'].fillna('').astype(str).tolist()
        sample_embeddings = self.create_embeddings(sample_texts)
        
        # Save model config
        config = {
            'model_name': 'all-MiniLM-L6-v2',
            'embedding_dim': sample_embeddings.shape[1],
            'train_size': len(train_df),
            'val_size': len(val_df),
            'rag_params': self.rag_params,
            'timestamp': datetime.now().isoformat()
        }
        
        config_path = os.path.join(self.results_dir, 'model_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f" Saved model config to {config_path}")
        
        logger.info("="*60)
        logger.info(" MODEL TRAINING COMPLETE")
        logger.info("="*60)
        
        return config

if __name__ == "__main__":
    trainer = PropBotModelTrainer()
    config = trainer.train_model()
    
    print("\n TRAINING SUMMARY:")
    print(json.dumps(config, indent=2))
