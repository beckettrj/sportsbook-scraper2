#!/usr/bin/env python3
"""
Test script to parse JSON data from sportsbookreview.com for NCAA basketball 2nd half totals.
Now supports multiple dates from a dates file.
"""

import json
import pandas as pd
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import re
import os

def load_dates_from_file(dates_file_path):
    """
    Load dates from the specified file.
    """
    print(f"📅 Loading dates from: {dates_file_path}")
    
    if not os.path.exists(dates_file_path):
        print(f"❌ Dates file not found: {dates_file_path}")
        return []
    
    try:
        with open(dates_file_path, 'r') as f:
            dates = [line.strip() for line in f if line.strip()]
        
        print(f"✅ Loaded {len(dates)} dates: {dates}")
        return dates
    except Exception as e:
        print(f"❌ Error loading dates file: {e}")
        return []

def fetch_json_data_with_selenium(url):
    """
    Use Selenium to load the page and extract the embedded JSON data.
    Uses the exact setup from cli.py
    """
    print(f"🌐 Using Selenium to fetch: {url}")
    
    # Use the exact Selenium setup from cli.py
    options = Options()
    options.headless = True
    service = Service(r"C:\\Drivers\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for JS to render
        html = driver.page_source
        
        # Look for the <script> tag containing the JSON (look for 'props')
        # This regex finds the first {"props": ... } object in the HTML
        match = re.search(r'(\{\s*"props"[\s\S]+?\})<\/script>', html)
        if not match:
            # Try a more greedy match (to the last closing brace)
            match = re.search(r'(\{\s*"props"[\s\S]+?\})', html)
        
        if match:
            json_text = match.group(1)
            try:
                data = json.loads(json_text)
                print("✅ Successfully extracted JSON from Selenium page source")
                return data
            except Exception as e:
                print(f"❌ Error parsing JSON: {e}")
                return None
        else:
            print("❌ Could not find JSON in page source")
            return None
    finally:
        driver.quit()

def parse_json_odds_data(json_data, date):
    """
    Parse the JSON data from sportsbookreview.com and extract odds information.
    Creates 2 rows per game (one for each team).
    """
    print(f"🔍 Parsing JSON odds data for {date}")
    print("=" * 50)
    
    # Parse the JSON data
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Extract the odds tables
    odds_tables = data.get('props', {}).get('pageProps', {}).get('oddsTables', [])
    
    if not odds_tables:
        print("❌ No odds tables found in JSON data")
        return None
    
    print(f"📊 Found {len(odds_tables)} odds table(s)")
    
    all_games = []
    
    for table in odds_tables:
        league = table.get('league', 'Unknown')
        print(f"🏀 Processing {league} data")
        
        game_rows = table.get('oddsTableModel', {}).get('gameRows', [])
        print(f"   📋 Found {len(game_rows)} games")
        
        for game_row in game_rows:
            game_view = game_row.get('gameView', {})
            odds_views = game_row.get('oddsViews', [])
            
            # Extract basic game information
            game_id = game_view.get('gameId')
            start_date = game_view.get('startDate')
            game_status = game_view.get('gameStatusText', 'Unknown')
            
            # Extract team information
            away_team = game_view.get('awayTeam', {})
            home_team = game_view.get('homeTeam', {})
            
            away_name = away_team.get('displayName', away_team.get('name', 'Unknown'))
            home_name = home_team.get('displayName', home_team.get('name', 'Unknown'))
            away_score = game_view.get('awayTeamScore', 0)
            home_score = game_view.get('homeTeamScore', 0)
            
            # Extract venue information
            venue = game_view.get('venueName', 'Unknown')
            city = game_view.get('city', 'Unknown')
            state = game_view.get('state', 'Unknown')
            
            # Extract consensus data
            consensus = game_view.get('consensus', {})
            over_pick_percent = consensus.get('overPickPercent', 0) if consensus else 0
            under_pick_percent = consensus.get('underPickPercent', 0) if consensus else 0
            
            # Create two rows - one for each team
            for team_type, team_name, team_score in [('away', away_name, away_score), ('home', home_name, home_score)]:
                # Initialize game data
                game_data = {
                    'scrape_date': date,  # Add the date we're scraping for
                    'game_id': game_id,
                    'start_date': start_date,
                    'game_status': game_status,
                    'team_type': team_type,
                    'team_name': team_name,
                    'team_score': team_score,
                    'opponent_name': home_name if team_type == 'away' else away_name,
                    'opponent_score': home_score if team_type == 'away' else away_score,
                    'venue': venue,
                    'city': city,
                    'state': state,
                    'over_pick_percent': over_pick_percent,
                    'under_pick_percent': under_pick_percent,
                }
                
                # Extract odds from each sportsbook
                sportsbooks = ['betmgm', 'fanduel', 'caesars', 'bet365', 'draftkings', 'betrivers']
                
                for i, sportsbook in enumerate(sportsbooks):
                    if i < len(odds_views) and odds_views[i]:
                        odds_view = odds_views[i]
                        sportsbook_name = odds_view.get('sportsbook', sportsbook)
                        
                        # Extract opening line
                        opening_line = odds_view.get('openingLine', {})
                        opening_over_odds = opening_line.get('overOdds')
                        opening_under_odds = opening_line.get('underOdds')
                        opening_total = opening_line.get('total')
                        
                        # Extract current line
                        current_line = odds_view.get('currentLine', {})
                        current_over_odds = current_line.get('overOdds')
                        current_under_odds = current_line.get('underOdds')
                        current_total = current_line.get('total')
                        
                        # Add to game data
                        game_data[f'{sportsbook_name}_opening_over_odds'] = opening_over_odds
                        game_data[f'{sportsbook_name}_opening_under_odds'] = opening_under_odds
                        game_data[f'{sportsbook_name}_opening_total'] = opening_total
                        game_data[f'{sportsbook_name}_current_over_odds'] = current_over_odds
                        game_data[f'{sportsbook_name}_current_under_odds'] = current_under_odds
                        game_data[f'{sportsbook_name}_current_total'] = current_total
                    else:
                        # No odds available for this sportsbook
                        game_data[f'{sportsbook}_opening_over_odds'] = None
                        game_data[f'{sportsbook}_opening_under_odds'] = None
                        game_data[f'{sportsbook}_opening_total'] = None
                        game_data[f'{sportsbook}_current_over_odds'] = None
                        game_data[f'{sportsbook}_current_under_odds'] = None
                        game_data[f'{sportsbook}_current_total'] = None
                
                all_games.append(game_data)
    
    # Convert to DataFrame
    if all_games:
        df = pd.DataFrame(all_games)
        print(f"✅ Successfully parsed {len(df)} team rows ({len(df)//2} games) for {date}")
        return df
    else:
        print(f"❌ No games found in data for {date}")
        return None

def display_sample_data(df, num_rows=6):
    """
    Display a sample of the parsed data.
    """
    if df is None or df.empty:
        print("❌ No data to display")
        return
    
    print(f"\n📊 Sample Data (first {num_rows} rows):")
    print("=" * 120)
    
    # Select key columns for display
    display_cols = [
        'scrape_date', 'game_id', 'team_type', 'team_name', 'team_score', 'opponent_name', 'opponent_score',
        'game_status', 'venue', 'city', 'state',
        'fanduel_current_total', 'fanduel_current_over_odds', 'fanduel_current_under_odds',
        'draftkings_current_total', 'draftkings_current_over_odds', 'draftkings_current_under_odds'
    ]
    
    # Filter to columns that exist
    existing_cols = [col for col in display_cols if col in df.columns]
    
    print(df[existing_cols].head(num_rows).to_string(index=False))

def save_to_csv(df, filename):
    """
    Save the parsed data to a CSV file.
    """
    if df is None or df.empty:
        print("❌ No data to save")
        return
    
    try:
        df.to_csv(filename, index=False)
        print(f"✅ Data saved to {filename}")
        print(f"📊 Saved {len(df)} team rows ({len(df)//2} games) with {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Error saving data: {e}")

def main():
    """
    Main function to scrape multiple dates and save to timestamped CSV.
    """
    # Load dates from file
    dates_file_path = "data/NCAA-2ndHalf-dates.txt"
    dates = load_dates_from_file(dates_file_path)
    
    if not dates:
        print("❌ No dates to process")
        return
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"data/ncaa_2ndhalf_odds_{timestamp}.csv"
    
    print(f"📁 Output file: {output_filename}")
    print("=" * 60)
    
    # Initialize empty DataFrame to collect all data
    all_data = []
    
    # Process each date
    for i, date in enumerate(dates, 1):
        print(f"\n🔄 Processing date {i}/{len(dates)}: {date}")
        
        # Construct URL for this date
        url = f"https://www.sportsbookreview.com/betting-odds/ncaa-basketball/totals/2nd-half/?date={date}"
        
        # Use Selenium to fetch the data
        json_data = fetch_json_data_with_selenium(url)
        
        if json_data is None:
            print(f"❌ Failed to fetch data for {date}, skipping...")
            continue
        
        # Parse the data
        df = parse_json_odds_data(json_data, date)
        
        if df is not None:
            # Add to our collection
            all_data.append(df)
            print(f"✅ Added {len(df)} rows for {date}")
        else:
            print(f"❌ No data parsed for {date}")
        
        # Small delay between requests
        if i < len(dates):
            print("⏳ Waiting 10 seconds before next request...")
            time.sleep(10)
    
    # Combine all data
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Display sample data if we want to debug
        # display_sample_data(combined_df) 
        
        # Save to CSV
        save_to_csv(combined_df, output_filename)
        
        print(f"\n🎉 Successfully processed all dates!")
        print(f"📊 Total team rows: {len(combined_df)}")
        print(f"📊 Total games: {len(combined_df)//2}")
        print(f"📋 Total columns: {len(combined_df.columns)}")
        
        # Show some statistics
        print(f"\n📈 Data Summary:")
        print(f"   • Dates processed: {len(dates)}")
        print(f"   • Games with FanDuel odds: {combined_df['fanduel_current_total'].notna().sum()//2}")
        print(f"   • Games with DraftKings odds: {combined_df['draftkings_current_total'].notna().sum()//2}")
        print(f"   • Games with BetRivers odds: {combined_df['bet_rivers_ny_current_total'].notna().sum()//2}")
        print(f"   • Average over pick percentage: {combined_df['over_pick_percent'].mean():.1f}%")
        print(f"   • Average under pick percentage: {combined_df['under_pick_percent'].mean():.1f}%")
        
        # Show breakdown by date
        print(f"\n📅 Data by Date:")
        date_counts = combined_df['scrape_date'].value_counts().sort_index()
        for date, count in date_counts.items():
            print(f"   • {date}: {count} team rows ({count//2} games)")
        
    else:
        print("\n❌ No data collected from any dates")

if __name__ == "__main__":
    main() 