#!/usr/bin/env python3
"""
Test script to scrape a single date and examine the table structure.
This will help us understand the actual format of the data from the website.
"""

import requests
import pandas as pd
from io import StringIO
from scrapers.sportsbookreview import NCAABasketball2ndHalf

def test_single_date():
    """
    Test scraping a single date to examine the table structure.
    """
    print("🧪 Testing single date scraping")
    print("=" * 50)
    
    # Test URL for March 19, 2025
    test_url = "https://www.sportsbookreview.com/betting-odds/ncaa-basketball/totals/2nd-half/?date=2025-03-19"
    
    print(f"📡 Fetching data from: {test_url}")
    
    # Make the request
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(test_url, headers=headers)
        print(f"✅ Response status: {r.status_code}")
        
        # Parse HTML tables
        dfs = pd.read_html(StringIO(r.text))
        print(f"📊 Found {len(dfs)} tables on the page")
        
        if dfs:
            # Examine the first table
            df = dfs[0]
            print(f"\n📋 Table shape: {df.shape}")
            print(f"📋 Table columns: {list(df.columns)}")
            print(f"📋 Table head:")
            print(df.head())
            
            # Show a few sample rows
            print(f"\n📋 Sample rows:")
            for i, row in df.head(3).iterrows():
                print(f"Row {i}: {list(row)}")
            
            # Test our parsing methods
            print(f"\n🔍 Testing parsing methods...")
            
            # Create a minimal scraper instance for testing
            scraper = NCAABasketball2ndHalf(dates_file="NCAA-2ndHalf-dates")
            
            # Test the reformat_data method
            try:
                processed_df = scraper._reformat_data(df, "2025-03-19")
                print(f"✅ Successfully processed data")
                print(f"📊 Processed shape: {processed_df.shape}")
                print(f"📊 Processed columns: {list(processed_df.columns)}")
                
                if not processed_df.empty:
                    print(f"\n📋 Sample processed data:")
                    print(processed_df.head())
                    # Write to CSV in the data directory
                    output_path = "data/ncaa_2ndhalf_single_date.csv"
                    processed_df.to_csv(output_path, index=False)
                    print(f"\n✅ CSV output written to {output_path}")
                else:
                    print("⚠️  No data was processed")
                    
            except Exception as e:
                print(f"❌ Error processing data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ No tables found on the page")
            
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_date() 