"""
Experiment Tracking with MLflow
Logs all experiments and results
"""

import os
import mlflow
import mlflow.sklearn
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentTracker:
    """Track experiments with MLflow"""
    
    def __init__(self):
        self.results_dir = 'results'
        self.mlruns_dir = 'mlruns'
        
        # Setup MLflow
        mlflow.set_tracking_uri(f"file:///{os.path.abspath(self.mlruns_dir)}")
        mlflow.set_experiment("PropBot_Milestone2")
        
        logger.info("🔧 MLflow Experiment Tracker initialized")
        logger.info(f"📊 Tracking URI: {mlflow.get_tracking_uri()}")
    
    def log_experiment(self, experiment_name, params, metrics):
        """Log a single experiment"""
        logger.info(f"📝 Logging experiment: {experiment_name}")
        
        with mlflow.start_run(run_name=experiment_name):
            # Log parameters
            for key, value in params.items():
                mlflow.log_param(key, value)
            
            # Log metrics
            for key, value in metrics.items():
                mlflow.log_metric(key, value)
            
            logger.info(f"✅ Experiment logged: {experiment_name}")
    
    def log_all_results(self):
        """Log all results from other scripts"""
        logger.info("="*60)
        logger.info("🚀 LOGGING ALL EXPERIMENTS")
        logger.info("="*60)
        
        experiments_logged = 0
        
        # 1. Log model config
        model_config_path = os.path.join(self.results_dir, 'model_config.json')
        if os.path.exists(model_config_path):
            with open(model_config_path) as f:
                config = json.load(f)
            
            self.log_experiment(
                experiment_name="model_training",
                params={
                    'model_name': config['model_name'],
                    'embedding_dim': config['embedding_dim'],
                    'train_size': config['train_size'],
                    'val_size': config['val_size']
                },
                metrics={
                    'train_samples': config['train_size'],
                    'val_samples': config['val_size']
                }
            )
            experiments_logged += 1
        
        # 2. Log hyperparameter tuning
        tuning_path = os.path.join(self.results_dir, 'hyperparameter_tuning_results.json')
        if os.path.exists(tuning_path):
            with open(tuning_path) as f:
                tuning = json.load(f)
            
            best_config = tuning['best_config']
            
            self.log_experiment(
                experiment_name="hyperparameter_tuning_best",
                params=best_config['config'],
                metrics={'best_score': best_config['score']}
            )
            experiments_logged += 1
        
        # 3. Log validation results
        val_path = os.path.join(self.results_dir, 'validation_report.json')
        if os.path.exists(val_path):
            with open(val_path) as f:
                validation = json.load(f)
            
            self.log_experiment(
                experiment_name="model_validation",
                params={'validation_samples': validation['validation_samples']},
                metrics=validation['metrics']
            )
            experiments_logged += 1
        
        # 4. Log bias detection
        bias_path = os.path.join(self.results_dir, 'bias_metrics', 'bias_detection_report.json')
        if os.path.exists(bias_path):
            with open(bias_path) as f:
                bias = json.load(f)
            
            self.log_experiment(
                experiment_name="bias_detection",
                params={'total_samples': bias['total_samples']},
                metrics={
                    'bias_issues_found': len(bias['bias_findings']),
                    'high_severity_issues': sum(1 for b in bias['bias_findings'] if b['severity'] == 'HIGH')
                }
            )
            experiments_logged += 1
        
        logger.info("="*60)
        logger.info(f"✅ LOGGED {experiments_logged} EXPERIMENTS")
        logger.info("="*60)
        
        return experiments_logged
    
    def view_experiments(self):
        """View all logged experiments"""
        logger.info("📊 Retrieving experiment data...")
        
        experiment = mlflow.get_experiment_by_name("PropBot_Milestone2")
        if experiment:
            runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
            logger.info(f"✅ Found {len(runs)} runs")
            return runs
        else:
            logger.warning("⚠️  No experiments found")
            return None

if __name__ == "__main__":
    tracker = ExperimentTracker()
    
    # Log all results
    count = tracker.log_all_results()
    
    # View experiments
    runs = tracker.view_experiments()
    
    print(f"\n📊 EXPERIMENT TRACKING SUMMARY:")
    print(f"   Total experiments logged: {count}")
    
    if runs is not None and not runs.empty:
        print(f"   Total runs in MLflow: {len(runs)}")
        print(f"\n✅ View experiments:")
        print(f"   mlflow ui --backend-store-uri file:///{os.path.abspath('mlruns')}")
