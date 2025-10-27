"""
Bias Detection Module for PropBot Data Pipeline
Performs data slicing to detect bias across different subgroups
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
        logging.FileHandler('logs/bias_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BiasDetector:
    """Detect bias in PropBot datasets through data slicing"""
    
    def __init__(self, data_dir='data/processed/Boston'):
        self.data_dir = data_dir
        self.bias_findings = []
        
    def analyze_price_distribution(self, df, slice_column, slice_name):
        """Analyze price distribution across different slices"""
        logger.info(f"\nAnalyzing price distribution by {slice_name}...")
        
        if 'price' not in df.columns or slice_column not in df.columns:
            logger.warning(f"⚠️  Cannot analyze - missing columns")
            return
        
        # Group by slice and calculate statistics
        stats = df.groupby(slice_column)['price'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ]).round(2)
        
        logger.info(f"\nPrice Statistics by {slice_name}:")
        logger.info(f"\n{stats}")
        
        # Calculate coefficient of variation to detect bias
        cv = (stats['std'] / stats['mean'] * 100).round(2)
        
        # Flag high variation as potential bias
        high_variation = cv[cv > 50]  # CV > 50% considered high
        if len(high_variation) > 0:
            logger.warning(f"⚠️  High price variation detected:")
            for idx, val in high_variation.items():
                logger.warning(f"   {idx}: CV = {val}%")
                self.bias_findings.append({
                    'type': 'price_variation',
                    'slice': slice_name,
                    'value': str(idx),
                    'cv': float(val),
                    'mean_price': float(stats.loc[idx, 'mean'])
                })
        
        # Check for significant mean differences
        overall_mean = df['price'].mean()
        for idx, row in stats.iterrows():
            diff_pct = abs((row['mean'] - overall_mean) / overall_mean * 100)
            if diff_pct > 30:  # More than 30% difference
                logger.warning(f"⚠️  {idx}: {diff_pct:.1f}% deviation from mean")
                self.bias_findings.append({
                    'type': 'price_bias',
                    'slice': slice_name,
                    'value': str(idx),
                    'deviation_pct': float(diff_pct),
                    'slice_mean': float(row['mean']),
                    'overall_mean': float(overall_mean)
                })
        
        return stats
    
    def analyze_data_coverage(self, df, slice_column, slice_name):
        """Analyze data coverage across slices"""
        logger.info(f"\nAnalyzing data coverage by {slice_name}...")
        
        if slice_column not in df.columns:
            logger.warning(f"⚠️  Column {slice_column} not found")
            return
        
        coverage = df[slice_column].value_counts()
        coverage_pct = (coverage / len(df) * 100).round(2)
        
        logger.info(f"\nData Coverage by {slice_name}:")
        for idx, count in coverage.items():
            pct = coverage_pct[idx]
            logger.info(f"  {idx}: {count} ({pct}%)")
        
        # Flag underrepresented groups (< 5%)
        underrepresented = coverage_pct[coverage_pct < 5]
        if len(underrepresented) > 0:
            logger.warning(f"⚠️  Underrepresented groups detected:")
            for idx, pct in underrepresented.items():
                logger.warning(f"   {idx}: only {pct}% of data")
                self.bias_findings.append({
                    'type': 'underrepresentation',
                    'slice': slice_name,
                    'value': str(idx),
                    'percentage': float(pct),
                    'count': int(coverage[idx])
                })
        
        return coverage
    
    def analyze_missing_data_bias(self, df, slice_column, slice_name):
        """Check if missing data is biased toward certain slices"""
        logger.info(f"\nAnalyzing missing data patterns by {slice_name}...")
        
        if slice_column not in df.columns:
            return
        
        # Calculate missing percentage for each slice
        for col in df.columns:
            if col == slice_column:
                continue
            
            missing_by_slice = df.groupby(slice_column)[col].apply(
                lambda x: x.isnull().sum() / len(x) * 100
            ).round(2)
            
            # Flag if any slice has > 10% more missing than overall
            overall_missing = df[col].isnull().sum() / len(df) * 100
            
            for idx, pct in missing_by_slice.items():
                if pct > overall_missing + 10:
                    logger.warning(f"⚠️  {col} missing in {idx}: {pct}% (overall: {overall_missing:.1f}%)")
                    self.bias_findings.append({
                        'type': 'missing_data_bias',
                        'slice': slice_name,
                        'value': str(idx),
                        'column': col,
                        'missing_pct': float(pct),
                        'overall_missing_pct': float(overall_missing)
                    })
    
    def analyze_properties(self):
        """Analyze properties dataset for bias"""
        logger.info("\n" + "="*60)
        logger.info("ANALYZING PROPERTIES DATA")
        logger.info("="*60)
        
        filepath = os.path.join(self.data_dir, 'properties_CLEAN_20251025.csv')
        
        if not os.path.exists(filepath):
            logger.warning(f"⚠️  Properties file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} properties")
        
        # Analyze by neighborhood (if column exists)
        if 'neighborhood' in df.columns:
            self.analyze_data_coverage(df, 'neighborhood', 'Neighborhood')
            self.analyze_price_distribution(df, 'neighborhood', 'Neighborhood')
            self.analyze_missing_data_bias(df, 'neighborhood', 'Neighborhood')
        
        # Analyze by price ranges
        if 'price' in df.columns:
            df['price_range'] = pd.cut(df['price'], 
                                       bins=[0, 300000, 500000, 750000, 1000000, float('inf')],
                                       labels=['<300K', '300-500K', '500-750K', '750K-1M', '>1M'])
            self.analyze_data_coverage(df, 'price_range', 'Price Range')
    
    def analyze_crime(self):
        """Analyze crime dataset for bias"""
        logger.info("\n" + "="*60)
        logger.info("ANALYZING CRIME DATA")
        logger.info("="*60)
        
        filepath = os.path.join(self.data_dir, 'crime_2020_2025_CLEAN_20251025.csv')
        
        if not os.path.exists(filepath):
            logger.warning(f"⚠️  Crime file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} crime records")
        
        # Analyze by district
        if 'DISTRICT' in df.columns:
            self.analyze_data_coverage(df, 'DISTRICT', 'District')
        
        # Analyze by offense type
        if 'OFFENSE_DESCRIPTION' in df.columns:
            coverage = df['OFFENSE_DESCRIPTION'].value_counts().head(10)
            logger.info(f"\nTop 10 Crime Types:")
            for offense, count in coverage.items():
                logger.info(f"  {offense}: {count}")
    
    def analyze_demographics(self):
        """Analyze demographics dataset for bias"""
        logger.info("\n" + "="*60)
        logger.info("ANALYZING DEMOGRAPHICS DATA")
        logger.info("="*60)
        
        filepath = os.path.join(self.data_dir, 'demographics_CLEAN_20251025.csv')
        
        if not os.path.exists(filepath):
            logger.warning(f"⚠️  Demographics file not found: {filepath}")
            return
        
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} demographic records")
        
        # Analyze coverage by neighborhood
        if 'neighborhood' in df.columns or 'Neighborhood' in df.columns:
            col = 'neighborhood' if 'neighborhood' in df.columns else 'Neighborhood'
            self.analyze_data_coverage(df, col, 'Neighborhood')
    
    def generate_report(self):
        """Generate bias detection summary report"""
        logger.info("\n" + "="*60)
        logger.info("BIAS DETECTION SUMMARY")
        logger.info("="*60)
        
        logger.info(f"Total bias findings: {len(self.bias_findings)}")
        
        # Group findings by type
        by_type = {}
        for finding in self.bias_findings:
            ftype = finding['type']
            by_type[ftype] = by_type.get(ftype, 0) + 1
        
        logger.info("\nFindings by type:")
        for ftype, count in by_type.items():
            logger.info(f"  {ftype}: {count}")
        
        if len(self.bias_findings) > 0:
            logger.warning("\n⚠️  BIAS DETECTED: Review findings above")
            logger.info("\nMitigation recommendations:")
            logger.info("1. Balance data collection across all neighborhoods")
            logger.info("2. Ensure adequate representation of all price ranges")
            logger.info("3. Address missing data patterns in underrepresented groups")
        else:
            logger.info("\n✅ No significant bias detected!")
        
        # Save report
        report_path = 'logs/bias_detection_report.txt'
        with open(report_path, 'w') as f:
            f.write(f"Bias Detection Report - {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            f.write(f"Total findings: {len(self.bias_findings)}\n\n")
            for finding in self.bias_findings:
                f.write(f"{finding}\n")
        logger.info(f"\nReport saved to {report_path}")
    
    def run_analysis(self):
        """Run complete bias detection analysis"""
        logger.info("\n" + "="*60)
        logger.info("STARTING BIAS DETECTION")
        logger.info("="*60)
        
        self.analyze_properties()
        self.analyze_crime()
        self.analyze_demographics()
        self.generate_report()

def main():
    """Main function"""
    detector = BiasDetector()
    detector.run_analysis()

if __name__ == "__main__":
    main()
