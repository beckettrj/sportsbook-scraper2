#!/usr/bin/env python3
"""
Sportsbook Review Scraper - Command Line Interface

This module provides the main entry point for the sportsbook scraper application.
It handles command line argument parsing, validation, and orchestrates the scraping process.

Supported sports: NFL, NBA, NHL, MLB, NCAA Basketball
Year range: 2007-2023 (configurable in config.py)

Author: Finn Lancaster, Rod Beckett (NCAA add-on)
License: MIT
"""

import sys
import argparse
import config
from scrapers.sportsbookreview import (
    NFLOddsScraper,
    NBAOddsScraper,
    NHLOddsScraper,
    MLBOddsScraper,
    NCAABasketballOddsScraper,
    NCAABasketball2ndHalf,
)
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Configure command line argument parser
parser = argparse.ArgumentParser(
    description="Scrape sports betting odds data from sportsbookreview.com",
    epilog="""
Examples:
  python cli.py --sport nfl --start 2020 --end 2021 --filename nfl_2020_2021
  python cli.py --sport ncaa2ndhalf --filename ncaa_2ndhalf_2025 --dates-file NCAA-2ndHalf-dates
"""
)

parser.add_argument(
    "--sport", 
    type=str, 
    required=True,
    choices=["nfl", "nba", "nhl", "mlb", "ncaa", "ncaa2ndhalf"],
    help="Sport to scrape data for (nfl, nba, nhl, mlb, ncaa, ncaa2ndhalf)"
)

# --start and --end are only required for non-ncaa2ndhalf
parser.add_argument(
    "--start", 
    type=int, 
    help="Start year for data scraping (inclusive). Required for all sports except ncaa2ndhalf."
)

parser.add_argument(
    "--end", 
    type=int, 
    help="End year for data scraping (inclusive). Required for all sports except ncaa2ndhalf."
)

parser.add_argument(
    "--filename", 
    type=str, 
    required=True,
    help="Output filename (without extension)"
)

parser.add_argument(
    "--format", 
    type=str, 
    default="csv",
    choices=["json", "csv"],
    help="Output format (default: csv)"
)

parser.add_argument(
    "--dates-file", 
    type=str, 
    default="NCAA-2ndHalf-dates",
    help="Dates file for ncaa2ndhalf scraper (default: NCAA-2ndHalf-dates). Only used for ncaa2ndhalf."
)

def validate_arguments(args):
    """
    Validate command line arguments against configuration constraints.
    """
    if args.sport == "ncaa2ndhalf":
        # For ncaa2ndhalf, ignore start/end
        if args.start is not None or args.end is not None:
            print("⚠️  Warning: --start and --end are ignored for ncaa2ndhalf.")
        return
    # For all other sports, start and end are required
    if args.start is None or args.end is None:
        raise ValueError("--start and --end are required for this sport.")
    if args.start < config.MIN_YEAR or args.end > config.MAX_YEAR:
        raise ValueError(
            f"Invalid year range. Must be between {config.MIN_YEAR} and {config.MAX_YEAR}."
        )
    if args.start > args.end:
        raise ValueError("Invalid year range. Start year must be before or equal to end year.")

def get_scraper_class(sport):
    """
    Get the appropriate scraper class for the specified sport.
    
    Args:
        sport (str): Sport identifier (nfl, nba, nhl, mlb, ncaa, ncaa2ndhalf)
        
    Returns:
        class: Scraper class for the specified sport
        
    Raises:
        ValueError: If sport is not supported
    """
    scrapers = {
        "nfl": NFLOddsScraper,
        "nba": NBAOddsScraper,
        "nhl": NHLOddsScraper,
        "mlb": MLBOddsScraper,
        "ncaa": NCAABasketballOddsScraper,
        "ncaa2ndhalf": NCAABasketball2ndHalf,
    }
    
    if sport.lower() not in scrapers:
        raise ValueError(f"Unsupported sport: {sport}. Supported sports: {list(scrapers.keys())}")
    
    return scrapers[sport.lower()]

def save_data(data, filename, output_format):
    """
    Save scraped data to file in the specified format.
    
    Args:
        data: Pandas DataFrame containing scraped data
        filename (str): Base filename without extension
        output_format (str): Output format ('json' or 'csv')
        
    Raises:
        ValueError: If output format is not supported
    """
    if output_format.lower() == "csv":
        output_path = f"data/{filename}.csv"
        data.to_csv(output_path, index=False)
        print(f"✅ Data saved to {output_path}")
    elif output_format.lower() == "json":
        output_path = f"data/{filename}.json"
        data.to_json(output_path, orient="records")
        print(f"✅ Data saved to {output_path}")
    else:
        raise ValueError("Invalid output format. Must be 'csv' or 'json'.")

