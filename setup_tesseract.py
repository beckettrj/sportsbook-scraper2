"""
setup_tesseract.py

Helper script to set up Tesseract OCR in the working directory.
"""

import os
import sys

def setup_tesseract():
    """Set up Tesseract OCR in the working directory"""
    print("🔧 Tesseract OCR Setup")
    print("=" * 30)
    
    # Check if tesseract-ocr directory exists
    tesseract_dir = os.path.join(os.getcwd(), "tesseract-ocr")
    tesseract_exe = os.path.join(tesseract_dir, "tesseract.exe")
    
    if os.path.exists(tesseract_exe):
        print(f"✅ Found Tesseract at: {tesseract_exe}")
        update_ocr_script(tesseract_exe)
        return True
    
    print("❌ Tesseract not found in working directory.")
    print("\n📥 Manual Installation Instructions:")
    print("1. Download Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/releases")
    print("2. Look for: tesseract-ocr-w64-setup-5.3.3.20231005.exe (or latest version)")
    print("3. Run the installer and choose to install to: " + tesseract_dir)
    print("4. Or extract a portable version to: " + tesseract_dir)
    print("5. Make sure tesseract.exe is in: " + tesseract_exe)
    print("\nAfter installation, run this script again to configure the OCR scripts.")
    
    return False

def update_ocr_script(tesseract_exe):
    """Update OCR script to use local Tesseract"""
    print(f"🔧 Updating OCR script to use: {tesseract_exe}")
    
    # Update OCR_ncaa_2ndhalf.py
    with open("OCR_ncaa_2ndhalf.py", "r") as f:
        content = f.read()
    
    # Add tesseract path setting if not already present
    if "pytesseract.pytesseract.tesseract_cmd" not in content:
        import_section = "import pytesseract\nfrom PIL import Image\nimport pandas as pd\nimport os\n"
        path_setting = f"\n# Set Tesseract path\npytesseract.pytesseract.tesseract_cmd = r'{tesseract_exe}'\n\n"
        
        content = content.replace(import_section, import_section + path_setting)
        
        with open("OCR_ncaa_2ndhalf.py", "w") as f:
            f.write(content)
        
        print(f"✅ Updated OCR_ncaa_2ndhalf.py")
    else:
        print("✅ OCR script already configured")
    
    # Update example_ncaa_2ndhalf.py
    with open("example_ncaa_2ndhalf.py", "r") as f:
        content = f.read()
    
    # Update the TESSERACT_PATH variable
    old_path = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    new_path = tesseract_exe.replace('\\', '\\\\')
    
    if old_path in content:
        content = content.replace(old_path, new_path)
        
        with open("example_ncaa_2ndhalf.py", "w") as f:
            f.write(content)
        
        print(f"✅ Updated example_ncaa_2ndhalf.py")
    else:
        print("✅ example_ncaa_2ndhalf.py already configured")

def test_tesseract():
    """Test if Tesseract is working"""
    print("\n🧪 Testing Tesseract installation...")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Create a simple test image
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a test image with text
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test OCR", fill='black')
        
        # Save test image
        test_image = "test_ocr.png"
        img.save(test_image)
        
        # Try OCR
        text = pytesseract.image_to_string(img)
        print(f"✅ OCR test successful: '{text.strip()}'")
        
        # Clean up
        os.remove(test_image)
        
        return True
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

if __name__ == "__main__":
    if setup_tesseract():
        if test_tesseract():
            print("\n🎉 Tesseract setup completed successfully!")
            print("You can now run your OCR scripts.")
        else:
            print("\n⚠️  Tesseract installed but test failed. Check the installation.")
    else:
        print("\n📋 Please follow the installation instructions above.") 