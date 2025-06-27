"""
OCR_ncaa_2ndhalf.py

Extract NCAA 2nd half point spread odds from a screenshot using OCR.

Instructions:
1. In your browser, set magnification to 80%.
2. Scroll so the 'Time' header row is at the top of the page.
3. Press the Down Arrow key 7 times to ensure all rows are visible.
4. Take a screenshot of the entire visible odds table (including all rows).
5. Save the screenshot as 'odds_table.png' in the current directory.
6. Run this script to extract the table and save as CSV.

Dependencies:
- pytesseract
- pillow
- pandas

Install with:
    pip install pytesseract pillow pandas
    # You also need Tesseract OCR installed: https://github.com/tesseract-ocr/tesseract

Usage:
    python OCR_ncaa_2ndhalf.py
"""

import pytesseract
from PIL import Image
import pandas as pd
import os

# Path to the screenshot
IMAGE_PATH = 'odds_table.png'
CSV_PATH = 'data/ocr_ncaa_2ndhalf.csv'

if not os.path.exists(IMAGE_PATH):
    print(f"❌ Screenshot '{IMAGE_PATH}' not found. Please follow the instructions at the top of this script.")
    exit(1)

# Load the image
img = Image.open(IMAGE_PATH)

# Run OCR
print("Running OCR on screenshot...")
ocr_text = pytesseract.image_to_string(img)

# Split into lines and try to find the header
lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]

# Find the header row (should contain 'Time' and 'Teams')
header_idx = None
for i, line in enumerate(lines):
    if 'Time' in line and 'Teams' in line:
        header_idx = i
        break

if header_idx is None:
    print("❌ Could not find header row in OCR output. Please check your screenshot.")
    exit(1)

header_line = lines[header_idx]
# Try to split header into columns
header_cols = [col.strip() for col in header_line.split() if col.strip()]

# Collect data rows (until a line that looks like a footer or is too short)
data_rows = []
for line in lines[header_idx+1:]:
    # Stop if we hit a line that looks like a footer or is too short
    if line.lower().startswith('recent news') or len(line.split()) < 4:
        break
    # Split line into columns (may need more robust parsing for real-world use)
    row = [col.strip() for col in line.split() if col.strip()]
    if len(row) >= len(header_cols):
        data_rows.append(row[:len(header_cols)])

# Build DataFrame
if not data_rows:
    print("❌ No data rows found in OCR output. Please check your screenshot and try again.")
    exit(1)

df = pd.DataFrame(data_rows, columns=header_cols)
print(df)

# Save to CSV
os.makedirs('data', exist_ok=True)
df.to_csv(CSV_PATH, index=False)
print(f"✅ Data saved to {CSV_PATH}") 