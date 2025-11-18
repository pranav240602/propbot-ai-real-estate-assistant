"""
Model Validation for PropBot
Implements metrics and validation
"""

import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelValidator:
    """Validate model performance"""
    
    def __init__(self):
        self.results_dir = 'results'
        self.cm_dir = os.path.join(self.results_dir, 'confusion_matrices')
        os.makedirs(self.cm_dir, exist_ok=True)
        logger.info("🔧 Model Validator initialized")
    
    def load_validation_data(self):
        """Load validation set"""
        val_path = os.path.join(self.results_dir, 'validation_set.csv')
        
        if not os.path.exists(val_path):
            logger.error(f"❌ Validation set not found: {val_path}")
            return None
        
        df = pd.read_csv(val_path)
        logger.info(f" Loaded validation set: {len(df)} samples")
        return df
    
    def generate_mock_predictions(self, n_samples):
        """Generate mock predictions for testing"""
        # In real scenario, these come from your model
        np.random.seed(42)
        
        # Binary classification example (e.g., property will sell or not)
        y_true = np.random.randint(0, 2, n_samples)
        y_pred = y_true.copy()
        
        # Add some noise (10% error rate)
        noise_indices = np.random.choice(n_samples, size=int(0.1 * n_samples), replace=False)
        y_pred[noise_indices] = 1 - y_pred[noise_indices]
        
        y_prob = np.random.rand(n_samples)
        
        return y_true, y_pred, y_prob
    
    def calculate_metrics(self, y_true, y_pred, y_prob):
        """Calculate all metrics"""
        logger.info("📊 Calculating metrics...")
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='binary'),
            'recall': recall_score(y_true, y_pred, average='binary'),
            'f1_score': f1_score(y_true, y_pred, average='binary'),
            'auc': roc_auc_score(y_true, y_prob)
        }
        
        logger.info(" Metrics calculated:")
        for name, value in metrics.items():
            logger.info(f"   {name}: {value:.4f}")
        
        return metrics
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """Generate confusion matrix plot"""
        logger.info("📈 Generating confusion matrix...")
        
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        cm_path = os.path.join(self.cm_dir, 'confusion_matrix.png')
        plt.savefig(cm_path)
        plt.close()
        
        logger.info(f" Confusion matrix saved: {cm_path}")
        return cm_path
    
    def validate(self):
        """Main validation function"""
        logger.info("="*60)
        logger.info("🚀 STARTING MODEL VALIDATION")
        logger.info("="*60)
        
        # Load validation data
        val_df = self.load_validation_data()
        if val_df is None:
            return None
        
        n_samples = len(val_df)
        
        # Generate predictions (mock for now)
        y_true, y_pred, y_prob = self.generate_mock_predictions(n_samples)
        
        # Calculate metrics
        metrics = self.calculate_metrics(y_true, y_pred, y_prob)
        
        # Generate confusion matrix
        cm_path = self.plot_confusion_matrix(y_true, y_pred)
        
        # Save validation report
        report = {
            'validation_samples': n_samples,
            'metrics': metrics,
            'confusion_matrix_path': cm_path,
            'timestamp': datetime.now().isoformat()
        }
        
        report_path = os.path.join(self.results_dir, 'validation_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f" Validation report saved: {report_path}")
        
        logger.info("="*60)
        logger.info(" MODEL VALIDATION COMPLETE")
        logger.info("="*60)
        
        return report

if __name__ == "__main__":
    validator = ModelValidator()
    report = validator.validate()
    
    if report:
        print("\n📊 VALIDATION RESULTS:")
        print(json.dumps(report['metrics'], indent=2))
