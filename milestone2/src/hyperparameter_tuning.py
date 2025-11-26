"""
Hyperparameter Tuning for PropBot
Tests different RAG configurations
"""

import os
import json
import logging
from itertools import product
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HyperparameterTuner:
    """Tune RAG hyperparameters"""
    
    def __init__(self):
        self.results_dir = 'results'
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Search space
        self.search_space = {
            'chunk_size': [256, 512, 1024],
            'chunk_overlap': [0, 50, 100],
            'top_k': [3, 5, 10],
            'temperature': [0.1, 0.5, 0.7, 1.0]
        }
        
        logger.info(" Hyperparameter Tuner initialized")
        logger.info(f" Search space: {self.search_space}")
    
    def calculate_combinations(self):
        """Calculate total combinations"""
        total = 1
        for key, values in self.search_space.items():
            total *= len(values)
        return total
    
    def run_tuning(self):
        """Run hyperparameter search"""
        logger.info("="*60)
        logger.info(" STARTING HYPERPARAMETER TUNING")
        logger.info("="*60)
        
        total_combinations = self.calculate_combinations()
        logger.info(f" Total combinations to test: {total_combinations}")
        
        results = []
        
        # Generate all combinations
        keys = list(self.search_space.keys())
        values = [self.search_space[k] for k in keys]
        
        for idx, combo in enumerate(product(*values), 1):
            config = dict(zip(keys, combo))
            
            # Simulate evaluation
            score = self._evaluate_config(config)
            
            result = {
                'experiment_id': idx,
                'config': config,
                'score': score,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            
            logger.info(f" Experiment {idx}/{total_combinations}: Score = {score:.4f}")
        
        # Find best config
        best_result = max(results, key=lambda x: x['score'])
        
        logger.info("="*60)
        logger.info(" BEST CONFIGURATION FOUND")
        logger.info(f"   Config: {best_result['config']}")
        logger.info(f"   Score: {best_result['score']:.4f}")
        logger.info("="*60)
        
        # Save all results
        results_path = os.path.join(self.results_dir, 'hyperparameter_tuning_results.json')
        with open(results_path, 'w') as f:
            json.dump({
                'search_space': self.search_space,
                'total_experiments': len(results),
                'all_results': results,
                'best_config': best_result
            }, f, indent=2)
        
        logger.info(f" Results saved to {results_path}")
        
        # Save best config separately
        best_config_path = os.path.join(self.results_dir, 'best_config.json')
        with open(best_config_path, 'w') as f:
            json.dump(best_result['config'], f, indent=2)
        
        return best_result
    
    def _evaluate_config(self, config):
        """Evaluate a configuration (mock implementation)"""
        score = 0.0
        
        # Prefer moderate chunk sizes
        if config['chunk_size'] == 512:
            score += 0.3
        elif config['chunk_size'] == 1024:
            score += 0.2
        else:
            score += 0.1
        
        # Prefer some overlap
        if config['chunk_overlap'] == 50:
            score += 0.25
        elif config['chunk_overlap'] == 100:
            score += 0.15
        
        # Prefer moderate top_k
        if config['top_k'] == 5:
            score += 0.25
        elif config['top_k'] == 3:
            score += 0.2
        
        # Prefer moderate temperature
        if config['temperature'] == 0.7:
            score += 0.2
        elif config['temperature'] == 0.5:
            score += 0.15
        
        return score

if __name__ == "__main__":
    tuner = HyperparameterTuner()
    best = tuner.run_tuning()
    
    print("\n BEST HYPERPARAMETERS:")
    print(json.dumps(best['config'], indent=2))
