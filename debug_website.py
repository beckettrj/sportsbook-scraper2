#!/usr/bin/env python3
"""
Debug script to examine the actual HTML content from the website.
"""

import requests
import pandas as pd
from io import StringIO

def debug_website():
    """
    Debug the website response to understand what's being returned.
    """
    print("🔍 Debugging website response")
    print("=" * 50)
    
    # Test URL
    test_url = "https://www.sportsbookreview.com/betting-odds/ncaa-basketball/totals/2nd-half/?date=2025-03-19"
    
    # Try different headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        r = requests.get(test_url, headers=headers)
        print(f"✅ Response status: {r.status_code}")
        print(f"📏 Content length: {len(r.text)} characters")
        
        # Check if we got redirected
        if r.history:
            print(f"🔄 Redirected from: {r.history[0].url}")
        print(f"📍 Final URL: {r.url}")
        
        # Look for table-related content
        html_content = r.text.lower()
        
        # Check for common table indicators
        if "<table" in html_content:
            print("✅ Found <table> tags in HTML")
        else:
            print("❌ No <table> tags found")
            
        if "ncaa" in html_content:
            print("✅ Found 'ncaa' in HTML")
        else:
            print("❌ No 'ncaa' found in HTML")
            
        if "basketball" in html_content:
            print("✅ Found 'basketball' in HTML")
        else:
            print("❌ No 'basketball' found in HTML")
            
        if "odds" in html_content:
            print("✅ Found 'odds' in HTML")
        else:
            print("❌ No 'odds' found in HTML")
        
        # Look for specific content that might indicate the page structure
        if "sportsbook" in html_content:
            print("✅ Found 'sportsbook' in HTML")
        else:
            print("❌ No 'sportsbook' found in HTML")
            
        # Check if we got a login page or error page
        if "login" in html_content or "sign in" in html_content:
            print("⚠️  Page appears to require login")
            
        if "access denied" in html_content or "blocked" in html_content:
            print("⚠️  Access appears to be blocked")
            
        # Show first 1000 characters of HTML
        print(f"\n📄 First 1000 characters of HTML:")
        print(r.text[:1000])
        
        # Try to find any table-like structures
        print(f"\n🔍 Looking for table structures...")
        lines = r.text.split('\n')
        table_lines = [line for line in lines if '<table' in line or '<tr>' in line or '<td>' in line]
        if table_lines:
            print(f"Found {len(table_lines)} table-related lines")
            for i, line in enumerate(table_lines[:5]):
                print(f"  {i+1}: {line.strip()}")
        else:
            print("No table structures found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_website() 