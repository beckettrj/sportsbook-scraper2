@echo off
echo 🚀 Sportsbook Review Scraper - Windows Installation
echo ==================================================

echo.
echo 📋 This script will install everything needed to run the scraper.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.7+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the installation script
echo 🔄 Running installation script...
python install.py

if errorlevel 1 (
    echo.
    echo ❌ Installation failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo 🎉 Installation completed successfully!
echo.
echo 📋 Quick Start Examples:
echo.
echo 1. Scrape NFL data for 2023:
echo    python cli.py --sport nfl --start 2023 --end 2023 --filename nfl_2023
echo.
echo 2. Scrape NBA data for 2022-2023:
echo    python cli.py --sport nba --start 2022 --end 2023 --filename nba_2022_2023
echo.
echo 3. Scrape NCAA Basketball data as CSV:
echo    python cli.py --sport ncaa --start 2021 --end 2022 --filename ncaa_2021_2022 --format csv
echo.
echo 📖 For more information, see README.md
echo.
pause 