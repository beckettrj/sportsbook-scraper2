from scrapers.sportsbookreview import NCAABasketballOddsScraper
import requests
import pandas as pd
from io import StringIO

# Test NCAA scraper with trailing slash
scraper = NCAABasketballOddsScraper([2021])
print("Base URL:", scraper.base)
print("Season:", scraper._make_season(2021))
full_url = scraper.base + scraper._make_season(2021) + "/"
print("Full URL with slash:", full_url)

# Test the URL with trailing slash
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(full_url, headers=headers)
print("Status Code:", r.status_code)
print("Content Length:", len(r.text))

# Check what tables are available
try:
    tables = pd.read_html(StringIO(r.text))
    print(f"Number of tables found: {len(tables)}")
    for i, table in enumerate(tables):
        print(f"Table {i} shape: {table.shape}")
        if table.shape[0] > 0:
            print(f"Table {i} columns: {list(table.columns)}")
            print(f"Table {i} first few rows:")
            print(table.head(3))
            print()
except Exception as e:
    print(f"Error reading tables: {e}")

# Also check if there are any table tags in the HTML
if "table" in r.text.lower():
    print("Table tags found in HTML")
    # Find table positions
    table_positions = []
    start = 0
    while True:
        pos = r.text.find("<table", start)
        if pos == -1:
            break
        table_positions.append(pos)
        start = pos + 1
    print(f"Found {len(table_positions)} table tags at positions: {table_positions[:5]}")
else:
    print("No table tags found in HTML") 