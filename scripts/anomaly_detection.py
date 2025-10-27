"""
Anomaly Detection Module for PropBot Data Pipeline
Detects missing values, outliers, and invalid formats in the data
"""

import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/anomaly_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detect anomalies in PropBot datasets"""
    
    def __init__(self, data_dir='data/processed/Boston'):
        self.data_dir = data_dir
        self.anomalies = []
        
    def detect_missing_values(self, df, filename):
        """Detect missing values in dataframe"""
        logger.info(f"Checking missing values in {filename}...")
        
        missing = df.isnull().sum()
        total_missing = missing.sum()
        
        if total_missing > 0:
            logger.warning(f"⚠️  Found {total_missing} missing values in {filename}")
            for col in missing[missing > 0].index:
                count = missing[col]
                percentage = (count / len(df)) * 100
                logger.warning(f"   - {col}: {count} missing ({percentage:.2f}%)")
                self.anomalies.append({
                    'file': filename,
                    'type': 'missing_values',
                    'column': col,
                    'count': int(count),
                    'percentage': float(percentage)
                })
        else:
            logger.info(f"✅ No missing values in {filename}")
            
        return total_missing
    
    def detect_outliers(self, df, filename, numeric_columns=None):
        """Detect outliers using IQR method"""
        logger.info(f"Checking outliers in {filename}...")
        
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        total_outliers = 0
        
        for col in numeric_columns:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                count = len(outliers)
                
                if count > 0:
                    percentage = (count / len(df)) * 100
                    logger.warning(f"⚠️  {col}: {count} outliers ({percentage:.2f}%)")
                    total_outliers += count
                    self.anomalies.append({
                        'file': filename,
                        'type': 'outliers',
                        'column': col,
                        'count': int(count),
                        'percentage': float(percentage),
                        'bounds': f"[{lower_bound:.2f}, {upper_bound:.2f}]"
                    })
        
        if total_outliers == 0:
            logger.info(f"✅ No outliers detected in {filename}")
        else:
            logger.warning(f"⚠️  Total outliers in {filename}: {total_outliers}")
            
        return total_outliers
    
    def detect_invalid_formats(self, df, filename):
        """Detect invalid data formats"""
        logger.info(f"Checking invalid formats in {filename}...")
        
        issues = 0
        
        # Check for negative prices (if price column exists)
        if 'price' in df.columns:
            negative_prices = df[df['price'] < 0]
            if len(negative_prices) > 0:
                logger.warning(f"⚠️  Found {len(negative_prices)} negative prices")
                issues += len(negative_prices)
                self.anomalies.append({
                    'file': filename,
                    'type': 'invalid_format',
                    'issue': 'negative_prices',
                    'count': len(negative_prices)
                })
        
        # Check for future dates (if date columns exist)
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            future_dates = df[df[col] > pd.Timestamp.now()]
            if len(future_dates) > 0:
                logger.warning(f"⚠️  Found {len(future_dates)} future dates in {col}")
                issues += len(future_dates)
                self.anomalies.append({
                    'file': filename,
                    'type': 'invalid_format',
                    'issue': f'future_dates_{col}',
                    'count': len(future_dates)
                })
        
        if issues == 0:
            logger.info(f"✅ No format issues in {filename}")
            
        return issues
    
    def analyze_file(self, filepath):
        """Analyze a single CSV file for anomalies"""
        filename = os.path.basename(filepath)
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing: {filename}")
        logger.info(f"{'='*60}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Run all anomaly checks
            missing = self.detect_missing_values(df, filename)
            outliers = self.detect_outliers(df, filename)
            invalid = self.detect_invalid_formats(df, filename)
            
            total_anomalies = missing + outliers + invalid
            
            if total_anomalies > 0:
                logger.warning(f"⚠️  Total anomalies in {filename}: {total_anomalies}")
            else:
                logger.info(f"✅ {filename} passed all checks!")
                
            return total_anomalies
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {filepath}: {str(e)}")
            return 0
    
    def analyze_all_files(self):
        """Analyze all CSV files in the data directory"""
        logger.info("\n" + "="*60)
        logger.info("STARTING ANOMALY DETECTION")
        logger.info("="*60 + "\n")
        
        if not os.path.exists(self.data_dir):
            logger.error(f"❌ Data directory not found: {self.data_dir}")
            return
        
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        logger.info(f"Found {len(csv_files)} CSV files to analyze\n")
        
        total_anomalies = 0
        for filename in csv_files:
            filepath = os.path.join(self.data_dir, filename)
            anomalies = self.analyze_file(filepath)
            total_anomalies += anomalies
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("ANOMALY DETECTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Files analyzed: {len(csv_files)}")
        logger.info(f"Total anomalies detected: {total_anomalies}")
        logger.info(f"Anomaly types found: {len(self.anomalies)}")
        
        if total_anomalies > 0:
            logger.warning("⚠️  ALERT: Anomalies detected in data!")
            logger.warning("Review logs/anomaly_detection.log for details")
        else:
            logger.info("✅ All data passed quality checks!")
        
        return self.anomalies

def main():
    """Main function to run anomaly detection"""
    detector = AnomalyDetector()
    anomalies = detector.analyze_all_files()
    
    # Save anomalies report
    if anomalies:
        report_path = 'logs/anomalies_report.txt'
        with open(report_path, 'w') as f:
            f.write(f"Anomaly Detection Report - {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            for anomaly in anomalies:
                f.write(f"{anomaly}\n")
        logger.info(f"Anomaly report saved to {report_path}")

if __name__ == "__main__":
    main()
