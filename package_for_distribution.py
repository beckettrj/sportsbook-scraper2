#!/usr/bin/env python3
"""
Package the sportsbook scraper for distribution via email.

This script creates a clean distribution package with all necessary files
and excludes development files and large data files.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_distribution_package():
    """Create a clean distribution package for email sharing."""
    
    # Define source and destination directories
    source_dir = Path(".")
    dist_dir = Path("distribution/sportsbook-scraper")
    
    # Files to include in distribution
    include_files = [
        # Core application files
        "cli.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "LICENSE.md",
        
        # Installation scripts
        "install.py",
        "install.bat",
        "install.sh",
        
        # Scraper modules
        "scrapers/__init__.py",
        "scrapers/sportsbookreview.py",
        
        # Configuration files
        "config/translated.json",
        
        # Distribution files
        "distribution/README_QUICK_START.md",
        "distribution/EMAIL_TEMPLATE.txt",
        
        # Makefile (for Linux/Mac users)
        "Makefile",
    ]
    
    # Directories to include
    include_dirs = [
        "scrapers",
        "config",
    ]
    
    # Files to exclude
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".gitignore",
        "data/*.json",
        "data/*.csv",
        "test_*.py",
        "*.log",
        ".DS_Store",
        "Thumbs.db",
    ]
    
    print("📦 Creating distribution package...")
    
    # Clean and create distribution directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy included files
    for file_path in include_files:
        source_file = source_dir / file_path
        dest_file = dist_dir / file_path
        
        if source_file.exists():
            # Create parent directories if needed
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_file, dest_file)
            print(f"✅ Copied: {file_path}")
        else:
            print(f"⚠️  Warning: {file_path} not found")
    
    # Copy included directories
    for dir_path in include_dirs:
        source_dir_path = source_dir / dir_path
        dest_dir_path = dist_dir / dir_path
        
        if source_dir_path.exists():
            shutil.copytree(source_dir_path, dest_dir_path, dirs_exist_ok=True)
            print(f"✅ Copied directory: {dir_path}")
        else:
            print(f"⚠️  Warning: {dir_path} not found")
    
    # Create empty data directory
    (dist_dir / "data").mkdir(exist_ok=True)
    
    # Create a sample data file to show the output format
    sample_data = {
        "season": [2023, 2023],
        "date": [20230907, 20230908],
        "home_team": ["Chiefs", "Eagles"],
        "away_team": ["Lions", "Patriots"],
        "home_final": [21, 25],
        "away_final": [20, 20],
        "home_close_spread": [-3.5, -4.0],
        "away_close_spread": [3.5, 4.0],
        "close_over_under": [52.5, 45.0]
    }
    
    import pandas as pd
    sample_df = pd.DataFrame(sample_data)
    sample_df.to_json(dist_dir / "data" / "sample_output.json", orient="records")
    print("✅ Created sample output file")
    
    # Create zip file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"sportsbook-scraper_{timestamp}.zip"
    zip_path = Path("distribution") / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"🎉 Distribution package created: {zip_path}")
    print(f"📁 Package size: {zip_path.stat().st_size / 1024:.1f} KB")
    
    return zip_path

def print_distribution_instructions():
    """Print instructions for distributing the package."""
    print("\n" + "="*60)
    print("📧 EMAIL DISTRIBUTION INSTRUCTIONS")
    print("="*60)
    print("\n1. 📦 The zip file is ready in the 'distribution' folder")
    print("2. 📧 Use the email template in 'distribution/EMAIL_TEMPLATE.txt'")
    print("3. 📎 Attach the zip file to your email")
    print("4. 📋 Include the README_QUICK_START.md content in the email body")
    print("\n📊 Package Contents:")
    print("   ✅ Complete scraper with all dependencies")
    print("   ✅ Automated installation scripts")
    print("   ✅ Professional documentation")
    print("   ✅ Sample data and examples")
    print("   ✅ Cross-platform compatibility")
    print("\n🎯 Recipient can:")
    print("   - Extract the zip file")
    print("   - Run the installation script")
    print("   - Start scraping immediately")
    print("   - Get help from included documentation")

if __name__ == "__main__":
    try:
        zip_path = create_distribution_package()
        print_distribution_instructions()
    except Exception as e:
        print(f"❌ Error creating package: {e}") 