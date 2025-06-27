"""
install_tesseract.py

Download and install Tesseract OCR to the working directory.
"""

import os
import urllib.request
import zipfile
import subprocess
import sys

def download_tesseract():
    """Download portable Tesseract OCR"""
    print("Downloading Tesseract OCR...")
    
    # URL for portable Tesseract
    url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    
    try:
        # Download the installer
        print(f"Downloading from: {url}")
        urllib.request.urlretrieve(url, "tesseract-installer.exe")
        print("✅ Download completed")
        
        # Install to current directory
        print("Installing Tesseract to current directory...")
        install_dir = os.path.join(os.getcwd(), "tesseract-ocr")
        
        # Run installer silently
        cmd = [
            "tesseract-installer.exe",
            "/S",  # Silent install
            f"/D={install_dir}"  # Install directory
        ]
        
        subprocess.run(cmd, check=True)
        print(f"✅ Tesseract installed to: {install_dir}")
        
        # Update the OCR script to use the local Tesseract
        update_ocr_script(install_dir)
        
        # Clean up installer
        os.remove("tesseract-installer.exe")
        print("✅ Installer cleaned up")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def update_ocr_script(tesseract_path):
    """Update OCR script to use local Tesseract"""
    tesseract_exe = os.path.join(tesseract_path, "tesseract.exe")
    
    # Update OCR_ncaa_2ndhalf.py
    with open("OCR_ncaa_2ndhalf.py", "r") as f:
        content = f.read()
    
    # Add tesseract path setting
    if "pytesseract.pytesseract.tesseract_cmd" not in content:
        import_section = "import pytesseract\nfrom PIL import Image\nimport pandas as pd\nimport os\n"
        path_setting = f"\n# Set Tesseract path\npytesseract.pytesseract.tesseract_cmd = r'{tesseract_exe}'\n\n"
        
        content = content.replace(import_section, import_section + path_setting)
        
        with open("OCR_ncaa_2ndhalf.py", "w") as f:
            f.write(content)
        
        print(f"✅ Updated OCR script to use: {tesseract_exe}")

if __name__ == "__main__":
    print("🔧 Tesseract OCR Installer")
    print("=" * 30)
    
    if download_tesseract():
        print("\n🎉 Tesseract installation completed!")
        print("You can now run your OCR scripts.")
    else:
        print("\n❌ Installation failed. Please try again.") 