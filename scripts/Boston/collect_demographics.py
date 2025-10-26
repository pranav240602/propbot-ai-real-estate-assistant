"""
PropBot - Boston Demographics Collection
US Census Bureau API (VERY RELIABLE!)
Requires: Free API key from api.census.gov
"""

import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# All Boston ZIP codes
BOSTON_ZIP_CODES = [
    '02108', '02109', '02110', '02111', '02113', '02114', '02115', '02116',
    '02118', '02119', '02120', '02121', '02122', '02124', '02125', '02126',
    '02127', '02128', '02129', '02130', '02131', '02132', '02134', '02135',
    '02136', '02163', '02199', '02203', '02210', '02215', '02467'
]

def collect_census_demographics():
    """
    Collect demographics from US Census Bureau API
    This API is very stable and reliable!
    """
    
    print("=" * 70)
    print("PROPBOT: BOSTON DEMOGRAPHICS COLLECTION")
    print("Source: US Census Bureau API")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure output folder
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    
    # Get API key
    api_key = os.getenv('CENSUS_API_KEY')
    
    if not api_key or api_key == 'your_census_api_key_here':
        print("⚠️  CENSUS_API_KEY not found in .env file")
        print("\n📋 To get a FREE API key:")
        print("1. Visit: https://api.census.gov/data/key_signup.html")
        print("2. Fill out form (takes 30 seconds)")
        print("3. Check email for API key")
        print("4. Add to .env file: CENSUS_API_KEY=your_key_here")
        print("\n💡 Using DEMO key for now (limited to 500 calls/day)\n")
        api_key = None
    else:
        print(f"✅ API key loaded: {api_key[:10]}...\n")
    
    # Census API endpoint
    base_url = "https://api.census.gov/data/2022/acs/acs5"
    
    # Variables to collect
    variables = {
        'B01003_001E': 'total_population',
        'B19013_001E': 'median_household_income',
        'B01002_001E': 'median_age',
        'B15003_022E': 'bachelors_degree',
        'B15003_023E': 'masters_degree',
        'B25064_001E': 'median_gross_rent',
        'B23025_005E': 'unemployed',
        'B03002_001E': 'total_pop_race',
        'B03002_012E': 'hispanic_latino'
    }
    
    var_string = ','.join(variables.keys())
    
    all_demographics = []
    
    print(f"📊 Collecting demographics for {len(BOSTON_ZIP_CODES)} Boston ZIP codes...")
    print(f"📈 Variables: Population, Income, Age, Education, Rent\n")
    
    # Collect for each ZIP
    for zip_code in tqdm(BOSTON_ZIP_CODES, desc="Fetching ZIPs"):
        params = {
            'get': var_string,
            'for': f'zip code tabulation area:{zip_code}'
        }
        
        # Add API key if available
        if api_key:
            params['key'] = api_key
        
        try:
            response = requests.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # First row is headers, second row is data
                if len(data) > 1:
                    values = data[1]
                    
                    # Create record
                    record = {
                        'zip_code': zip_code,
                        'total_population': values[0],
                        'median_household_income': values[1],
                        'median_age': values[2],
                        'bachelors_degree': values[3],
                        'masters_degree': values[4],
                        'median_gross_rent': values[5],
                        'unemployed': values[6],
                        'total_pop_race': values[7],
                        'hispanic_latino': values[8]
                    }
                    
                    all_demographics.append(record)
                    tqdm.write(f"  ✅ {zip_code}: {values[0]} population")
                else:
                    tqdm.write(f"  ⚠️  {zip_code}: No data")
                    
            elif response.status_code == 429:
                tqdm.write(f"  ⏰ {zip_code}: Rate limited, waiting...")
                time.sleep(5)
                # Retry
                response = requests.get(base_url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1:
                        all_demographics.append({'zip_code': zip_code, **dict(zip(variables.values(), data[1]))})
                        
            else:
                tqdm.write(f"  ❌ {zip_code}: HTTP {response.status_code}")
                
        except Exception as e:
            tqdm.write(f"  ❌ {zip_code}: {str(e)}")
        
        time.sleep(0.3)  # Rate limiting
    
    # Process results
    if len(all_demographics) > 0:
        df = pd.DataFrame(all_demographics)
        
        # Calculate derived metrics
        df['college_educated_pct'] = (
            (pd.to_numeric(df['bachelors_degree'], errors='coerce') + 
             pd.to_numeric(df['masters_degree'], errors='coerce')) /
            pd.to_numeric(df['total_population'], errors='coerce') * 100
        ).fillna(0)
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'data/raw/boston_demographics_{timestamp}.csv'
        df.to_csv(output_file, index=False)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ DEMOGRAPHICS COLLECTION SUCCESSFUL!")
        print("=" * 70)
        print(f"ZIP codes collected: {len(df)}/{len(BOSTON_ZIP_CODES)}")
        print(f"File saved: {output_file}")
        print(f"Coverage: {(len(df)/len(BOSTON_ZIP_CODES)*100):.1f}% of Boston")
        
        print(f"\n📋 Sample data:")
        print(df.head(3).to_string())
        
        print("\n" + "=" * 70)
        
        return df
    else:
        print("\n❌ No demographics collected")
        return None

if __name__ == "__main__":
    # Get API key first
    print("\n📝 BEFORE RUNNING:")
    print("Get FREE Census API key: https://api.census.gov/data/key_signup.html")
    print("Add to .env file: CENSUS_API_KEY=your_key\n")
    
    input("Press Enter when ready (or Ctrl+C to cancel)...")
    
    df = collect_census_demographics()
    
    if df is not None:
        print(f"\n✅ SUCCESS! Demographics data in data/raw/")