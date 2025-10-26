"""
PropBot - Merge Crime Datasets
Combines 2020, 2021, 2022, and 2023-2025 crime data into complete dataset
Week 2 - Day 1 Task
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import numpy as np

def merge_all_crime_data():
    """
    Merge all crime datasets into one complete 2020-2025 file
    """
    
    print("=" * 80)
    print("PROPBOT: MERGING CRIME DATASETS (2020-2025)")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure output folder
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Files to merge
    crime_files = {
        '2020': 'data/raw/boston_crime_data_2020.csv',
        '2021': 'data/raw/boston_crime_data_2021.csv',
        '2022': 'data/raw/boston_crime_2022.csv',
        '2023-2025': 'data/raw/boston_crime_2023_2025_api_20251024_232735.csv'
    }
    
    all_dataframes = []
    total_before_merge = 0
    
    print("📂 Loading individual crime datasets...\n")
    
    # Load each file
    for period, file_path in crime_files.items():
        if Path(file_path).exists():
            print(f"Loading {period}...")
            df = pd.read_csv(file_path)
            
            # Standardize column names (make uppercase)
            df.columns = df.columns.str.upper()
            
            print(f"  ✅ {period}: {len(df):,} records")
            
            all_dataframes.append(df)
            total_before_merge += len(df)
        else:
            print(f"  ⚠️  {period}: File not found - {file_path}")
    
    # Merge all dataframes
    if len(all_dataframes) > 0:
        print(f"\n🔗 Merging {len(all_dataframes)} datasets...")
        df_merged = pd.concat(all_dataframes, ignore_index=True)
        
        print(f"  ✅ Combined: {len(df_merged):,} total records")
        
        # Remove duplicates based on incident number
        if 'INCIDENT_NUMBER' in df_merged.columns:
            original_count = len(df_merged)
            df_merged = df_merged.drop_duplicates(subset=['INCIDENT_NUMBER'], keep='first')
            duplicates_removed = original_count - len(df_merged)
            print(f"  ✅ Removed {duplicates_removed:,} duplicate incidents")
        
        # Sort by date
        if 'OCCURRED_ON_DATE' in df_merged.columns:
            df_merged['OCCURRED_ON_DATE'] = pd.to_datetime(df_merged['OCCURRED_ON_DATE'], errors='coerce')
            df_merged = df_merged.sort_values('OCCURRED_ON_DATE')
            print(f"  ✅ Sorted by occurrence date")
        
        # Validate year coverage
        if 'YEAR' in df_merged.columns:
            print(f"\n📊 Year coverage after merge:")
            year_counts = df_merged['YEAR'].value_counts().sort_index()
            
            for year, count in year_counts.items():
                if pd.notna(year):
                    print(f"  {int(year)}: {count:,} incidents")
            
            # Check for 2020-2025
            years_present = set(year_counts.index.dropna())
            expected_years = {2020, 2021, 2022, 2023, 2024, 2025}
            
            if expected_years.issubset(years_present):
                print(f"\n  ✅ COMPLETE: All years 2020-2025 present!")
            else:
                missing = expected_years - years_present
                print(f"\n  ⚠️  Missing years: {missing}")
        
        # Save merged dataset
        output_file = f'data/processed/boston_crime_2020_2025_complete_{datetime.now().strftime("%Y%m%d")}.csv'
        
        print(f"\n💾 Saving merged dataset...")
        df_merged.to_csv(output_file, index=False)
        
        file_size_mb = Path(output_file).stat().st_size / (1024 * 1024)
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ MERGE COMPLETE!")
        print("=" * 80)
        print(f"Input files: {len(all_dataframes)}")
        print(f"Records before merge: {total_before_merge:,}")
        print(f"Records after merge: {len(df_merged):,}")
        print(f"Duplicates removed: {total_before_merge - len(df_merged):,}")
        print(f"\nOutput file: {output_file}")
        print(f"File size: {file_size_mb:.2f} MB")
        print(f"Columns: {len(df_merged.columns)}")
        
        # Show column names
        print(f"\n📋 Available columns:")
        for i, col in enumerate(df_merged.columns[:20], 1):
            print(f"  {i}. {col}")
        if len(df_merged.columns) > 20:
            print(f"  ... and {len(df_merged.columns) - 20} more")
        
        # Date range
        if 'OCCURRED_ON_DATE' in df_merged.columns:
            min_date = df_merged['OCCURRED_ON_DATE'].min()
            max_date = df_merged['OCCURRED_ON_DATE'].max()
            print(f"\n📅 Date range: {min_date} to {max_date}")
        
        # Sample
        print(f"\n📋 Sample (first 3 records):")
        print(df_merged.head(3).to_string())
        
        print("\n" + "=" * 80)
        print("🎯 READY FOR NEXT STEP: Calculate Crime Rates!")
        print("=" * 80)
        print("\nNext: python scripts\\calculate_crime_rates.py")
        
        return df_merged
    
    else:
        print("\n❌ No datasets found to merge")
        return None

if __name__ == "__main__":
    print("\n🔗 Merging Crime Datasets (2020-2025)\n")
    
    merged_df = merge_all_crime_data()
    
    if merged_df is not None:
        print(f"\n✅ SUCCESS! Complete crime dataset created")
        print(f"✅ File: data/processed/boston_crime_2020_2025_complete_*.csv")
        print(f"\n🎯 Next: Calculate crime rates and trends")