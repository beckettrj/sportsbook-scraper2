# 🚀 Sportsbook Scraper - Quick Start Guide

## 📋 What You Received
This package contains a complete sports betting odds scraper that can collect data from sportsbookreview.com for:
- **NFL** (2007-2023)
- **NBA** (2007-2023) 
- **NHL** (2007-2023)
- **MLB** (2007-2023)
- **NCAA Basketball** (2007-2023)

## ⚡ Quick Installation (Choose Your Platform)

### Windows Users
1. **Extract** the zip file to a folder
2. **Double-click** `install.bat`
3. **Follow** the on-screen instructions
4. **Done!** You're ready to scrape data

### Mac/Linux Users
1. **Extract** the zip file to a folder
2. **Open Terminal** and navigate to the folder
3. **Run:** `chmod +x install.sh && ./install.sh`
4. **Follow** the on-screen instructions

## 🎯 Quick Examples

Once installed, you can run these commands:

```bash
# Scrape NFL data for 2023
python cli.py --sport nfl --start 2023 --end 2023 --filename nfl_2023

# Scrape NBA data for 2022-2023
python cli.py --sport nba --start 2022 --end 2023 --filename nba_2022_2023

# Scrape NCAA Basketball as CSV
python cli.py --sport ncaa --start 2021 --end 2022 --filename ncaa_2021_2022 --format csv
```

## 📁 What You'll Get
- **JSON files** (default) or **CSV files** in the `data/` folder
- **Complete game data** including scores, spreads, totals, money lines
- **Team names** automatically translated to full names

## 🆘 Need Help?
- Check the main `README.md` for detailed documentation
- Look at the troubleshooting section for common issues
- The scraper handles missing years automatically

## 📊 Sample Data Fields
- Game dates and teams
- Quarter/half scores
- Opening and closing spreads
- Over/under totals
- Money lines
- Second half odds

**Happy Scraping! 🎉** 