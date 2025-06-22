#!/bin/bash

echo "🚀 Sportsbook Review Scraper - Installation"
echo "============================================"

echo ""
echo "📋 This script will install everything needed to run the scraper."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python 3.7+ from https://python.org"
    echo "   Or use your system's package manager:"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "   macOS: brew install python3"
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Run the installation script
echo "🔄 Running installation script..."
python3 install.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Quick Start Examples:"
echo ""
echo "1. Scrape NFL data for 2023:"
echo "   python3 cli.py --sport nfl --start 2023 --end 2023 --filename nfl_2023"
echo ""
echo "2. Scrape NBA data for 2022-2023:"
echo "   python3 cli.py --sport nba --start 2022 --end 2023 --filename nba_2022_2023"
echo ""
echo "3. Scrape NCAA Basketball data as CSV:"
echo "   python3 cli.py --sport ncaa --start 2021 --end 2022 --filename ncaa_2021_2022 --format csv"
echo ""
echo "📖 For more information, see README.md"
echo "" 