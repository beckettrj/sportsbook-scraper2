#!/usr/bin/env python3
"""
Sportsbook Review Scraper - Command Line Interface

This module provides the main entry point for the sportsbook scraper application.
It handles command line argument parsing, validation, and orchestrates the scraping process.

Supported sports: NFL, NBA, NHL, MLB, NCAA Basketball
Year range: 2007-2023 (configurable in config.py)

Author: Finn Lancaster
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
)

# Configure command line argument parser
parser = argparse.ArgumentParser(
    description="Scrape sports betting odds data from sportsbookreview.com",
    epilog="Example: python cli.py --sport nfl --start 2020 --end 2021 --filename nfl_2020_2021"
)

# Required arguments
parser.add_argument(
    "--sport", 
    type=str, 
    required=True,
    choices=["nfl", "nba", "nhl", "mlb", "ncaa"],
    help="Sport to scrape data for (nfl, nba, nhl, mlb, ncaa)"
)

parser.add_argument(
    "--start", 
    type=int, 
    required=True,
    help="Start year for data scraping (inclusive)"
)

parser.add_argument(
    "--end", 
    type=int, 
    required=True,
    help="End year for data scraping (inclusive)"
)

parser.add_argument(
    "--filename", 
    type=str, 
    required=True,
    help="Output filename (without extension)"
)

# Optional arguments
parser.add_argument(
    "--format", 
    type=str, 
    default="json",
    choices=["json", "csv"],
    help="Output format (default: json)"
)

def validate_arguments(args):
    """
    Validate command line arguments against configuration constraints.
    
    Args:
        args: Parsed command line arguments
        
    Raises:
        ValueError: If arguments are invalid
    """
    # Check year range against configured limits
    if args.start < config.MIN_YEAR or args.end > config.MAX_YEAR:
        raise ValueError(
            f"Invalid year range. Must be between {config.MIN_YEAR} and {config.MAX_YEAR}."
        )
    
    # Ensure start year is before or equal to end year
    if args.start > args.end:
        raise ValueError("Invalid year range. Start year must be before or equal to end year.")

def get_scraper_class(sport):
    """
    Get the appropriate scraper class for the specified sport.
    
    Args:
        sport (str): Sport identifier (nfl, nba, nhl, mlb, ncaa)
        
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
        
        # Generate list of years to scrape
        years_to_scrape = list(range(args.start, args.end + 1))
        print(f"🎯 Scraping {args.sport.upper()} data for years: {args.start}-{args.end}")
        
        # Get appropriate scraper class and initialize
        scraper_class = get_scraper_class(args.sport)
        scraper = scraper_class(years_to_scrape)
        
        # Execute scraping process
        print("🔄 Starting data collection...")
        data = scraper.driver()
        
        # Display summary statistics
        print(f"📊 Collected {len(data)} games")
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
