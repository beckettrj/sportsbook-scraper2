#!/usr/bin/env python3
"""
Sportsbook Review Scraper - Installation Script
This script will set up everything needed to run the scraper.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please install Python 3.7+ from https://python.org")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def check_pip():
    """Check if pip is available."""
    print("🔍 Checking pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: pip is not available")
        print("   Please install pip or ensure Python was installed with pip")
        return False

def upgrade_pip():
    """Upgrade pip to latest version."""
    print("🔄 Upgrading pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print("✅ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not upgrade pip: {e}")
        return False

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_data_directory():
    """Create data directory if it doesn't exist."""
    print("📁 Creating data directory...")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory ready")

def test_installation():
    """Test if the scraper can be imported."""
    print("🧪 Testing installation...")
    try:
        import requests
        import pandas
        import lxml
        import html5lib
        import beautifulsoup4
        import openpyxl
        import xlrd
        print("✅ All packages imported successfully")
        
        # Test scraper import
        from scrapers.sportsbookreview import NFLOddsScraper
        print("✅ Scraper modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Error importing packages: {e}")
        return False

def show_usage_examples():
    """Show usage examples."""
    print("\n" + "="*60)
    print("🎉 Installation Complete!")
    print("="*60)
    print("\n📋 Quick Start Examples:")
    print("\n1. Scrape NFL data for 2023:")
    print("   python cli.py --sport nfl --start 2023 --end 2023 --filename nfl_2023")
    print("\n2. Scrape NBA data for 2022-2023:")
    print("   python cli.py --sport nba --start 2022 --end 2023 --filename nba_2022_2023")
    print("\n3. Scrape NCAA Basketball data as CSV:")
    print("   python cli.py --sport ncaa --start 2021 --end 2022 --filename ncaa_2021_2022 --format csv")
    print("\n4. Scrape all available years for MLB:")
    print("   python cli.py --sport mlb --start 2007 --end 2023 --filename mlb_archive_17Y")
    print("\n📖 For more information, see README.md")
    print("="*60)

def main():
    """Main installation function."""
    print("🚀 Sportsbook Review Scraper - Installation")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        sys.exit(1)
    
    # Upgrade pip
    upgrade_pip()
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create data directory
    create_data_directory()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed. Please check the error messages above.")
        sys.exit(1)
    
    # Show usage examples
    show_usage_examples()

if __name__ == "__main__":
    main() 