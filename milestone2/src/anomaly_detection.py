"""
Anomaly Detection for PropBot
Detects outliers and suspicious data
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
import logging
from datetime import datetime
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detect anomalies in property data"""
    
    def __init__(self):
        self.results_dir = 'results'
        self.anomaly_dir = os.path.join(self.results_dir, 'anomaly_detection')
        os.makedirs(self.anomaly_dir, exist_ok=True)
        logger.info("🔧 Anomaly Detector initialized")
    
    def load_data(self):
        """Load property data"""
        data_path = os.getenv('DATA_PATH', '../data/processed/Boston')
        properties_file = [f for f in os.listdir(data_path) if 'properties' in f.lower() and f.endswith('.csv')][0]
        df = pd.read_csv(os.path.join(data_path, properties_file))
        logger.info(f"✅ Loaded {len(df)} properties")
        return df
    
    def prepare_features(self, df):
        """Prepare features for anomaly detection"""
        feature_cols = ['TOTAL_VALUE', 'year_built', 'gross_square_feet', 
                       'living_square_feet', 'BED_RMS', 'FULL_BTH']
        
        available_cols = [col for col in feature_cols if col in df.columns]
        
        X = df[available_cols].copy()
        
        # CLEAN: Remove commas and convert to numeric
        for col in X.columns:
            if X[col].dtype == 'object':
                X[col] = X[col].astype(str).str.replace(',', '')
            X[col] = pd.to_numeric(X[col], errors='coerce')
        
        X = X.fillna(X.median())
        
        logger.info(f"✅ Prepared {len(available_cols)} features")
        return X, available_cols
    
    def detect_anomalies(self):
        """Detect anomalies using Isolation Forest"""
        logger.info("="*60)
        logger.info("🚀 STARTING ANOMALY DETECTION")
        logger.info("="*60)
        
        df = self.load_data()
        X, feature_names = self.prepare_features(df)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        logger.info("🔍 Training Isolation Forest...")
        iso_forest = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_estimators=100
        )
        
        predictions = iso_forest.fit_predict(X_scaled)
        anomaly_scores = iso_forest.score_samples(X_scaled)
        
        anomaly_mask = predictions == -1
        normal_mask = predictions == 1
        
        n_anomalies = anomaly_mask.sum()
        n_normal = normal_mask.sum()
        
        logger.info(f"✅ Detected {n_anomalies} anomalies ({n_anomalies/len(df)*100:.2f}%)")
        logger.info(f"✅ Normal samples: {n_normal} ({n_normal/len(df)*100:.2f}%)")
        
        anomaly_df = df[anomaly_mask].copy()
        anomaly_df['anomaly_score'] = anomaly_scores[anomaly_mask]
        anomaly_df = anomaly_df.sort_values('anomaly_score')
        
        anomaly_path = os.path.join(self.anomaly_dir, 'detected_anomalies.csv')
        anomaly_df.to_csv(anomaly_path, index=False)
        
        logger.info(f"✅ Saved anomalies to: {anomaly_path}")
        
        # Simple stats without complex calculations
        report = {
            'total_samples': len(df),
            'anomalies_detected': int(n_anomalies),
            'anomaly_percentage': float(n_anomalies/len(df)*100),
            'normal_samples': int(n_normal),
            'detection_method': 'Isolation Forest',
            'contamination_rate': 0.05,
            'features_used': feature_names,
            'timestamp': datetime.now().isoformat()
        }
        
        report_path = os.path.join(self.anomaly_dir, 'anomaly_detection_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Report saved: {report_path}")
        
        plt.figure(figsize=(10, 6))
        plt.hist(anomaly_scores[normal_mask], bins=50, alpha=0.7, label='Normal', color='green')
        plt.hist(anomaly_scores[anomaly_mask], bins=50, alpha=0.7, label='Anomaly', color='red')
        plt.xlabel('Anomaly Score')
        plt.ylabel('Frequency')
        plt.title('Anomaly Score Distribution')
        plt.legend()
        
        plot_path = os.path.join(self.anomaly_dir, 'anomaly_scores.png')
        plt.savefig(plot_path)
        plt.close()
        
        logger.info(f"✅ Plot saved: {plot_path}")
        logger.info("="*60)
        logger.info("✅ ANOMALY DETECTION COMPLETE")
        logger.info("="*60)
        
        return report

if __name__ == "__main__":
    detector = AnomalyDetector()
    report = detector.detect_anomalies()
    
    print("\n🔍 ANOMALY DETECTION SUMMARY:")
    print(f"   Total samples: {report['total_samples']:,}")
    print(f"   Anomalies: {report['anomalies_detected']} ({report['anomaly_percentage']:.2f}%)")
    print(f"   Detection method: {report['detection_method']}")
