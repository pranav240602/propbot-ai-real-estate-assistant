"""
PropBot - MBTA Transit Data (Fixed version with debugging)
"""

import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import json

def collect_mbta_transit_fixed():
    """
    Collect MBTA data with better error handling
    """
    
    print("=" * 70)
    print("PROPBOT: MBTA TRANSIT DATA COLLECTION (DEBUG MODE)")
    print("=" * 70)
    
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    
    # MBTA V3 API
    base_url = "https://api-v3.mbta.com/stops"
    
    print("\n🔍 Testing API connection...")
    
    # Test 1: Get ALL stops first (no filters)
    try:
        print("\nTest 1: Fetching all stops (no filters)...")
        response = requests.get(base_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            all_stops = data.get('data', [])
            
            print(f"✅ API working! Total stops in system: {len(all_stops)}")
            
            # Show what we got
            if len(all_stops) > 0:
                print(f"\n📋 Sample stop structure:")
                sample = all_stops[0]
                print(json.dumps(sample, indent=2)[:500])
                
                # Now filter for Boston area
                boston_stations = []
                
                for stop in all_stops:
                    attrs = stop.get('attributes', {})
                    municipality = attrs.get('municipality', '')
                    
                    # Boston area cities
                    if municipality in ['Boston', 'Cambridge', 'Somerville', 'Brookline']:
                        boston_stations.append({
                            'station_id': stop.get('id'),
                            'station_name': attrs.get('name'),
                            'municipality': municipality,
                            'latitude': attrs.get('latitude'),
                            'longitude': attrs.get('longitude'),
                            'wheelchair_accessible': attrs.get('wheelchair_boarding', 0) == 1,
                            'location_type': attrs.get('location_type'),
                            'vehicle_type': attrs.get('vehicle_type', '')
                        })
                
                print(f"\n✅ Filtered to {len(boston_stations)} Boston-area stations")
                
                if len(boston_stations) > 0:
                    df = pd.DataFrame(boston_stations)
                    
                    # Save
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f'data/raw/mbta_stations_{timestamp}.csv'
                    df.to_csv(output_file, index=False)
                    
                    file_size_kb = Path(output_file).stat().st_size / 1024
                    
                    print("\n" + "=" * 70)
                    print("✅ SUCCESS!")
                    print("=" * 70)
                    print(f"Stations collected: {len(df)}")
                    print(f"File saved: {output_file}")
                    print(f"File size: {file_size_kb:.2f} KB")
                    
                    print(f"\n📊 By municipality:")
                    for city, count in df['municipality'].value_counts().items():
                        print(f"  {city}: {count}")
                    
                    print(f"\n📋 Sample:")
                    print(df[['station_name', 'municipality']].head(10).to_string(index=False))
                    
                    print("=" * 70)
                    
                    return df
                else:
                    print("\n⚠️  No Boston stations found after filtering")
                    return None
                    
            else:
                print("\n⚠️  API returned empty data array")
                return None
                
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    df = collect_mbta_transit_fixed()
    
    if df is not None:
        print(f"\n✅ Transit data collected successfully!")
    else:
        print(f"\n⚠️  Transit API unavailable")
        print(f"\n💡 BACKUP PLAN:")
        print("1. Manual MBTA station list: https://www.mbta.com/stops")
        print("2. Or skip transit for now, collect amenities/properties")