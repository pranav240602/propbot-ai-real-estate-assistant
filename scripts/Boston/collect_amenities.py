"""
PropBot - Boston Local Businesses Collection
Yelp Fusion API - Amenities and Points of Interest

Collects: Restaurants, grocery stores, gyms, cafes, pharmacies, parks
Coverage: All 23 Boston neighborhoods
Output: data/raw/yelp_businesses_[timestamp].csv
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

# All Boston neighborhoods
BOSTON_NEIGHBORHOODS = [
    'Fenway', 'Back Bay', 'Beacon Hill', 'Allston', 'Brighton',
    'Roxbury', 'Mission Hill', 'Jamaica Plain', 'Dorchester',
    'South End', 'North End', 'Charlestown', 'South Boston',
    'East Boston', 'West Roxbury', 'Roslindale', 'Hyde Park',
    'Mattapan', 'Chinatown', 'Financial District', 'Seaport',
    'West End', 'Bay Village'
]

# Business categories important for real estate decisions
BUSINESS_CATEGORIES = {
    'grocery': 'grocery,supermarkets',
    'restaurants': 'restaurants',
    'cafes': 'coffee,cafes',
    'gyms': 'gyms,fitness',
    'pharmacies': 'drugstores,pharmacies',
    'convenience': 'convenience',
    'parks': 'parks'
}

def collect_yelp_businesses():
    """
    Collect local business data from Yelp Fusion API
    Free tier: 5,000 API calls per day
    """
    
    print("=" * 70)
    print("PROPBOT: YELP BUSINESS DATA COLLECTION")
    print("Source: Yelp Fusion API")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure output folder exists
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    
    # Get API key from environment
    api_key = os.getenv('YELP_API_KEY')
    
    # Validate API key
    if not api_key or api_key == 'your_yelp_api_key_here':
        print("❌ YELP_API_KEY not found in .env file\n")
        print("📋 Steps to get FREE Yelp API key:")
        print("1. Visit: https://www.yelp.com/developers/v3/manage_app")
        print("2. Create New App")
        print("   - App Name: PropBot")
        print("   - Industry: Business")
        print("3. Copy API key")
        print("4. Add to .env file: YELP_API_KEY=your_key")
        print("\nCannot proceed without API key.")
        return None
    
    print(f"✅ API key loaded: {api_key[:15]}...\n")
    
    # Yelp Fusion API endpoint
    url = "https://api.yelp.com/v3/businesses/search"
    
    # Headers with authentication
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    all_businesses = []
    api_calls = 0
    max_calls = 500  # Safety limit (free tier allows 5,000/day)
    
    print(f"📍 Neighborhoods: {len(BOSTON_NEIGHBORHOODS)}")
    print(f"🏪 Categories: {len(BUSINESS_CATEGORIES)}")
    print(f"📊 Max API calls: {max_calls}")
    print(f"⏱️  Estimated time: 5-8 minutes\n")
    
    # Calculate total tasks
    total_tasks = len(BOSTON_NEIGHBORHOODS) * len(BUSINESS_CATEGORIES)
    
    print(f"🔄 Starting collection of ~{total_tasks} searches...\n")
    
    # Collect for each neighborhood and category combination
    with tqdm(total=total_tasks, desc="Collecting businesses") as pbar:
        for neighborhood in BOSTON_NEIGHBORHOODS:
            for category_name, category_code in BUSINESS_CATEGORIES.items():
                
                # Safety check: don't exceed API limit
                if api_calls >= max_calls:
                    tqdm.write(f"\n⚠️  Reached API call safety limit ({max_calls} calls)")
                    tqdm.write(f"Collected {len(all_businesses):,} businesses so far")
                    break
                
                # Search parameters
                params = {
                    'location': f'{neighborhood}, Boston, MA',
                    'categories': category_code,
                    'limit': 50,  # Max results per request
                    'sort_by': 'best_match'
                }
                
                try:
                    response = requests.get(url, headers=headers, params=params, timeout=15)
                    api_calls += 1
                    
                    if response.status_code == 200:
                        data = response.json()
                        businesses = data.get('businesses', [])
                        
                        # Process each business
                        for biz in businesses:
                            location = biz.get('location', {})
                            coordinates = biz.get('coordinates', {})
                            categories_list = biz.get('categories', [])
                            
                            all_businesses.append({
                                'business_id': biz.get('id'),
                                'name': biz.get('name'),
                                'category': category_name,
                                'categories_full': ', '.join([c['title'] for c in categories_list]),
                                'rating': biz.get('rating'),
                                'review_count': biz.get('review_count'),
                                'price': biz.get('price', 'N/A'),
                                'phone': biz.get('phone', ''),
                                'address': location.get('address1', ''),
                                'city': location.get('city', ''),
                                'state': location.get('state', ''),
                                'zip_code': location.get('zip_code', ''),
                                'neighborhood_searched': neighborhood,
                                'latitude': coordinates.get('latitude'),
                                'longitude': coordinates.get('longitude'),
                                'distance_meters': biz.get('distance'),  # Distance from search center
                                'url': biz.get('url'),
                                'is_closed': biz.get('is_closed', False),
                                'transactions': ', '.join(biz.get('transactions', []))
                            })
                        
                        if len(businesses) > 0:
                            tqdm.write(f"  ✅ {neighborhood:20} - {category_name:12}: {len(businesses):2} businesses")
                        
                    elif response.status_code == 429:
                        tqdm.write(f"  ⏰ Rate limited at {neighborhood} - {category_name}")
                        time.sleep(5)  # Wait longer if rate limited
                        
                    elif response.status_code == 400:
                        tqdm.write(f"  ⚠️  {neighborhood} - {category_name}: Bad request")
                        
                    elif response.status_code == 401:
                        tqdm.write(f"  ❌ Invalid API key! Check your .env file")
                        break
                        
                    else:
                        tqdm.write(f"  ⚠️  {neighborhood} - {category_name}: HTTP {response.status_code}")
                    
                except requests.exceptions.Timeout:
                    tqdm.write(f"  ⏰ {neighborhood} - {category_name}: Timeout, skipping")
                    
                except Exception as e:
                    tqdm.write(f"  ❌ {neighborhood} - {category_name}: {str(e)}")
                
                # Update progress bar
                pbar.update(1)
                
                # Rate limiting: Yelp allows 5 calls/second
                time.sleep(0.25)  # 4 calls/second to be safe
            
            # Break outer loop if we hit API limit
            if api_calls >= max_calls:
                break
    
    # Process collected data
    if len(all_businesses) > 0:
        print(f"\n\n📊 Processing {len(all_businesses):,} businesses...")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_businesses)
        
        # Remove duplicates (same business may appear in multiple searches)
        original_count = len(df)
        df = df.drop_duplicates(subset=['business_id'], keep='first')
        duplicates_removed = original_count - len(df)
        
        print(f"✅ Removed {duplicates_removed:,} duplicates")
        print(f"✅ Final count: {len(df):,} unique businesses")
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'data/raw/yelp_businesses_{timestamp}.csv'
        
        print(f"\n💾 Saving to: {output_file}")
        df.to_csv(output_file, index=False)
        
        # File size
        file_size_kb = Path(output_file).stat().st_size / 1024
        
        # Summary statistics
        print("\n" + "=" * 70)
        print("✅ YELP BUSINESS DATA COLLECTION SUCCESSFUL!")
        print("=" * 70)
        print(f"Total businesses collected: {len(df):,}")
        print(f"API calls made: {api_calls}")
        print(f"File saved: {output_file}")
        print(f"File size: {file_size_kb:.2f} KB")
        
        # Breakdown by category
        print(f"\n📊 Businesses by category:")
        category_counts = df['category'].value_counts()
        for cat, count in category_counts.items():
            print(f"  {cat:15}: {count:,}")
        
        # Breakdown by neighborhood (top 10)
        print(f"\n📊 Top 10 neighborhoods by business count:")
        top_neighborhoods = df['neighborhood_searched'].value_counts().head(10)
        for hood, count in top_neighborhoods.items():
            print(f"  {hood:20}: {count}")
        
        # Rating statistics
        avg_rating = df['rating'].mean()
        print(f"\n⭐ Average business rating: {avg_rating:.2f}/5.0")
        
        # Price distribution
        print(f"\n💰 Price level distribution:")
        price_counts = df['price'].value_counts()
        for price, count in price_counts.items():
            print(f"  {price}: {count}")
        
        # Sample businesses
        print(f"\n📋 Sample businesses (top rated):")
        sample = df.nlargest(10, 'rating')[['name', 'category', 'neighborhood_searched', 'rating', 'review_count']]
        print(sample.to_string(index=False))
        
        print("\n" + "=" * 70)
        print("🎯 Amenity data ready for PropBot property analysis!")
        print("=" * 70)
        
        return df
        
    else:
        print("\n" + "=" * 70)
        print("❌ NO BUSINESS DATA COLLECTED")
        print("=" * 70)
        print("\nPossible issues:")
        print("1. Invalid API key - check .env file")
        print("2. API temporarily down")
        print("3. Rate limit exceeded (unlikely on first run)")
        print("\nTroubleshooting:")
        print("1. Verify API key in .env file")
        print("2. Check: echo %YELP_API_KEY%")
        print("3. Try again in a few minutes")
        print("=" * 70)
        
        return None

if __name__ == "__main__":
    print("\n🏪 Starting Yelp Local Business Data Collection\n")
    
    # Verify API key exists before starting
    load_dotenv()
    api_key = os.getenv('YELP_API_KEY')
    
    if not api_key or api_key == 'your_yelp_api_key_here':
        print("❌ YELP_API_KEY not set in .env file!\n")
        print("📋 Quick setup:")
        print("1. Get key from: https://www.yelp.com/developers/v3/manage_app")
        print("2. Open .env file")
        print("3. Add: YELP_API_KEY=your_key_here")
        print("4. Save and run this script again\n")
    else:
        # Run collection
        businesses_df = collect_yelp_businesses()
        
        if businesses_df is not None and len(businesses_df) > 0:
            print(f"\n✅ COMPLETE SUCCESS!")
            print(f"✅ Collected {len(businesses_df):,} Boston businesses via Yelp API")
            print(f"✅ Saved in: data\\raw\\yelp_businesses_*.csv")
            print(f"\n🎯 You now have 3/5 datasets collected!")
            print(f"   Next: Properties (Kaggle) + Crime (manual download)")
        else:
            print(f"\n❌ Collection failed")
            print(f"Check .env file and API key")