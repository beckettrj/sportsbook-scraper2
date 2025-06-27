#!/usr/bin/env python3
"""
Script to examine the actual content of the working URL.
"""

import requests
import re

def examine_content():
    """
    Examine the content of the working URL to understand the data structure.
    """
    print("🔍 Examining content of working URL")
    print("=" * 50)
    
    url = "https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaa-basketball-2nd-half/2025-03-19"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    try:
        r = requests.get(url, headers=headers)
        print(f"✅ Status: {r.status_code}")
        print(f"📏 Content length: {len(r.text)}")
        
        # Look for specific patterns in the content
        content = r.text.lower()
        
        # Check for common patterns
        patterns = [
            r'no.*data.*available',
            r'no.*games.*found',
            r'no.*odds.*available',
            r'coming.*soon',
            r'not.*available',
            r'page.*not.*found',
            r'error.*404',
            r'no.*results',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"❌ Found pattern '{pattern}': {matches[:3]}")
        
        # Look for positive indicators
        positive_patterns = [
            r'game',
            r'team',
            r'score',
            r'odds',
            r'total',
            r'over.*under',
            r'betting',
            r'line',
        ]
        
        for pattern in positive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"✅ Found pattern '{pattern}': {len(matches)} occurrences")
        
        # Show a sample of the content
        print(f"\n📄 Sample content (first 1000 characters):")
        print(r.text[:1000])
        
        # Look for any table-like structures
        print(f"\n🔍 Looking for table structures...")
        if '<table' in r.text:
            print("✅ Found <table> tags")
            # Extract table content
            table_matches = re.findall(r'<table[^>]*>(.*?)</table>', r.text, re.DOTALL | re.IGNORECASE)
            print(f"   Found {len(table_matches)} table(s)")
            for i, table in enumerate(table_matches[:2]):  # Show first 2 tables
                print(f"   Table {i+1} (first 200 chars): {table[:200]}...")
        else:
            print("❌ No <table> tags found")
        
        # Look for any data structures
        print(f"\n🔍 Looking for data structures...")
        if 'json' in content:
            print("✅ Found JSON references")
        if 'api' in content:
            print("✅ Found API references")
        if 'javascript' in content:
            print("✅ Found JavaScript references")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    examine_content() 