#!/usr/bin/env python3
"""
Example script for using the NCAABasketball2ndHalf scraper.

This script demonstrates how to:
1. Initialize the NCAABasketball2ndHalf scraper
2. Scrape 2nd half totals data for specified dates
3. Save the output using the same naming convention as NCAABasketballOddsScraper

Usage:
    python example_ncaa_2ndhalf.py

Author: Rod Beckett
License: MIT

Automated workflow:
1. Open browser and navigate to NCAA 2nd half odds page.
2. Wait 10 seconds for page to load.
3. Set zoom to 80%.
4. Scroll 'Time' header into view.
5. Press Down Arrow 7 times.
6. Take screenshot and save as 'data/odds_table.png'.
7. Run OCR on screenshot and extract table data.
8. Output extracted data as 'data/ncaa_2ndhalf_extracted.csv'.

Dependencies:
- selenium
- pytesseract
- pillow
- pandas

Install with:
    pip install selenium pytesseract pillow pandas
    # Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract

Usage:
    python example_ncaa_2ndhalf.py
"""

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image
import pytesseract
import shutil
import subprocess
import sys

# Config
URL = "https://www.sportsbookreview.com/betting-odds/ncaa-basketball/pointspread/2nd-half/?date=2024-02-05"
DATA_DIR = "data"
SCREENSHOT_PATH = os.path.join(DATA_DIR, "odds_table.png")
CSV_PATH = os.path.join(DATA_DIR, "ncaa_2ndhalf_extracted.csv")
TESSERACT_PATH = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # Update if needed

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Set tesseract path if needed
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Step 1: Open browser and navigate
options = Options()
options.headless = False
service = Service(r"C:\\Drivers\\chromedriver-win64\\chromedriver.exe")
try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()  # Maximize the browser window
except Exception as e:
    print(f"❌ Failed to start ChromeDriver: {e}")
    exit(1)

try:
    print(f"🌐 Navigating to {URL}")
    driver.get(URL)
    time.sleep(10)

    # Step 2: Set zoom to 80%
    try:
        driver.execute_script("document.body.style.zoom='80%'")
        print("🔍 Set zoom to 80%.")
    except Exception as e:
        print(f"⚠️  Failed to set zoom: {e}")

    # Step 3: Scroll 'Time' header into view
    try:
        header = driver.find_element(By.XPATH, "//th[contains(., 'Time')]")
        driver.execute_script("arguments[0].scrollIntoView();", header)
        print("⬇️  Scrolled 'Time' header into view.")
    except Exception as e:
        print(f"⚠️  Could not find or scroll to 'Time' header: {e}")

    # Step 4: Press Down Arrow 7 times
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(7):
            body.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.3)
        print("⬇️  Pressed Down Arrow 7 times.")
    except Exception as e:
        print(f"⚠️  Could not send Down Arrow keys: {e}")

    # Step 5: Take screenshot
    try:
        driver.save_screenshot(SCREENSHOT_PATH)
        print(f"✅ Screenshot saved as {SCREENSHOT_PATH}")
    except Exception as e:
        print(f"❌ Failed to save screenshot: {e}")
        driver.quit()
        exit(1)
finally:
    driver.quit()

# Step 6: Copy screenshot to where OCR script expects it
ocr_image_path = "odds_table.png"
try:
    shutil.copy2(SCREENSHOT_PATH, ocr_image_path)
    print(f"📋 Copied screenshot to {ocr_image_path} for OCR processing")
except Exception as e:
    print(f"❌ Failed to copy screenshot: {e}")
    exit(1)

# Step 7: Run OCR using the existing OCR script
print("🔍 Running OCR using OCR_ncaa_2ndhalf.py...")
try:
    # Set environment variables to handle encoding properly
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    result = subprocess.run([sys.executable, "OCR_ncaa_2ndhalf.py"], 
                          capture_output=True, text=True, check=True, env=env)
    print("✅ OCR completed successfully")
    print(result.stdout)
    
    # Copy the OCR output to our desired location
    ocr_output_path = "data/ocr_ncaa_2ndhalf.csv"
    if os.path.exists(ocr_output_path):
        shutil.copy2(ocr_output_path, CSV_PATH)
        print(f"✅ Data copied to {CSV_PATH}")
    else:
        print(f"⚠️  OCR output file {ocr_output_path} not found")
        
except subprocess.CalledProcessError as e:
    print(f"❌ OCR script failed: {e}")
    print(f"Error output: {e.stderr}")
    exit(1)
except Exception as e:
    print(f"❌ Failed to run OCR script: {e}")
    exit(1) 