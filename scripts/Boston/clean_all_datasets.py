"""
PropBot - Clean ALL Datasets
Master script to clean all raw data
Week 2 - Day 1 Complete Task
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import numpy as np

def clean_all_datasets():
    """
    Clean all PropBot datasets
    """
    
    print("=" * 80)
    print("PROPBOT: CLEANING ALL DATASETS")
    print("=" * 80)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    cleaned_files = []
    
    # 1. Clean Crime (all files)
    print("1️⃣  CLEANING CRIME DATA")
    print("─" * 80)
    
    crime_files = [
        'data/raw/boston_crime_data_2020.csv',
        'data/raw/boston_crime_data_2021.csv',
        'data/raw/boston_crime_2022.csv',
        'data/raw/boston_crime_2023_2025_api_20251024_232735.csv'
    ]
    
    crime_dfs = []
    for file in crime_files:
        if Path(file).exists():
            df = pd.read_csv(file)
            df.columns = df.columns.str.upper()
            df = df.drop_duplicates()
            if 'INCIDENT_NUMBER' in df.columns:
                df = df.dropna(subset=['INCIDENT_NUMBER'])
            print(f"✅ {Path(file).name}: {len(df):,} clean records")
            crime_dfs.append(df)
    
    if crime_dfs:
        df_crime = pd.concat(crime_dfs, ignore_index=True)
        if 'INCIDENT_NUMBER' in df_crime.columns:
            df_crime = df_crime.drop_duplicates(subset=['INCIDENT_NUMBER'])
        output = f'data/processed/crime_2020_2025_CLEAN_{datetime.now().strftime("%Y%m%d")}.csv'
        df_crime.to_csv(output, index=False)
        print(f"💾 Merged clean crime: {output}")
        print(f"   Total: {len(df_crime):,} records\n")
        cleaned_files.append(('Crime', len(df_crime)))
    
    # 2. Clean Demographics
    print("2️⃣  CLEANING DEMOGRAPHICS")
    print("─" * 80)
    
    demo_file = 'data/raw/boston_demographics_20251024_180101.csv'
    if Path(demo_file).exists():
        df = pd.read_csv(demo_file)
        # Remove invalid ZIP
        df = df[df['zip_code'] != '02203']
        # Remove negative values
        numeric_cols = ['total_population', 'median_household_income']
        for col in numeric_cols:
            if col in df.columns:
                df = df[df[col] >= 0]
        output = f'data/processed/demographics_CLEAN_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(output, index=False)
        print(f"✅ Demographics: {len(df)} ZIP codes")
        print(f"💾 Saved: {output}\n")
        cleaned_files.append(('Demographics', len(df)))
    
    # 3. Clean Properties
    print("3️⃣  CLEANING PROPERTIES")
    print("─" * 80)
    
    prop_file = 'data/raw/boston_properties_20251024_185711.csv'
    if Path(prop_file).exists():
        df = pd.read_csv(prop_file)
        original = len(df)
        
        # Remove duplicates
        if 'PID' in df.columns or 'property_id' in df.columns:
            id_col = 'PID' if 'PID' in df.columns else 'property_id'
            df = df.drop_duplicates(subset=[id_col])
        
        # Remove properties with no address
        if 'ST_NUM' in df.columns and 'ST_NAME' in df.columns:
            df = df.dropna(subset=['ST_NUM', 'ST_NAME'])
        
        # Convert numeric columns
        numeric_cols = ['AV_TOTAL', 'R_BDRMS', 'R_FULL_BTH', 'LIVING_AREA', 'YR_BUILT']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove properties with invalid values
        if 'AV_TOTAL' in df.columns:
            df = df[df['AV_TOTAL'] > 0]  # Value must be positive
        
        if 'YR_BUILT' in df.columns:
            df = df[(df['YR_BUILT'] >= 1650) & (df['YR_BUILT'] <= 2025)]  # Reasonable years
        
        output = f'data/processed/properties_CLEAN_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(output, index=False)
        print(f"✅ Properties: {len(df):,} (removed {original - len(df):,})")
        print(f"💾 Saved: {output}\n")
        cleaned_files.append(('Properties', len(df)))
    
    # 4. Clean Transit
    print("4️⃣  CLEANING TRANSIT")
    print("─" * 80)
    
    transit_file = 'data/raw/mbta_stations_20251024_181839.csv'
    if Path(transit_file).exists():
        df = pd.read_csv(transit_file)
        original = len(df)
        
        # Remove duplicates
        if 'station_id' in df.columns:
            df = df.drop_duplicates(subset=['station_id'])
        
        # Remove entries without coordinates
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df = df.dropna(subset=['latitude', 'longitude'])
        
        # Filter to actual stations (location_type == 1 or 0)
        if 'location_type' in df.columns:
            df = df[df['location_type'].isin([0, 1])]
        
        output = f'data/processed/transit_CLEAN_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(output, index=False)
        print(f"✅ Transit: {len(df)} stations (removed {original - len(df)})")
        print(f"💾 Saved: {output}\n")
        cleaned_files.append(('Transit', len(df)))
    
    # 5. Clean Amenities
    print("5️⃣  CLEANING AMENITIES")
    print("─" * 80)
    
    yelp_file = 'data/raw/yelp_businesses_20251024_185237.csv'
    if Path(yelp_file).exists():
        df = pd.read_csv(yelp_file)
        original = len(df)
        
        # Remove duplicates
        if 'business_id' in df.columns:
            df = df.drop_duplicates(subset=['business_id'])
        
        # Remove closed businesses
        if 'is_closed' in df.columns:
            df = df[df['is_closed'] == False]
        
        # Remove businesses without coordinates
        if 'latitude' in df.columns and 'longitude' in df.columns:
            df = df.dropna(subset=['latitude', 'longitude'])
        
        output = f'data/processed/amenities_CLEAN_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(output, index=False)
        print(f"✅ Amenities: {len(df):,} businesses (removed {original - len(df):,})")
        print(f"💾 Saved: {output}\n")
        cleaned_files.append(('Amenities', len(df)))
    
    # Final summary
    print("=" * 80)
    print("✅ ALL DATASETS CLEANED!")
    print("=" * 80)
    
    for dataset, count in cleaned_files:
        print(f"  ✅ {dataset}: {count:,} clean records")
    
    print(f"\n📁 All clean files in: data/processed/")
    
    print("\n" + "=" * 80)
    print("🎯 NEXT STEPS:")
    print("=" * 80)
    print("1. Calculate crime rates: python scripts\\calculate_crime_rates.py")
    print("2. Generate trends: python scripts\\generate_crime_trends.py")
    print("3. Calculate distances: python scripts\\calculate_distances.py")
    print("=" * 80)
    
    return cleaned_files

if __name__ == "__main__":
    results = clean_all_datasets()
    
    if results:
        print(f"\n✅ All {len(results)} datasets cleaned successfully!")