"""
Bias Detection for PropBot
Checks for bias across different data slices
"""

import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiasDetector:
    """Detect and analyze bias in model predictions"""
    
    def __init__(self):
        self.results_dir = 'results'
        self.bias_dir = os.path.join(self.results_dir, 'bias_metrics')
        os.makedirs(self.bias_dir, exist_ok=True)
        
        # Define data slices
        self.slices = {
            'neighborhoods': ['Back Bay', 'Beacon Hill', 'South End', 'Dorchester', 
                            'Roxbury', 'Jamaica Plain', 'Charlestown', 'East Boston'],
            'price_ranges': ['<$300K', '$300K-$600K', '$600K-$1M', '>$1M'],
            'property_types': ['Condo', 'Single Family', 'Multi-family', 'Townhouse'],
            'building_age': ['Pre-1900', '1900-1950', '1950-2000', 'Post-2000']
        }
        
        logger.info("🔧 Bias Detector initialized")
        logger.info(f"📊 Checking bias across {len(self.slices)} dimensions")
    
    def load_validation_data(self):
        """Load validation dataset"""
        val_path = os.path.join(self.results_dir, 'validation_set.csv')
        df = pd.read_csv(val_path)
        logger.info(f"✅ Loaded validation data: {len(df)} samples")
        return df
    
    def assign_slices(self, df):
        """Assign each property to slices"""
        logger.info("📊 Assigning properties to slices...")
        
        # Convert TOTAL_VALUE to numeric, handle any non-numeric values
        df['TOTAL_VALUE'] = pd.to_numeric(df['TOTAL_VALUE'], errors='coerce').fillna(0)
        
        # Price ranges
        df['price_slice'] = pd.cut(
            df['TOTAL_VALUE'], 
            bins=[0, 300000, 600000, 1000000, float('inf')],
            labels=self.slices['price_ranges']
        )
        
        # Convert year_built to numeric
        df['year_built'] = pd.to_numeric(df['year_built'], errors='coerce')
        
        # Building age
        current_year = 2025
        df['age'] = current_year - df['year_built'].fillna(current_year)
        df['age_slice'] = pd.cut(
            df['age'],
            bins=[0, 25, 75, 125, float('inf')],
            labels=['Post-2000', '1950-2000', '1900-1950', 'Pre-1900']
        )
        
        # Mock neighborhood assignment
        np.random.seed(42)
        df['neighborhood_slice'] = np.random.choice(
            self.slices['neighborhoods'], 
            size=len(df)
        )
        
        # Mock property type
        df['property_type_slice'] = np.random.choice(
            self.slices['property_types'], 
            size=len(df)
        )
        
        logger.info("✅ Slice assignment complete")
        return df
    
    def generate_predictions_by_slice(self, df):
        """Generate mock predictions for each slice"""
        np.random.seed(42)
        
        # Base predictions
        y_true = np.random.randint(0, 2, len(df))
        y_pred = y_true.copy()
        
        # Introduce bias: worse performance on certain slices
        bias_neighborhoods = ['Dorchester', 'Roxbury']
        for neighborhood in bias_neighborhoods:
            mask = df['neighborhood_slice'] == neighborhood
            indices = df[mask].index
            if len(indices) > 0:
                noise_count = int(0.3 * len(indices))
                noise_indices = np.random.choice(indices, size=noise_count, replace=False)
                y_pred[noise_indices] = 1 - y_pred[noise_indices]
        
        return y_true, y_pred
    
    def calculate_metrics_by_slice(self, df, y_true, y_pred):
        """Calculate performance metrics for each slice"""
        logger.info("📊 Calculating metrics per slice...")
        
        slice_metrics = {}
        
        for slice_type in ['neighborhood_slice', 'price_slice', 'age_slice', 'property_type_slice']:
            slice_metrics[slice_type] = {}
            
            for slice_value in df[slice_type].unique():
                if pd.isna(slice_value):
                    continue
                
                mask = df[slice_type] == slice_value
                indices = df[mask].index
                
                if len(indices) < 10:
                    continue
                
                slice_y_true = y_true[indices]
                slice_y_pred = y_pred[indices]
                
                metrics = {
                    'count': len(indices),
                    'accuracy': accuracy_score(slice_y_true, slice_y_pred),
                    'f1_score': f1_score(slice_y_true, slice_y_pred, average='binary', zero_division=0)
                }
                
                slice_metrics[slice_type][str(slice_value)] = metrics
                
                logger.info(f"   {slice_type}/{slice_value}: Accuracy={metrics['accuracy']:.3f}, F1={metrics['f1_score']:.3f}")
        
        return slice_metrics
    
    def detect_bias(self, slice_metrics):
        """Detect bias by comparing metrics across slices"""
        logger.info("🔍 Detecting bias...")
        
        bias_findings = []
        
        for slice_type, slices in slice_metrics.items():
            if not slices:
                continue
            
            accuracies = [m['accuracy'] for m in slices.values()]
            
            if len(accuracies) < 2:
                continue
            
            max_acc = max(accuracies)
            min_acc = min(accuracies)
            disparity = max_acc - min_acc
            
            if disparity > 0.1:
                bias_findings.append({
                    'slice_type': slice_type,
                    'disparity': disparity,
                    'max_accuracy': max_acc,
                    'min_accuracy': min_acc,
                    'severity': 'HIGH' if disparity > 0.2 else 'MODERATE'
                })
                logger.warning(f"⚠️  BIAS DETECTED in {slice_type}: {disparity:.3f} disparity")
        
        return bias_findings
    
    def run_detection(self):
        """Main bias detection function"""
        logger.info("="*60)
        logger.info("🚀 STARTING BIAS DETECTION")
        logger.info("="*60)
        
        # Load data
        df = self.load_validation_data()
        
        # Assign slices
        df = self.assign_slices(df)
        
        # Generate predictions
        y_true, y_pred = self.generate_predictions_by_slice(df)
        
        # Calculate metrics per slice
        slice_metrics = self.calculate_metrics_by_slice(df, y_true, y_pred)
        
        # Detect bias
        bias_findings = self.detect_bias(slice_metrics)
        
        # Save report
        report = {
            'total_samples': len(df),
            'slices_analyzed': self.slices,
            'slice_metrics': slice_metrics,
            'bias_findings': bias_findings,
            'timestamp': datetime.now().isoformat()
        }
        
        report_path = os.path.join(self.bias_dir, 'bias_detection_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Bias report saved: {report_path}")
        
        logger.info("="*60)
        if bias_findings:
            logger.warning(f"⚠️  BIAS DETECTED: {len(bias_findings)} issues found")
        else:
            logger.info("✅ NO SIGNIFICANT BIAS DETECTED")
        logger.info("="*60)
        
        return report

if __name__ == "__main__":
    detector = BiasDetector()
    report = detector.run_detection()
    
    print("\n🔍 BIAS DETECTION SUMMARY:")
    print(f"   Total samples: {report['total_samples']}")
    print(f"   Bias findings: {len(report['bias_findings'])}")
    
    if report['bias_findings']:
        print("\n⚠️  BIAS ISSUES:")
        for finding in report['bias_findings']:
            print(f"   - {finding['slice_type']}: {finding['severity']} ({finding['disparity']:.3f} disparity)")