def extract_ncaa_2ndhalf_games(driver):
    games = driver.find_elements(By.CSS_SELECTOR, "div[id^='game-']")
    all_rows = []

    for game in games:
        # Extract team names and scores
        teams = game.find_elements(By.CSS_SELECTOR, ".OddsTableMobile_participantData__vyNNx a")
        scores = game.find_elements(By.CSS_SELECTOR, ".OddsTableMobile_participantScore__Nap6l div")
        team_names = [t.text for t in teams]
        team_scores = [s.text for s in scores]

        # Extract WAGERS percentages (may be missing)
        wagers = game.find_elements(By.CSS_SELECTOR, ".OddsTableMobile_containerNumbers__BFztk .OddsTableMobile_opener__4YddM span")
        wagers_percents = [w.text for w in wagers]

        # Extract OPENER odds (first .OddsTableMobile_containerNumbers__BFztk after OPENER header)
        opener_section = game.find_elements(By.XPATH, ".//div[contains(text(), 'OPENER')]/following-sibling::section[1]//span")
        opener_odds = [o.text for o in opener_section]

        # Extract sportsbook odds (loop through each sportsbook column)
        sportsbook_odds = []
        sportsbook_sections = game.find_elements(By.CSS_SELECTOR, "section.OddsTableMobile_containerNumbers__BFztk")
        for section in sportsbook_sections:
            odds = section.find_elements(By.CSS_SELECTOR, ".OddsTableMobile_odds__thxLF span")
            sportsbook_odds.append([o.text for o in odds])

        # Build a row for the DataFrame
        row = {
            "team_away": team_names[0] if len(team_names) > 0 else "",
            "team_home": team_names[1] if len(team_names) > 1 else "",
            "score_away": team_scores[0] if len(team_scores) > 0 else "",
            "score_home": team_scores[1] if len(team_scores) > 1 else "",
            "wagers_away": wagers_percents[0] if len(wagers_percents) > 0 else "",
            "wagers_home": wagers_percents[1] if len(wagers_percents) > 1 else "",
            "opener_away": opener_odds[0] if len(opener_odds) > 0 else "",
            "opener_home": opener_odds[1] if len(opener_odds) > 1 else "",
        }

        # Add sportsbook odds (flattened, e.g., betmgm_away, betmgm_home, etc.)
        sportsbook_names = ["betmgm", "fanduel", "caesars", "bet365", "draftkings", "betrivers"]
        for i, sb in enumerate(sportsbook_names):
            if i < len(sportsbook_odds):
                row[f"{sb}_away"] = sportsbook_odds[i][0] if len(sportsbook_odds[i]) > 0 else ""
                row[f"{sb}_home"] = sportsbook_odds[i][1] if len(sportsbook_odds[i]) > 1 else ""
            else:
                row[f"{sb}_away"] = ""
                row[f"{sb}_home"] = ""

        all_rows.append(row)

    df = pd.DataFrame(all_rows)
    return df

def main():
    """
    Main execution function for the sportsbook scraper CLI.
    
    This function:
    1. Parses command line arguments
    2. Validates input parameters
    3. Initializes the appropriate scraper
    4. Executes the scraping process
    5. Saves results to file
    """
    # Parse command line arguments
    args = parser.parse_args()
    
    try:
        # Validate arguments
        validate_arguments(args)
        
        # Get appropriate scraper class
        scraper_class = get_scraper_class(args.sport)
        
        # Initialize scraper based on sport type
        if args.sport == "ncaa2ndhalf":
            print(f"🎯 Scraping {args.sport.upper()} data using dates file: {args.dates_file}")
            options = Options()
            options.headless = True
            service = Service(r"C:\\Drivers\\chromedriver-win64\\chromedriver.exe")
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("https://www.sportsbookreview.com/betting-odds/ncaa-basketball/pointspread/2nd-half/?date=2024-02-05")
            df = extract_ncaa_2ndhalf_games(driver)
            save_data(df, args.filename, args.format)
            driver.quit()
        else:
            # Generate list of years to scrape for other sports
            years_to_scrape = list(range(args.start, args.end + 1))
            print(f"🎯 Scraping {args.sport.upper()} data for years: {args.start}-{args.end}")
            scraper = scraper_class(years_to_scrape)
        
        # Execute scraping process
        print("🔄 Starting data collection...")
        data = scraper.driver()
        
        if data.empty:
            print("❌ No data collected. This may be normal for ncaa2ndhalf if no data is available for the specified dates.")
            return
        
        # Display summary statistics
        if args.sport == "ncaa2ndhalf":
            print(f"📊 Collected {len(data)} team records")
        else:
            print(f"📊 Collected {len(data)} games")
        
        if 'date' in data.columns and not data.empty:
            print(f"📅 Date range: {data['date'].min()} to {data['date'].max()}")
        
        # Save data to file
        save_data(data, args.filename, args.format)
        
        print("🎉 Scraping completed successfully!")
        
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
