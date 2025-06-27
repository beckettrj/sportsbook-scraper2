#!/usr/bin/env python3
"""
Test script to look for API endpoints that might provide the actual odds data.
"""

import requests
import json

def test_api_endpoints():
    """
    Test various API endpoints that might provide the odds data.
    """
    print("🔍 Testing API endpoints for odds data")
    print("=" * 50)
    
    # Test different possible API endpoints
    api_endpoints = [
        "https://www.sportsbookreview.com/api/odds/ncaa-basketball/totals/2nd-half?date=2025-03-19",
        "https://www.sportsbookreview.com/api/v1/odds/ncaa-basketball/totals/2nd-half?date=2025-03-19",
        "https://www.sportsbookreview.com/api/odds?league=ncaa-basketball&type=totals&scope=2nd-half&date=2025-03-19",
        "https://www.sportsbookreview.com/api/betting-odds/ncaa-basketball/totals/2nd-half?date=2025-03-19",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    for endpoint in api_endpoints:
        print(f"\n🔗 Testing: {endpoint}")
        try:
            r = requests.get(endpoint, headers=headers)
            print(f"   Status: {r.status_code}")
            
            if r.status_code == 200:
                try:
                    # Try to parse as JSON
                    data = r.json()
                    print(f"   ✅ JSON response received")
                    print(f"   📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Look for odds-related data
                    if isinstance(data, dict):
                        if 'odds' in data or 'data' in data or 'games' in data:
                            print(f"   🎯 Found potential odds data!")
                            print(f"   📋 Sample: {str(data)[:200]}...")
                except json.JSONDecodeError:
                    print(f"   📄 Not JSON - content type: {r.headers.get('content-type', 'unknown')}")
                    print(f"   📋 First 200 chars: {r.text[:200]}...")
            else:
                print(f"   ❌ Failed with status {r.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Also try to find any JavaScript files that might contain API calls
    print(f"\n🔍 Looking for JavaScript files...")
    try:
        r = requests.get("https://www.sportsbookreview.com/betting-odds/ncaa-basketball/totals/2nd-half/?date=2025-03-19")
        
        # Look for script tags that might contain API endpoints
        import re
        script_patterns = [
            r'src="([^"]*\.js)"',
            r'api[^"]*\.js',
            r'odds[^"]*\.js',
            r'data[^"]*\.js'
        ]
        
        for pattern in script_patterns:
            matches = re.findall(pattern, r.text, re.IGNORECASE)
            if matches:
                print(f"   Found potential JS files: {matches[:3]}")  # Show first 3
                
    except Exception as e:
        print(f"   ❌ Error searching for JS files: {e}")

if __name__ == "__main__":
    test_api_endpoints() 