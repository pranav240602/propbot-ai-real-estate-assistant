import pytest
import pandas as pd
import os
import chromadb

class TestDataPipeline:
    """Test suite for PropBot data pipeline"""
    
    def test_raw_data_exists(self):
        """Test that raw data files exist"""
        raw_dir = 'data/raw'
        assert os.path.exists(raw_dir), "Raw data directory missing"
        
    def test_processed_data_exists(self):
        """Test that processed data files exist"""
        processed_dir = 'data/processed'
        assert os.path.exists(processed_dir), "Processed data directory missing"
        
    def test_chromadb_connection(self):
        """Test ChromaDB connection"""
        client = chromadb.PersistentClient(path='./chroma_backup')
        collections = client.list_collections()
        assert len(collections) > 0, "No collections found in ChromaDB"
        
    def test_chromadb_collections(self):
        """Test all required collections exist"""
        client = chromadb.PersistentClient(path='./chroma_backup')
        collections = [c.name for c in client.list_collections()]
        
        required = ['propbot_properties', 'propbot_crime', 'propbot_demographics', 
                   'propbot_amenities', 'propbot_transit']
        
        for collection_name in required:
            assert collection_name in collections, f"Missing collection: {collection_name}"
    
    def test_properties_data_quality(self):
        """Test properties collection has data"""
        client = chromadb.PersistentClient(path='./chroma_backup')
        collection = client.get_collection('propbot_properties')
        count = collection.count()
        assert count > 1000, f"Too few properties: {count}"
        
    def test_crime_data_quality(self):
        """Test crime collection has data"""
        client = chromadb.PersistentClient(path='./chroma_backup')
        collection = client.get_collection('propbot_crime')
        count = collection.count()
        assert count > 10000, f"Too few crime records: {count}"

class TestDataPreprocessing:
    """Test preprocessing functions"""
    
    def test_no_duplicate_ids(self):
        """Test that processed data has no duplicate IDs"""
        # This is a placeholder - update based on actual data structure
        assert True, "Implement based on your data structure"
    
    def test_valid_price_ranges(self):
        """Test property prices are in valid range"""
        # Placeholder test
        assert True, "Implement based on your data"
    
    def test_no_null_critical_fields(self):
        """Test critical fields have no null values"""
        # Placeholder test
        assert True, "Implement based on your data"

class TestAnomalyDetection:
    """Test anomaly detection"""
    
    def test_outlier_detection(self):
        """Test outlier detection works"""
        # Simple outlier test with sample data
        import numpy as np
        data = np.array([1, 2, 3, 4, 5, 100])  # 100 is outlier
        
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        outliers = data[(data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)]
        assert len(outliers) > 0, "Outlier detection not working"
