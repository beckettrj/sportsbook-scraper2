"""
download_tesseract.py

Download pre-compiled Tesseract OCR for Windows.
"""

import os
import urllib.request
import zipfile
import shutil

def download_tesseract():
    """Download portable Tesseract OCR"""
    print("Downloading Tesseract OCR...")
    
    # Try different URLs for Tesseract
    urls = [
        "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe",
        "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe",
        "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.1.20230401/tesseract-ocr-w64-setup-5.3.1.20230401.exe"
    ]
    
    for url in urls:
        try:
            print(f"Trying: {url}")
            filename = url.split('/')[-1]
            urllib.request.urlretrieve(url, filename)
            print(f"✅ Downloaded: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    print("❌ All download attempts failed")
    return None

def extract_portable():
    """Try to find a portable version"""
    print("\nLooking for portable Tesseract...")
    
    # Check if there's already a portable version in the directory
    portable_dirs = [
        "tesseract-ocr",
        "tesseract-portable", 
        "tesseract"
    ]
    
    for dir_name in portable_dirs:
        tesseract_exe = os.path.join(dir_name, "tesseract.exe")
        if os.path.exists(tesseract_exe):
            print(f"✅ Found existing Tesseract: {tesseract_exe}")
            return tesseract_exe
    
    print("❌ No portable Tesseract found")
    return None

def main():
    print("🔧 Tesseract OCR Downloader")
    print("=" * 30)
    
    # First check for existing portable version
    existing = extract_portable()
    if existing:
        print(f"Using existing Tesseract: {existing}")
        return existing
    
    # Try to download
    filename = download_tesseract()
    if filename:
        print(f"\n📦 Downloaded: {filename}")
        print("Please run the installer and choose to install to: tesseract-ocr/")
        print("Then run: python setup_tesseract.py")
    else:
        print("\n❌ Could not download Tesseract automatically.")
        print("Please manually download from: https://github.com/UB-Mannheim/tesseract/releases")
        print("Install to: tesseract-ocr/ directory")

if __name__ == "__main__":
    main() 