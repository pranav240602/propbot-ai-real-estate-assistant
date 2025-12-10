"""
SHAP Analysis for Feature Importance
"""

import os
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SHAPAnalyzer:
    """SHAP-based sensitivity analysis"""
    
    def __init__(self):
        self.results_dir = 'results'
        self.sensitivity_dir = os.path.join(self.results_dir, 'sensitivity_analysis')
        os.makedirs(self.sensitivity_dir, exist_ok=True)
        logger.info("🔧 SHAP Analyzer initialized")
    
    def load_data(self):
        """Load validation data for analysis"""
        val_path = os.path.join(self.results_dir, 'validation_set.csv')
        df = pd.read_csv(val_path)
        logger.info(f"✅ Loaded {len(df)} samples")
        return df
    
    def prepare_features(self, df):
        """Prepare numeric features for SHAP"""
        numeric_cols = ['TOTAL_VALUE', 'year_built', 'gross_square_feet', 
                       'living_square_feet', 'BED_RMS', 'FULL_BTH']
        
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        X = df[available_cols].copy()
        
        # Clean TOTAL_VALUE - remove commas
        if 'TOTAL_VALUE' in X.columns:
            X['TOTAL_VALUE'] = X['TOTAL_VALUE'].astype(str).str.replace(',', '')
            X['TOTAL_VALUE'] = pd.to_numeric(X['TOTAL_VALUE'], errors='coerce')
        
        # Clean other numeric columns
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce')
        
        # Fill NaN with mean
        X = X.fillna(X.mean())
        
        logger.info(f"✅ Prepared {len(available_cols)} features")
        return X, available_cols
    
    def run_shap_analysis(self):
        """Run SHAP analysis"""
        logger.info("="*60)
        logger.info("🚀 STARTING SHAP ANALYSIS")
        logger.info("="*60)
        
        df = self.load_data()
        X, feature_names = self.prepare_features(df)
        
        sample_size = min(100, len(X))
        X_sample = X.sample(n=sample_size, random_state=42)
        
        logger.info(f"📊 Analyzing {sample_size} samples...")
        
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=10, random_state=42, max_depth=5)
        
        y = X_sample['TOTAL_VALUE'] if 'TOTAL_VALUE' in X_sample.columns else X_sample.iloc[:, 0]
        model.fit(X_sample, y)
        
        logger.info("🔄 Creating SHAP explainer...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_sample, show=False)
        plot_path = os.path.join(self.sensitivity_dir, 'shap_summary.png')
        plt.savefig(plot_path, bbox_inches='tight', dpi=150)
        plt.close()
        logger.info(f"✅ SHAP plot saved: {plot_path}")
        
        feature_importance = np.abs(shap_values).mean(axis=0)
        importance_dict = dict(zip(feature_names, feature_importance.tolist()))
        sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        logger.info("📊 Feature Importance (SHAP):")
        for feature, importance in sorted_importance.items():
            logger.info(f"   {feature}: {importance:.4f}")
        
        report = {
            'method': 'SHAP',
            'samples_analyzed': sample_size,
            'features': feature_names,
            'feature_importance': sorted_importance,
            'plot_path': plot_path,
            'timestamp': datetime.now().isoformat()
        }
        
        report_path = os.path.join(self.sensitivity_dir, 'shap_analysis.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ SHAP report saved: {report_path}")
        logger.info("="*60)
        logger.info("✅ SHAP ANALYSIS COMPLETE")
        logger.info("="*60)
        
        return report

if __name__ == "__main__":
    analyzer = SHAPAnalyzer()
    report = analyzer.run_shap_analysis()
    
    print("\n📊 TOP 3 MOST IMPORTANT FEATURES:")
    top_features = list(report['feature_importance'].items())[:3]
    for feature, importance in top_features:
        print(f"   {feature}: {importance:.4f}")
