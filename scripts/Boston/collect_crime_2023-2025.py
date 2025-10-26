"""
PropBot - Crime Data 2023-2025 (Present) via API
Resource: Crime Incident Reports - 2023 to Present
Resource ID: b973d8cb-eeb2-4e7e-99da-c92938efc9c0
Coverage: 2023, 2024, 2025 (up to October 2025)
"""

import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import time

def collect_crime_2023_to_present():
    """
    Collect crime data from 2023 to present (October 2025)
    """
    
    print("=" * 70)
    print("PROPBOT: CRIME DATA 2023-2025 (API)")
    print("=" * 70)
    print(f"Resource ID: b973d8cb-eeb2-4e7e-99da-c92938efc9c0")
    print(f"Coverage: 2023 to October 2025")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    
    api_url = "https://data.boston.gov/api/3/action/datastore_search"
    resource_id = "b973d8cb-eeb2-4e7e-99da-c92938efc9c0"
    
    all_records = []
    offset = 0
    limit = 10000
    
    print("🔄 Collecting 2023-2025 crime data...\n")
    
    with tqdm(desc="Fetching recent crime data", unit=" records") as pbar:
        batch = 1
        
        while offset < 100000:
            params = {
                'resource_id': resource_id,
                'limit': limit,
                'offset': offset
            }
            
            try:
                response = requests.get(api_url, params=params, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        records = data.get('result', {}).get('records', [])
                        
                        if not records:
                            tqdm.write(f"\n✅ Batch {batch}: No more records")
                            break
                        
                        all_records.extend(records)
                        pbar.update(len(records))
                        pbar.set_postfix({
                            'Batch': batch,
                            'Total': f'{len(all_records):,}'
                        })
                        
                        tqdm.write(f"  Batch {batch}: +{len(records):,} (Total: {len(all_records):,})")
                        
                        offset += limit
                        batch += 1
                        
                        if len(records) < limit:
                            break
                            
                    else:
                        tqdm.write(f"\n❌ API error: {data.get('error')}")
                        break
                        
                else:
                    tqdm.write(f"\n❌ HTTP {response.status_code}")
                    break
                
                time.sleep(0.5)
                
            except Exception as e:
                tqdm.write(f"\n❌ Error: {e}")
                break
    
    if len(all_records) > 0:
        df = pd.DataFrame(all_records)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'data/raw/boston_crime_2023_2025_api_{timestamp}.csv'
        
        df.to_csv(output_file, index=False)
        
        file_size_mb = Path(output_file).stat().st_size / (1024 * 1024)
        
        print("\n" + "=" * 70)
        print("✅ API COLLECTION SUCCESSFUL!")
        print("=" * 70)
        print(f"Records (2023-2025): {len(df):,}")
        print(f"File: {output_file}")
        print(f"Size: {file_size_mb:.2f} MB")
        
        if 'YEAR' in df.columns:
            print(f"\n📊 By year:")
            for year, count in df['YEAR'].value_counts().sort_index().items():
                print(f"  {year}: {count:,}")
        
        print(f"\n📋 Sample:")
        print(df.head(3).to_string())
        
        print("\n" + "=" * 70)
        print("🎯 NEXT STEP:")
        print("=" * 70)
        print("Download historical data (2020-2022) manually:")
        print("1. Visit: https://data.boston.gov/dataset/crime-incident-reports")
        print("2. Find legacy/historical dataset (2015-2022)")
        print("3. Download CSV")
        print("4. Filter to 2020-2022 only")
        print("5. Save as: data/raw/boston_crime_2020_2022_manual.csv")
        print("\nWeek 2: Merge → Complete 2020-2025 dataset (6 years!)")
        print("=" * 70)
        
        return df
    else:
        print("\n❌ No data collected")
        return None

if __name__ == "__main__":
    df = collect_crime_2023_to_present()
    
    if df is not None:
        print(f"\n✅ API collection complete!")
        print(f"🎯 Now download 2020-2022 manually to complete dataset")
