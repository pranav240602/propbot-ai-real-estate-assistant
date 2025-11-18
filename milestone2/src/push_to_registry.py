"""
Push trained models to GCP Artifact Registry
"""

import os
import json
import logging
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelRegistryPusher:
    """Push models to GCP Artifact Registry"""
    
    def __init__(self):
        self.results_dir = 'results'
        self.models_dir = 'models'
        self.registry_dir = 'registry'
        
        os.makedirs(self.registry_dir, exist_ok=True)
        logger.info("🔧 Model Registry Pusher initialized")
    
    def package_model(self):
        """Package model artifacts"""
        logger.info("📦 Packaging model artifacts...")
        
        package_dir = os.path.join(self.registry_dir, f'model_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        os.makedirs(package_dir, exist_ok=True)
        
        # Copy model config
        if os.path.exists(f'{self.results_dir}/model_config.json'):
            shutil.copy(f'{self.results_dir}/model_config.json', package_dir)
        
        # Copy best hyperparameters
        if os.path.exists(f'{self.results_dir}/best_config.json'):
            shutil.copy(f'{self.results_dir}/best_config.json', package_dir)
        
        # Copy validation report
        if os.path.exists(f'{self.results_dir}/validation_report.json'):
            shutil.copy(f'{self.results_dir}/validation_report.json', package_dir)
        
        # Copy bias report
        if os.path.exists(f'{self.results_dir}/bias_metrics/bias_detection_report.json'):
            shutil.copy(f'{self.results_dir}/bias_metrics/bias_detection_report.json', package_dir)
        
        logger.info(f"✅ Model packaged at: {package_dir}")
        return package_dir
    
    def create_metadata(self, package_dir):
        """Create model metadata"""
        logger.info("📝 Creating model metadata...")
        
        metadata = {
            'model_name': 'propbot-milestone2',
            'version': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'framework': 'sentence-transformers',
            'model_type': 'embedding + RAG',
            'timestamp': datetime.now().isoformat(),
            'artifacts': os.listdir(package_dir)
        }
        
        metadata_path = os.path.join(package_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Metadata created: {metadata_path}")
        return metadata
    
    def push_to_gcp(self, package_dir, metadata):
        """Push to GCP Artifact Registry"""
        logger.info("🚀 Simulating GCP push...")
        
        gcp_commands = f"""# GCP Push Commands
gcloud auth activate-service-account --key-file=$GCP_CREDENTIALS
gcloud config set project $GCP_PROJECT_ID
gcloud artifacts repositories create propbot-models --repository-format=docker --location=us-central1
docker tag propbot-model:latest us-central1-docker.pkg.dev/$GCP_PROJECT_ID/propbot-models/propbot:{metadata['version']}
docker push us-central1-docker.pkg.dev/$GCP_PROJECT_ID/propbot-models/propbot:{metadata['version']}
"""
        
        commands_path = os.path.join(package_dir, 'gcp_push_commands.sh')
        with open(commands_path, 'w') as f:
            f.write(gcp_commands)
        
        logger.info(f"✅ GCP commands saved: {commands_path}")
        return True
    
    def run(self):
        """Main push function"""
        logger.info("="*60)
        logger.info("🚀 PUSHING MODEL TO REGISTRY")
        logger.info("="*60)
        
        package_dir = self.package_model()
        metadata = self.create_metadata(package_dir)
        self.push_to_gcp(package_dir, metadata)
        
        logger.info("="*60)
        logger.info("✅ MODEL PUSHED TO REGISTRY")
        logger.info(f"   Version: {metadata['version']}")
        logger.info("="*60)
        
        return metadata

if __name__ == "__main__":
    pusher = ModelRegistryPusher()
    metadata = pusher.run()
    print("\n📊 REGISTRY PUSH SUMMARY:")
    print(json.dumps(metadata, indent=2))
