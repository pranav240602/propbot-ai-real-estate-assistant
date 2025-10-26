"""
Boston Property Data Extraction Pipeline
For MLOps Course Project - PropBot
This code extracts 30,000+ Boston property records from official sources
Author: Priyanka (corrected by Dhanush)
"""

import pandas as pd
import requests
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path

class BostonPropertyDataPipeline:
    """
    Main class to extract Boston property data
    Gets data from Boston's official open data portal
    """
    
    def __init__(self):  # ✅ FIXED: Double underscores!
        """
        Initialize the pipeline with API endpoints and configuration
        """
        
        # Base URL for Boston's open data API
        self.base_api_url = "https://data.boston.gov/api/3/action/datastore_search"
        
        # SQL endpoint for complex queries
        self.sql_api_url = "https://data.boston.gov/api/3/action/datastore_search_sql"
        
        # Resource ID for Boston Property Assessment FY2024 dataset
        self.property_dataset_id = "4b99718b-d064-471b-9b24-517ae5effecc"
        
        # All Boston ZIP codes (31 total)
        self.boston_zip_codes = [
            '02108', '02109', '02110', '02111', '02113', '02114', '02115',
            '02116', '02118', '02119', '02120', '02121', '02122', '02124',
            '02125', '02126', '02127', '02128', '02129', '02130', '02131',
            '02132', '02134', '02135', '02136', '02163', '02199', '02210',
            '02211', '02215', '02467'
        ]
        
        # Boston neighborhoods
        self.boston_neighborhoods = [
            'Allston', 'Back Bay', 'Bay Village', 'Beacon Hill', 'Brighton',
            'Charlestown', 'Chinatown', 'Dorchester', 'Downtown', 'East Boston',
            'Fenway', 'Hyde Park', 'Jamaica Plain', 'Mattapan', 'Mission Hill',
            'North End', 'Roslindale', 'Roxbury', 'South Boston', 'South End',
            'West End', 'West Roxbury'
        ]
        
        # Ensure output folder exists
        Path('data/raw').mkdir(parents=True, exist_ok=True)
        
        print("=" * 70)
        print("Boston Property Data Pipeline Initialized")
        print("=" * 70)
    
    def fetch_property_data(self, limit=30000):
        """
        Main method to fetch Boston property data
        """
        
        print(f"\n🏠 Fetching up to {limit:,} Boston property records...")
        print(f"📡 Source: Boston Open Data Portal API")
        print(f"🎯 Dataset: Property Assessment FY2024\n")
        
        all_records = []
        offset = 0
        batch_size = 2000
        
        while len(all_records) < limit:
            params = {
                'resource_id': self.property_dataset_id,
                'limit': batch_size,
                'offset': offset
            }
            
            try:
                print(f"📥 Batch {offset//batch_size + 1}: offset={offset:,}, size={batch_size}")
                response = requests.get(self.base_api_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success', False):
                        records = data.get('result', {}).get('records', [])
                        
                        if not records:
                            print("  ✅ No more records available")
                            break
                        
                        all_records.extend(records)
                        print(f"  ✅ Got {len(records):,} records. Total: {len(all_records):,}")
                        
                        offset += batch_size
                    else:
                        print(f"  ❌ API error: {data.get('error', 'Unknown')}")
                        break
                        
                else:
                    print(f"  ❌ HTTP {response.status_code}")
                    break
                
                time.sleep(0.5)
                
            except requests.exceptions.Timeout:
                print("  ⏰ Timeout, retrying...")
                time.sleep(2)
                continue
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                break
        
        print(f"\n✅ Fetched {len(all_records):,} total records")
        df = pd.DataFrame(all_records)
        
        return df
    
    def clean_property_data(self, df):
        """Clean and standardize property data"""
        
        print("\n🧹 Cleaning property data...")
        
        if df.empty:
            return df
        
        # Column mapping
        column_mapping = {
            'PID': 'property_id',
            'ST_NUM': 'street_number',
            'ST_NAME': 'street_name',
            'ST_NAME_SUF': 'street_suffix',
            'UNIT_NUM': 'unit_number',
            'ZIPCODE': 'zip_code',
            'PTYPE': 'property_type_code',
            'LU': 'land_use_code',
            'OWN_OCC': 'owner_occupied',
            'OWNER': 'owner_name',
            'AV_LAND': 'land_value',
            'AV_BLDG': 'building_value',
            'AV_TOTAL': 'total_assessed_value',
            'GROSS_TAX': 'property_tax',
            'YR_BUILT': 'year_built',
            'YR_REMOD': 'year_remodeled',
            'GROSS_AREA': 'gross_square_feet',
            'LIVING_AREA': 'living_square_feet',
            'NUM_FLOORS': 'number_of_floors',
            'R_BDRMS': 'bedrooms',
            'R_FULL_BTH': 'full_bathrooms',
            'R_HALF_BTH': 'half_bathrooms',
            'R_KITCH': 'kitchens'
        }
        
        # Rename columns
        for old, new in column_mapping.items():
            if old in df.columns:
                df.rename(columns={old: new}, inplace=True)
        
        # Convert to numeric
        numeric_cols = ['land_value', 'building_value', 'total_assessed_value',
                       'bedrooms', 'full_bathrooms', 'year_built', 'living_square_feet']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create full address
        if 'street_number' in df.columns and 'street_name' in df.columns:
            df['full_address'] = (
                df['street_number'].astype(str) + ' ' + 
                df['street_name'].astype(str) + ', Boston, MA ' + 
                df['zip_code'].astype(str)
            )
        
        df['city'] = 'Boston'
        df['state'] = 'MA'
        
        # Property type mapping
        property_types = {
            'R1': 'Single Family', 'R2': 'Two Family', 'R3': 'Three Family',
            'R4': 'Four+ Family', 'CD': 'Condo', 'CM': 'Commercial',
            'A': 'Apartment', 'C': 'Commercial'
        }
        
        if 'property_type_code' in df.columns:
            df['property_type'] = df['property_type_code'].map(property_types).fillna('Other')
        
        # Remove duplicates
        if 'property_id' in df.columns:
            original = len(df)
            df = df.drop_duplicates(subset=['property_id'])
            print(f"  ✅ Removed {original - len(df):,} duplicates")
        
        # Filter to Boston ZIPs only
        if 'zip_code' in df.columns:
            df = df[df['zip_code'].astype(str).isin(self.boston_zip_codes)]
        
        df['data_extracted_date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"  ✅ Cleaned! {len(df):,} records, {len(df.columns)} columns")
        
        return df
    
    def run_full_pipeline(self, num_records=30000):
        """Run complete pipeline"""
        
        print("\n" + "=" * 70)
        print("BOSTON PROPERTY DATA EXTRACTION PIPELINE")
        print("=" * 70)
        print(f"Target: {num_records:,} records")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Fetch
        df = self.fetch_property_data(limit=num_records)
        
        if df.empty:
            print("\n❌ No data fetched")
            return df
        
        # Clean
        df = self.clean_property_data(df)
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'data/raw/boston_properties_{timestamp}.csv'
        
        print(f"\n💾 Saving to: {output_file}")
        df.to_csv(output_file, index=False)
        
        file_size_mb = Path(output_file).stat().st_size / (1024 * 1024)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"Records: {len(df):,}")
        print(f"File: {output_file}")
        print(f"Size: {file_size_mb:.2f} MB")
        
        if 'zip_code' in df.columns:
            print(f"\n📊 Top 5 ZIP codes:")
            for zip_code, count in df['zip_code'].value_counts().head().items():
                print(f"  {zip_code}: {count:,}")
        
        if 'property_type' in df.columns:
            print(f"\n🏠 Property types:")
            for ptype, count in df['property_type'].value_counts().head().items():
                print(f"  {ptype}: {count:,}")
        
        if 'total_assessed_value' in df.columns:
            print(f"\n💰 Value stats:")
            print(f"  Mean: ${df['total_assessed_value'].mean():,.0f}")
            print(f"  Median: ${df['total_assessed_value'].median():,.0f}")
        
        print("=" * 70)
        
        return df


if __name__ == "__main__":  # ✅ FIXED: Double underscores!
    """Main execution"""
    
    print("\n🚀 Starting Boston Property Data Collection via API\n")
    
    # Create pipeline
    pipeline = BostonPropertyDataPipeline()
    
    # Run it!
    properties = pipeline.run_full_pipeline(num_records=30000)
    
    if not properties.empty:
        print(f"\n✅ SUCCESS! Collected {len(properties):,} Boston properties")
        print(f"✅ Saved in: data\\raw\\")
    else:
        print(f"\n❌ Collection failed")