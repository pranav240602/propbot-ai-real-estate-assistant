#!/usr/bin/env python3
"""
PropBot Data Cleaner - Cleans all CSV files at once
Run this script to clean ALL your data files automatically
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json

def clean_all_files():
    """Main function to clean all CSV files"""
    
    print("="*60)
    print("🚀 PROPBOT DATA CLEANER STARTING...")
    print("="*60)
    
    # Setup paths
    raw_data_dir = Path("raw_data")
    cleaned_data_dir = Path("cleaned_data")
    cleaned_data_dir.mkdir(exist_ok=True)
    
    # Get all CSV files
    csv_files = list(raw_data_dir.glob("*.csv"))
    print(f"\n📁 Found {len(csv_files)} CSV files to clean")
    
    # Create a summary report
    cleaning_report = {}
    
    for file_path in csv_files:
        print(f"\n{'='*50}")
        print(f"📄 Processing: {file_path.name}")
        print(f"{'='*50}")
        
        try:
            # Read the file
            df = pd.read_csv(file_path, low_memory=False)
            original_shape = df.shape
            print(f"   Original: {original_shape[0]} rows, {original_shape[1]} columns")
            
            # ========== UNIVERSAL CLEANING STEPS ==========
            
            # 1. Remove complete duplicates
            df = df.drop_duplicates()
            
            # 2. Remove columns that are completely empty
            df = df.dropna(axis=1, how='all')
            
            # 3. Clean string columns (remove extra spaces)
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
                # Replace 'nan' string with actual NaN
                df[col] = df[col].replace('nan', np.nan)
            
            # 4. Add metadata
            df['source_file'] = file_path.name
            df['cleaned_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save cleaned file
            output_path = cleaned_data_dir / f"cleaned_{file_path.name}"
            df.to_csv(output_path, index=False)
            
            # Record in report
            cleaning_report[file_path.name] = {
                'status': 'success',
                'original_rows': original_shape[0],
                'original_cols': original_shape[1],
                'cleaned_rows': df.shape[0],
                'cleaned_cols': df.shape[1],
                'rows_removed': original_shape[0] - df.shape[0]
            }
            
            print(f"   ✅ Cleaned: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"   💾 Saved to: {output_path.name}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            cleaning_report[file_path.name] = {
                'status': 'failed',
                'error': str(e)
            }
    
    # Save cleaning report
    report_path = cleaned_data_dir / "cleaning_report.json"
    with open(report_path, 'w') as f:
        json.dump(cleaning_report, f, indent=2)
    
    print("\n" + "="*60)
    print("📊 CLEANING SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in cleaning_report.values() if r['status'] == 'success')
    failed = sum(1 for r in cleaning_report.values() if r['status'] == 'failed')
    
    print(f"✅ Successfully cleaned: {successful} files")
    print(f"❌ Failed: {failed} files")
    print(f"📄 Report saved to: {report_path}")
    print("\n🎉 CLEANING COMPLETE!")
    
    return cleaning_report

# ========== RUN THE SCRIPT ==========
if __name__ == "__main__":
    clean_all_files()
