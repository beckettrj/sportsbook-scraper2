"""
Sportsbook Review Scraper - Core Scraping Classes

This module contains the core scraping classes for extracting sports betting odds
data from sportsbookreview.com. It provides specialized scrapers for different
sports (NFL, NBA, NHL, MLB, NCAA Basketball) with sport-specific data parsing.

Each scraper class handles:
- URL construction for specific sports
- HTML table parsing and data extraction
- Data transformation and schema mapping
- Error handling for missing or malformed data

Key Features:
- Automatic team name translation
- Graceful handling of missing years
- Standardized data schema across sports
- Robust error handling and logging

Author: Finn Lancaster, Rod Beckett (NCAA add-on)
License: MIT
"""

import requests
import pandas as pd
from itertools import tee
import json
import io
from io import StringIO
from pandas.errors import EmptyDataError


class OddsScraper:
    """
    Base class for all sports odds scrapers.
    
    This class provides common functionality for scraping sports betting odds
    from sportsbookreview.com. It handles HTTP requests, data parsing, and
    provides utility methods for data transformation.
    
    Attributes:
        blacklist (list): Values to filter out from odds data (e.g., 'pk', 'NL')
        sport (str): Sport identifier (nfl, nba, nhl, mlb, ncaa)
        translator (dict): Team name translation mappings
        seasons (list): List of years to scrape
        base (str): Base URL for the sport's odds archive
        schema (dict): Data schema for the sport's output format
    """
    
    def __init__(self, sport, years):
        """
        Initialize the base scraper with sport and year configuration.
        
        Args:
            sport (str): Sport identifier for team name translation
            years (list): List of years to scrape data for
        """
        # Values to filter out from odds data (not valid odds)
        self.blacklist = [
            "pk",      # Pick'em (no spread)
            "PK",      # Pick'em (no spread)
            "NL",      # No line
            "nl",      # No line
            "a100",    # Various invalid odds formats
            "a105",
            "a110",
            ".5+03",   # Malformed odds
            ".5ev",    # Even odds (malformed)
            "-",       # Missing data
        ]
        self.sport = sport
        self.seasons = years
        
        # Load team name translation mappings
        try:
            with open("config/translated.json", "r") as f:
                self.translator = json.load(f)
        except FileNotFoundError:
            print("⚠️  Warning: config/translated.json not found. Using raw team names.")
            self.translator = {}

    def _translate(self, name):
        """
        Translate team name from website format to full name.
        
        Args:
            name (str): Team name as it appears on the website
            
        Returns:
            str: Translated team name or original name if no translation found
        """
        return self.translator.get(self.sport, {}).get(name, name)

    @staticmethod
    def _make_season(season):
        """
        Convert year to season format (e.g., 2021 -> "2021-22").
        
        Args:
            season (int): Year to convert
            
        Returns:
            str: Season string in format "YYYY-YY"
        """
        season = str(season)
        yr = season[2:]  # Extract last two digits
        next_yr = str(int(yr) + 1)  # Next year
        return f"{season}-{next_yr}"

    @staticmethod
    def _make_datestr(date, season, start=8, yr_end=12):
        """
        Convert date string to integer format for sorting and analysis.
        
        This method handles the conversion of date strings (e.g., "1109" for Nov 9)
        to integer format (e.g., 20211109) for proper chronological ordering.
        
        Args:
            date (str): Date string in format "MMDD"
            season (int): Season year
            start (int): Start month for season (default: 8 for August)
            yr_end (int): End month for season (default: 12 for December)
            
        Returns:
            int: Date in YYYYMMDD format
        """
        date = str(date)
        
        # Pad single-digit dates with leading zero
        if len(date) == 3:
            date = f"0{date}"
            
        month = date[:2]
        day = date[2:]

        # Determine if date belongs to current season or next season
        # For most sports, season starts in August/September and ends in following year
        if int(month) in range(start, yr_end + 1):
            return int(f"{season}{month}{day}")
        else:
            return int(f"{int(season) + 1}{month}{day}")

    @staticmethod
    def _pairwise(iterable):
        """
        Create pairs of consecutive items from an iterable.
        
        This is used to process game data where each game has two rows
        (one for each team) that need to be paired together.
        
        Args:
            iterable: Any iterable object
            
        Returns:
            zip: Iterator of consecutive pairs
        """
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    def driver(self):
        """
        Main driver method for scraping data across multiple seasons.
        
        This method orchestrates the scraping process by:
        1. Iterating through specified seasons
        2. Constructing URLs for each season
        3. Making HTTP requests with proper headers
        4. Parsing HTML tables
        5. Processing and transforming data
        6. Handling errors gracefully
        
        Returns:
            pandas.DataFrame: Processed data in standardized schema
        """
        df = pd.DataFrame()
        
        for season in self.seasons:
            # Construct season string and URL
            season_str = self._make_season(season)
            url = self.base + season_str
            
            # Set headers to avoid being blocked by the website
            headers = {"User-Agent": "Mozilla/5.0"}
            
            try:
                # Make HTTP request
                r = requests.get(url, headers=headers)
                
                # Parse HTML tables and process data
                dfs = pd.read_html(StringIO(r.text))
                df = pd.concat([df, self._reformat_data(dfs[0][1:], season)], axis=0)
                
            except ValueError as e:
                # Handle cases where no tables are found (year not available)
                print(f"Warning: No tables found for {self.sport.upper()} {season_str} ({url}) - skipping.")
                continue
                
        return self._to_schema(df)


class NFLOddsScraper(OddsScraper):
    """
    NFL (National Football League) odds scraper.
    
    This class handles scraping NFL betting odds data from sportsbookreview.com.
    NFL data includes quarter-by-quarter scores, spreads, totals, and money lines.
    
    Data Schema:
    - Quarter scores (1st, 2nd, 3rd, 4th)
    - Final scores
    - Opening and closing spreads
    - Opening and closing totals (over/under)
    - Money lines
    - Second half spreads and totals
    
    URL Format: https://www.sportsbookreviewsonline.com/scoresoddsarchives/nfl-odds-YYYY-YY
    """
    
    def __init__(self, years):
        """
        Initialize NFL scraper with specified years.
        
        Args:
            years (list): List of years to scrape NFL data for
        """
        super().__init__("nfl", years)
        
        # Base URL for NFL odds archives
        self.base = (
            "https://www.sportsbookreviewsonline.com/scoresoddsarchives/nfl-odds-"
        )
        
        # Define the output schema for NFL data
        self.schema = {
            "season": [],           # Season year
            "date": [],             # Game date (YYYYMMDD)
            "home_team": [],        # Home team name
            "away_team": [],        # Away team name
            "home_1stQtr": [],      # Home team 1st quarter score
            "away_1stQtr": [],      # Away team 1st quarter score
            "home_2ndQtr": [],      # Home team 2nd quarter score
            "away_2ndQtr": [],      # Away team 2nd quarter score
            "home_3rdQtr": [],      # Home team 3rd quarter score
            "away_3rdQtr": [],      # Away team 3rd quarter score
            "home_4thQtr": [],      # Home team 4th quarter score
            "away_4thQtr": [],      # Away team 4th quarter score
            "home_final": [],       # Home team final score
            "away_final": [],       # Away team final score
            "home_close_ml": [],    # Home team closing money line
            "away_close_ml": [],    # Away team closing money line
            "home_open_spread": [], # Home team opening spread
            "away_open_spread": [], # Away team opening spread
            "home_close_spread": [], # Home team closing spread
            "away_close_spread": [], # Away team closing spread
            "home_2H_spread": [],   # Home team 2nd half spread
            "away_2H_spread": [],   # Away team 2nd half spread
            "2H_total": [],         # 2nd half total (over/under)
            "open_over_under": [],  # Opening total (over/under)
            "close_over_under": [], # Closing total (over/under)
        }

    def _reformat_data(self, df, season):
        """
        Reformat raw HTML table data into structured format.
        
        This method extracts and cleans data from the HTML table, handling
        missing values and converting data types appropriately.
        
        Args:
            df (pandas.DataFrame): Raw data from HTML table
            season (int): Season year being processed
            
        Returns:
            pandas.DataFrame: Cleaned and structured data
        """
        new_df = pd.DataFrame()
        
        # Add season information
        new_df["season"] = [season] * len(df)
        
        # Convert date strings to integer format
        new_df["date"] = df[0].apply(lambda x: self._make_datestr(x, season))
        
        # Extract team names and scores
        new_df["name"] = df[3]      # Team name
        new_df["1stQtr"] = df[4]    # 1st quarter score
        new_df["2ndQtr"] = df[5]    # 2nd quarter score
        new_df["3rdQtr"] = df[6]    # 3rd quarter score
        new_df["4thQtr"] = df[7]    # 4th quarter score
        new_df["final"] = df[8]     # Final score
        
        # Process opening odds (filter out invalid values)
        _open = df[9].apply(lambda x: 0 if x in self.blacklist else x)
        new_df["open_odds"] = _open
        
        # Process closing odds (filter out invalid values)
        close = df[10].apply(lambda x: 0 if x in self.blacklist else x)
        new_df["close_odds"] = close
        
        # Extract money line
        new_df["close_ml"] = df[11]
        
        # Process 2nd half odds (filter out invalid values)
        h2 = df[12].apply(lambda x: 0 if x in self.blacklist else x)
        new_df["2H_odds"] = h2
        
        return new_df

    def _to_schema(self, df):
        """
        Transform processed data into final schema format.
        
        This method pairs consecutive rows (home/away teams) and calculates
        spreads, totals, and other derived statistics. It handles the complex
        logic of determining which team is home/away and calculating proper
        spread values.
        
        Args:
            df (pandas.DataFrame): Processed data from _reformat_data
            
        Returns:
            pandas.DataFrame: Final data in standardized schema
        """
        new_df = self.schema.copy()
        df = df.fillna(0)  # Replace NaN values with 0
        
        # Create iterator for processing rows in pairs
        progress = df.iterrows()
        next(progress)  # Skip header row
        
        # Process each pair of rows (home and away teams)
        for (i1, row), (i2, next_row) in self._pairwise(progress):
            # Skip every other row to avoid processing same game twice
            if i1 % 2 == 0:
                continue

            # Extract money lines for determining home/away
            home_ml = int(next_row["close_ml"])
            away_ml = int(row["close_ml"])

            # Determine which odds represent spread vs total
            odds1 = float(row["open_odds"])
            odds2 = float(next_row["open_odds"])
            
            if odds1 < odds2:
                # odds1 is spread, odds2 is total
                open_spread = odds1
                close_spread = float(row["close_odds"])
                h2_spread = float(row["2H_odds"])

                h2_total = float(next_row["2H_odds"])
                open_ou = odds2
                close_ou = float(next_row["close_odds"])
            else:
                # odds2 is spread, odds1 is total
                open_spread = odds2
                close_spread = float(next_row["close_odds"])
                h2_spread = float(next_row["2H_odds"])

                h2_total = float(row["2H_odds"])
                open_ou = odds1
                close_ou = float(row["close_odds"])

            # Calculate proper spread values (negative for underdog)
            home_open_spread = -open_spread if home_ml < away_ml else open_spread
            away_open_spread = -home_open_spread
            home_close_spread = -close_spread if home_ml < away_ml else close_spread
            away_close_spread = -home_close_spread
            h2_home_spread = -h2_spread if home_ml < away_ml else h2_spread
            h2_away_spread = -h2_home_spread

            # Build the final data row
            new_df["season"].append(row["season"])
            new_df["date"].append(row["date"])
            new_df["home_team"].append(self._translate(next_row["name"]))
            new_df["away_team"].append(self._translate(row["name"]))
            
            # Quarter scores
            new_df["home_1stQtr"].append(next_row["1stQtr"])
            new_df["away_1stQtr"].append(row["1stQtr"])
            new_df["home_2ndQtr"].append(next_row["2ndQtr"])
            new_df["away_2ndQtr"].append(row["2ndQtr"])
            new_df["home_3rdQtr"].append(next_row["3rdQtr"])
            new_df["away_3rdQtr"].append(row["3rdQtr"])
            new_df["home_4thQtr"].append(next_row["4thQtr"])
            new_df["away_4thQtr"].append(row["4thQtr"])
            
            # Final scores
            new_df["home_final"].append(next_row["final"])
            new_df["away_final"].append(row["final"])
            
            # Money lines
            new_df["home_close_ml"].append(home_ml)
            new_df["away_close_ml"].append(away_ml)
            
            # Spreads
            new_df["home_open_spread"].append(home_open_spread)
            new_df["away_open_spread"].append(away_open_spread)
            new_df["home_close_spread"].append(home_close_spread)
            new_df["away_close_spread"].append(away_close_spread)
            new_df["home_2H_spread"].append(h2_home_spread)
            new_df["away_2H_spread"].append(h2_away_spread)
            
            # Totals (over/under)
            new_df["2H_total"].append(h2_total)
            new_df["open_over_under"].append(open_ou)
            new_df["close_over_under"].append(close_ou)

        return pd.DataFrame(new_df)


# NBA is the same as NFL, so we can subclass the NFL scraper
class NBAOddsScraper(NFLOddsScraper):
    """
    NBA (National Basketball Association) odds scraper.
    
    This class inherits from NFLOddsScraper since NBA and NFL have identical
    data structures and processing logic. NBA data includes quarter-by-quarter
    scores, spreads, totals, and money lines.
    
    Data Schema: Same as NFL (quarter scores, spreads, totals, money lines)
    URL Format: https://www.sportsbookreviewsonline.com/scoresoddsarchives/nba-odds-YYYY-YY
    """
    
    def __init__(self, years):
        """
        Initialize NBA scraper with specified years.
        
        Args:
            years (list): List of years to scrape NBA data for
        """
        super().__init__(years)
        self.sport = "nba"
        
        # Base URL for NBA odds archives
        self.base = (
            "https://www.sportsbookreviewsonline.com/scoresoddsarchives/nba-odds-"
        )


# NHL is the same as NFL, so we can subclass the NFL scraper
class NHLOddsScraper(OddsScraper):
    def __init__(self, years):
        super().__init__("nhl", years)
        self.base = (
            "https://www.sportsbookreviewsonline.com/scoresoddsarchives/nhl-odds-"
        )
        self.schema = {
            "season": [],
            "date": [],
            "home_team": [],
            "away_team": [],
            "home_1stPeriod": [],
            "away_1stPeriod": [],
            "home_2ndPeriod": [],
            "away_2ndPeriod": [],
            "home_3rdPeriod": [],
            "away_3rdPeriod": [],
            "home_final": [],
            "away_final": [],
            "home_open_ml": [],
            "away_open_ml": [],
            "home_close_ml": [],
            "away_close_ml": [],
            "home_close_spread": [],
            "away_close_spread": [],
            "home_close_spread_odds": [],
            "away_close_spread_odds": [],
            "open_over_under": [],
            "open_over_under_odds": [],
            "close_over_under": [],
            "close_over_under_odds": [],
        }

    def _reformat_data(self, df, season, covid=False):
        new_df = pd.DataFrame()
        new_df["season"] = [season] * len(df)
        new_df["date"] = df[0].apply(
            lambda x: (
                self._make_datestr(x, season)
                if not covid
                else self._make_datestr(x, season, start=1, yr_end=3)
            )
        )
        new_df["name"] = df[3]
        new_df["1stPeriod"] = df[4]
        new_df["2ndPeriod"] = df[5]
        new_df["3rdPeriod"] = df[6]
        new_df["final"] = df[7]
        new_df["open_ml"] = df[8]
        new_df["open_ml"] = new_df["open_ml"].apply(
            lambda x: 0 if x in self.blacklist else x
        )
        new_df["close_ml"] = df[9]
        new_df["close_ml"] = new_df["close_ml"].apply(
            lambda x: 0 if x in self.blacklist else x
        )
        new_df["close_spread"] = df[10] if season > 2013 else 0
        new_df["close_spread"] = new_df["close_spread"].apply(
            lambda x: 0 if x in self.blacklist else float(x)
        )
        new_df["close_spread_odds"] = df[11] if season > 2013 else 0
        new_df["close_spread_odds"] = new_df["close_spread_odds"].apply(
            lambda x: 0 if x in self.blacklist else float(x)
        )
        new_df["open_over_under"] = df[12] if season > 2013 else df[10]
        new_df["open_over_under"] = new_df["open_over_under"].apply(
            lambda x: 0 if x in self.blacklist else float(x)
        )
        new_df["open_over_under_odds"] = df[13] if season > 2013 else df[11]
        new_df["open_over_under_odds"] = new_df["open_over_under_odds"].apply(
            lambda x: 0 if x in self.blacklist else float(x)
        )
        new_df["close_over_under"] = df[14] if season > 2013 else df[12]
        new_df["close_over_under"] = new_df["close_over_under"].apply(
            lambda x: 0 if x in self.blacklist else float(x)
        )
        new_df["close_over_under_odds"] = df[15] if season > 2013 else df[13]
        new_df["close_over_under_odds"] = new_df["close_over_under_odds"].apply(
            lambda x: 0 if x in self.blacklist else float(x)
        )

        return new_df

    def _to_schema(self, df):
        new_df = self.schema.copy()
        df = df.fillna(0)
        progress = df.iterrows()
        # remove the first row, as it is the header
        next(progress)
        for (i1, row), (i2, next_row) in self._pairwise(progress):
            # skip every other row
            if i1 % 2 == 0:
                continue

            new_df["season"].append(row["season"])
            new_df["date"].append(row["date"])
            new_df["home_team"].append(self._translate(next_row["name"]))
            new_df["away_team"].append(self._translate(row["name"]))
            new_df["home_1stPeriod"].append(next_row["1stPeriod"])
            new_df["away_1stPeriod"].append(row["1stPeriod"])
            new_df["home_2ndPeriod"].append(next_row["2ndPeriod"])
            new_df["away_2ndPeriod"].append(row["2ndPeriod"])
            new_df["home_3rdPeriod"].append(next_row["3rdPeriod"])
            new_df["away_3rdPeriod"].append(row["3rdPeriod"])
            new_df["home_final"].append(next_row["final"])
            new_df["away_final"].append(row["final"])
            new_df["home_open_ml"].append(int(next_row["open_ml"]))
            new_df["away_open_ml"].append(int(row["open_ml"]))
            new_df["home_close_ml"].append(int(next_row["close_ml"]))
            new_df["away_close_ml"].append(int(row["close_ml"]))
            new_df["home_close_spread"].append(next_row["close_spread"])
            new_df["away_close_spread"].append(row["close_spread"])
            new_df["home_close_spread_odds"].append(next_row["close_spread_odds"])
            new_df["away_close_spread_odds"].append(row["close_spread_odds"])
            new_df["open_over_under"].append(next_row["open_over_under"])
            new_df["open_over_under_odds"].append(next_row["open_over_under_odds"])
            new_df["close_over_under"].append(next_row["close_over_under"])
            new_df["close_over_under_odds"].append(next_row["close_over_under_odds"])

        return pd.DataFrame(new_df)

    def driver(self):
        dfs = pd.DataFrame()
        for season in self.seasons:
            # compensate for the COVID shortened season in 2021
            season_str = self._make_season(season) if season != 2020 else "2021"
            is_cov = True if season == 2020 else False
            url = self.base + season_str

            # Sportsbookreview has scraper protection, so we need to set a user agent
            # to get around this.
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers)

            dfs = pd.concat(
                [dfs, self._reformat_data(pd.read_html(StringIO(r.text))[0][1:], season, is_cov)],
                axis=0,
            )

        return self._to_schema(dfs)


# MLB has a different format, so we need to subclass the OddsScraper
class MLBOddsScraper(OddsScraper):
    def __init__(self, years):
        super().__init__("mlb", years)
        self.base = "https://www.sportsbookreviewsonline.com/wp-content/uploads/sportsbookreviewsonline_com_737/mlb-odds-"
        self.ext = ".xlsx"
        self.schema = {
            "season": [],
            "date": [],
            "home_team": [],
            "away_team": [],
            "home_1stInn": [],
            "away_1stInn": [],
            "home_2ndInn": [],
            "away_2ndInn": [],
            "home_3rdInn": [],
            "away_3rdInn": [],
            "home_4thInn": [],
            "away_4thInn": [],
            "home_5thInn": [],
            "away_5thInn": [],
            "home_6thInn": [],
            "away_6thInn": [],
            "home_7thInn": [],
            "away_7thInn": [],
            "home_8thInn": [],
            "away_8thInn": [],
            "home_9thInn": [],
            "away_9thInn": [],
            "home_final": [],
            "away_final": [],
            "home_open_ml": [],
            "away_open_ml": [],
            "home_close_ml": [],
            "away_close_ml": [],
            "home_close_spread": [],
            "away_close_spread": [],
            "home_close_spread_odds": [],
            "away_close_spread_odds": [],
            "open_over_under": [],
            "open_over_under_odds": [],
            "close_over_under": [],
            "close_over_under_odds": [],
        }

    def _reformat_data(self, df, season):
        new_df = pd.DataFrame()
        new_df["season"] = [season] * len(df)
        new_df["date"] = df[0].apply(
            lambda x: self._make_datestr(x, season, start=3, yr_end=10)
        )
        new_df["name"] = df[3]
        new_df["1stInn"] = df[5]
        new_df["2ndInn"] = df[6]
        new_df["3rdInn"] = df[7]
        new_df["4thInn"] = df[8]
        new_df["5thInn"] = df[9]
        new_df["6thInn"] = df[10]
        new_df["7thInn"] = df[11]
        new_df["8thInn"] = df[12]
        new_df["9thInn"] = df[13]
        new_df["final"] = df[14]
        new_df["open_ml"] = df[15]
        new_df["close_ml"] = df[16]
        new_df["close_spread"] = df[17] if season > 2013 else 0
        new_df["close_spread_odds"] = df[18] if season > 2013 else 0
        new_df["open_over_under"] = df[19] if season > 2013 else df[17]
        new_df["open_over_under_odds"] = df[20] if season > 2013 else df[18]
        new_df["close_over_under"] = df[21] if season > 2013 else df[19]
        new_df["close_over_under_odds"] = df[22] if season > 2013 else df[20]

        return new_df

    def _to_schema(self, df):
        new_df = self.schema.copy()
        progress = df.iterrows()
        # remove the first row, as it is the header
        next(progress)
        for (i1, row), (i2, next_row) in self._pairwise(progress):
            if i1 % 2 != 0:
                continue

            new_df["season"].append(row["season"])
            new_df["date"].append(row["date"])
            new_df["home_team"].append(self._translate(next_row["name"]))
            new_df["away_team"].append(self._translate(row["name"]))
            new_df["home_1stInn"].append(next_row["1stInn"])
            new_df["away_1stInn"].append(row["1stInn"])
            new_df["home_2ndInn"].append(next_row["2ndInn"])
            new_df["away_2ndInn"].append(row["2ndInn"])
            new_df["home_3rdInn"].append(next_row["3rdInn"])
            new_df["away_3rdInn"].append(row["3rdInn"])
            new_df["home_4thInn"].append(next_row["4thInn"])
            new_df["away_4thInn"].append(row["4thInn"])
            new_df["home_5thInn"].append(next_row["5thInn"])
            new_df["away_5thInn"].append(row["5thInn"])
            new_df["home_6thInn"].append(next_row["6thInn"])
            new_df["away_6thInn"].append(row["6thInn"])
            new_df["home_7thInn"].append(next_row["7thInn"])
            new_df["away_7thInn"].append(row["7thInn"])
            new_df["home_8thInn"].append(next_row["8thInn"])
            new_df["away_8thInn"].append(row["8thInn"])
            new_df["home_9thInn"].append(next_row["9thInn"])
            new_df["away_9thInn"].append(row["9thInn"])
            new_df["home_final"].append(next_row["final"])
            new_df["away_final"].append(row["final"])
            new_df["home_open_ml"].append(next_row["open_ml"])
            new_df["away_open_ml"].append(row["open_ml"])
            new_df["home_close_ml"].append(next_row["close_ml"])
            new_df["away_close_ml"].append(row["close_ml"])
            new_df["home_close_spread"].append(next_row["close_spread"])
            new_df["away_close_spread"].append(row["close_spread"])
            new_df["home_close_spread_odds"].append(next_row["close_spread_odds"])
            new_df["away_close_spread_odds"].append(row["close_spread_odds"])
            new_df["open_over_under"].append(next_row["open_over_under"])
            new_df["open_over_under_odds"].append(next_row["open_over_under_odds"])
            new_df["close_over_under"].append(next_row["close_over_under"])
            new_df["close_over_under_odds"].append(next_row["close_over_under_odds"])

        return pd.DataFrame(new_df)

    def driver(self):
        dfs = pd.DataFrame()
        for season in self.seasons:
            url = self.base + str(season) + self.ext
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers)

            with io.BytesIO(r.content) as fh:
                df = pd.read_excel(fh, header=None, sheet_name=None)
            dfs = pd.concat(
                [dfs, self._reformat_data(df["Sheet1"][1:], season)], axis=0
            )

        return self._to_schema(dfs)


# NCAA Basketball follows the same format as NBA
class NCAABasketballOddsScraper(NBAOddsScraper):
    """
    NCAA Basketball odds scraper.
    
    This class handles scraping NCAA basketball betting odds data from
    sportsbookreview.com. NCAA data includes half-by-half scores, spreads,
    totals, and money lines.
    
    Data Schema:
    - Half scores (1st half, 2nd half)
    - Final scores
    - Opening and closing spreads
    - Opening and closing totals (over/under)
    - Money lines
    - Second half spreads and totals
    
    URL Format: https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaa-basketball-YYYY-YY/
    Note: NCAA URLs require trailing slash for proper access.
    """
    
    def __init__(self, years):
        """
        Initialize NCAA basketball scraper with specified years.
        
        Args:
            years (list): List of years to scrape NCAA data for
        """
        super().__init__(years)
        self.sport = "ncaa"
        
        # Base URL for NCAA basketball odds archives
        self.base = (
            "https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaa-basketball-"
        )
        
        # Define the output schema for NCAA data (different from NBA/NFL)
        self.schema = {
            "season": [],           # Season year
            "date": [],             # Game date (YYYYMMDD)
            "home_team": [],        # Home team name
            "away_team": [],        # Away team name
            "home_1st": [],         # Home team 1st half score
            "away_1st": [],         # Away team 1st half score
            "home_2nd": [],         # Home team 2nd half score
            "away_2nd": [],         # Away team 2nd half score
            "home_final": [],       # Home team final score
            "away_final": [],       # Away team final score
            "home_open": [],        # Home team opening spread
            "away_open": [],        # Away team opening spread
            "home_close": [],       # Home team closing spread
            "away_close": [],       # Away team closing spread
            "home_ml": [],          # Home team money line
            "away_ml": [],          # Away team money line
            "home_2H": [],          # Home team 2nd half spread
            "away_2H": [],          # Away team 2nd half spread
        }

    def _reformat_data(self, df, season):
        """
        Reformat raw HTML table data into structured format for NCAA basketball.
        
        NCAA basketball data has a different structure than NBA/NFL:
        - Uses half scores instead of quarters
        - Different column layout
        - V/H indicators for visitor/home teams
        
        Args:
            df (pandas.DataFrame): Raw data from HTML table
            season (int): Season year being processed
            
        Returns:
            pandas.DataFrame: Cleaned and structured data
        """
        new_df = pd.DataFrame()
        
        # Add season information
        new_df["season"] = [season] * len(df)
        
        # Convert date strings to integer format
        new_df["date"] = df[0].apply(lambda x: self._make_datestr(x, season))
        
        # Extract visitor/home indicator and team information
        new_df["VH"] = df[2]        # V = visitor, H = home
        new_df["team"] = df[3]      # Team name
        new_df["1st"] = df[4]       # 1st half score
        new_df["2nd"] = df[5]       # 2nd half score
        new_df["final"] = df[6]     # Final score
        
        # Extract odds data
        new_df["open"] = df[7]      # Opening spread/total
        new_df["close"] = df[8]     # Closing spread/total
        new_df["ml"] = df[9]        # Money line
        new_df["2H"] = df[10]       # 2nd half spread/total
        
        return new_df

    def _to_schema(self, df):
        """
        Transform processed NCAA data into final schema format.
        
        This method pairs consecutive rows (visitor/home teams) and organizes
        the data into a standardized schema. NCAA data uses V/H indicators
        to determine visitor vs home teams.
        
        Args:
            df (pandas.DataFrame): Processed data from _reformat_data
            
        Returns:
            pandas.DataFrame: Final data in standardized schema
        """
        new_df = self.schema.copy()
        df = df.fillna(0)  # Replace NaN values with 0
        
        # Create iterator for processing rows in pairs
        progress = df.iterrows()
        next(progress)  # Skip header row
        
        # Process each pair of rows (visitor and home teams)
        for (i1, row), (i2, next_row) in self._pairwise(progress):
            # NCAA: V = visitor (away), H = home
            # Only process pairs where first row is visitor and second is home
            if row["VH"] == "V" and next_row["VH"] == "H":
                # Build the final data row
                new_df["season"].append(row["season"])
                new_df["date"].append(row["date"])
                new_df["home_team"].append(self._translate(next_row["team"]))
                new_df["away_team"].append(self._translate(row["team"]))
                
                # Half scores
                new_df["home_1st"].append(next_row["1st"])
                new_df["away_1st"].append(row["1st"])
                new_df["home_2nd"].append(next_row["2nd"])
                new_df["away_2nd"].append(row["2nd"])
                
                # Final scores
                new_df["home_final"].append(next_row["final"])
                new_df["away_final"].append(row["final"])
                
                # Spreads and odds
                new_df["home_open"].append(next_row["open"])
                new_df["away_open"].append(row["open"])
                new_df["home_close"].append(next_row["close"])
                new_df["away_close"].append(row["close"])
                new_df["home_ml"].append(next_row["ml"])
                new_df["away_ml"].append(row["ml"])
                new_df["home_2H"].append(next_row["2H"])
                new_df["away_2H"].append(row["2H"])
                
        return pd.DataFrame(new_df)

    def driver(self):
        """
        Main driver method for scraping NCAA basketball data.
        
        Overrides the base driver method to handle NCAA-specific URL format
        which requires a trailing slash for proper access.
        
        Returns:
            pandas.DataFrame: Processed NCAA basketball data
        """
        df = pd.DataFrame()
        
        for season in self.seasons:
            # Construct season string and URL with trailing slash
            season_str = self._make_season(season)
            url = self.base + season_str + "/"  # NCAA requires trailing slash
            
            # Set headers to avoid being blocked by the website
            headers = {"User-Agent": "Mozilla/5.0"}
            
            try:
                # Make HTTP request
                r = requests.get(url, headers=headers)
                
                # Parse HTML tables and process data
                dfs = pd.read_html(StringIO(r.text))
                df = pd.concat([df, self._reformat_data(dfs[0][1:], season)], axis=0)
                
            except ValueError as e:
                # Handle cases where no tables are found (year not available)
                print(f"Warning: No tables found for NCAA {season_str} ({url}) - skipping.")
                continue
                
        return self._to_schema(df)


class NCAABasketball2ndHalf:
    """
    NCAA Basketball 2nd Half Odds Scraper.
    Scrapes 2nd half totals for NCAA basketball from sportsbookreview.com for a list of dates.

    Note: This scraper may not work for all dates as 2nd half totals data availability
    varies by date and the website uses dynamic JavaScript loading.

    **Requires Selenium and ChromeDriver for JavaScript-rendered tables.**
    Install with: pip install selenium
    Download ChromeDriver: https://sites.google.com/chromium.org/driver/

    Website table structure (when available):
    - Time: Game time
    - Rot: Rotation number
    - Teams: Two team names with scores
    - WAGERS %: Wagering percentage
    - OPENER: O/U indicator, total value, and odds
    - BetMGM, FanDuel, Caesars, bet365, DraftKings: Sportsbook odds

    Output: One CSV row per team, where each game becomes two rows (one per team)
    """
    def __init__(self, dates_file="NCAA-2ndHalf-dates"):
        self.sport = "ncaa2ndhalf"
        # Try multiple URL patterns since the data availability varies
        self.base_urls = [
            "https://www.sportsbookreview.com/betting-odds/ncaa-basketball/totals/2nd-half/",
            "https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaa-basketball-2nd-half/",
        ]
        self.dates = self._load_dates(dates_file)
        
        # Load team name translation mappings
        try:
            with open("config/translated.json", "r") as f:
                self.translator = json.load(f)
        except FileNotFoundError:
            print("⚠️  Warning: config/translated.json not found. Using raw team names.")
            self.translator = {}
        
        # Define the output schema for 2nd half data
        # Each game from website becomes 2 rows (one per team)
        self.schema = {
            "date": [],                    # Game date
            "time": [],                    # Game time
            "rotation": [],                # Rotation number
            "team": [],                    # Team name
            "opponent": [],                # Opponent team name
            "team_score": [],              # Team's score
            "opponent_score": [],          # Opponent's score
            "wagers_percent": [],          # Wagering percentage
            "opener_ou": [],               # O/U indicator (O or U)
            "opener_total": [],            # Opening total value
            "opener_odds": [],             # Opening odds
            "betmgm_total": [],            # BetMGM 2nd half total
            "betmgm_odds": [],             # BetMGM odds
            "fanduel_total": [],           # FanDuel 2nd half total
            "fanduel_odds": [],            # FanDuel odds
            "caesars_total": [],           # Caesars 2nd half total
            "caesars_odds": [],            # Caesars odds
            "bet365_total": [],            # bet365 2nd half total
            "bet365_odds": [],             # bet365 odds
            "draftkings_total": [],        # DraftKings 2nd half total
            "draftkings_odds": [],         # DraftKings odds
            "betrivers_total": [],         # BetRivers 2nd half total
            "betrivers_odds": [],          # BetRivers odds
        }

    def _load_dates(self, dates_file):
        """Load dates from file."""
        try:
            with open(dates_file, "r") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"⚠️  Warning: {dates_file} not found. No dates to process.")
            return []

    def _translate(self, name):
        """
        Translate team name from website format to full name.
        
        Args:
            name (str): Team name as it appears on the website
            
        Returns:
            str: Translated team name or original name if no translation found
        """
        return self.translator.get(self.sport, {}).get(name, name)

    def _parse_teams_and_scores(self, teams_text):
        """
        Parse teams and scores from the Teams column.
        
        Args:
            teams_text (str): Text containing both teams and scores
            
        Returns:
            tuple: (team1_name, team1_score, team2_name, team2_score)
        """
        try:
            # Handle common formats:
            # "Duke 75 - North Carolina 70"
            # "Duke 75 North Carolina 70"
            # "Duke 75 @ North Carolina 70"
            
            # Remove any extra whitespace
            teams_text = teams_text.strip()
            
            # Split by common separators
            if " - " in teams_text:
                parts = teams_text.split(" - ")
            elif " @ " in teams_text:
                parts = teams_text.split(" @ ")
            else:
                # Try to find where the second team starts
                # Look for pattern: Team1 Score Team2 Score
                words = teams_text.split()
                if len(words) >= 4:
                    # Try to find where the second team name starts
                    # Usually after the first score
                    for i in range(1, len(words) - 2):
                        try:
                            # Check if this position contains a score (number)
                            score1 = int(words[i])
                            # The next word should be the second team name
                            if i + 2 < len(words):
                                try:
                                    score2 = int(words[i + 2])
                                    # Found both scores, reconstruct parts
                                    team1_part = " ".join(words[:i+1])
                                    team2_part = " ".join(words[i+1:])
                                    parts = [team1_part, team2_part]
                                    break
                                except ValueError:
                                    continue
                        except ValueError:
                            continue
                    else:
                        # Fallback: split in the middle
                        words = teams_text.split()
                        mid = len(words) // 2
                        parts = [" ".join(words[:mid]), " ".join(words[mid:])]
                else:
                    return "Team1", 0, "Team2", 0
            
            if len(parts) != 2:
                return "Team1", 0, "Team2", 0
            
            # Parse first team and score
            team1_parts = parts[0].strip().split()
            if len(team1_parts) >= 2:
                try:
                    team1_score = int(team1_parts[-1])
                    team1_name = " ".join(team1_parts[:-1])
                except ValueError:
                    team1_name = parts[0].strip()
                    team1_score = 0
            else:
                team1_name = parts[0].strip()
                team1_score = 0
            
            # Parse second team and score
            team2_parts = parts[1].strip().split()
            if len(team2_parts) >= 2:
                try:
                    team2_score = int(team2_parts[-1])
                    team2_name = " ".join(team2_parts[:-1])
                except ValueError:
                    team2_name = parts[1].strip()
                    team2_score = 0
            else:
                team2_name = parts[1].strip()
                team2_score = 0
            
            return team1_name, team1_score, team2_name, team2_score
            
        except Exception as e:
            print(f"Error parsing teams and scores from '{teams_text}': {e}")
            return "Team1", 0, "Team2", 0

    def _parse_opener(self, opener_text):
        """
        Parse OPENER column which contains O/U indicator, total value, and odds.
        
        Args:
            opener_text (str): Text from OPENER column
            
        Returns:
            tuple: (ou_indicator, total_value, odds)
        """
        try:
            # Parse format like "O 75.5 -110" or "U 75.5 +110"
            parts = opener_text.split()
            if len(parts) >= 3:
                ou_indicator = parts[0]  # O or U
                total_value = float(parts[1])  # 75.5
                odds = parts[2]  # -110 or +110
                return ou_indicator, total_value, odds
            else:
                return "", 0, ""
        except:
            return "", 0, ""

    def _parse_sportsbook_odds(self, odds_text):
        """
        Parse sportsbook odds column which may contain total and odds.
        
        Args:
            odds_text (str): Text from sportsbook column
            
        Returns:
            tuple: (total_value, odds)
        """
        try:
            # Parse format like "75.5 -110" or just odds like "-110"
            parts = odds_text.split()
            if len(parts) >= 2:
                total_value = float(parts[0])
                odds = parts[1]
                return total_value, odds
            elif len(parts) == 1:
                # Only odds, no total
                return 0, parts[0]
            else:
                return 0, ""
        except:
            return 0, ""

    def _get_rendered_html(self, url, wait_time=5):
        """
        Use Selenium to load the page and return the fully rendered HTML.
        Args:
            url (str): The URL to load
            wait_time (int): Seconds to wait for JS to load
        Returns:
            str: Rendered HTML source
        """
        # Import Selenium only here
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        import time

        options = Options()
        options.headless = True
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        service = Service(r"C:\\Drivers\\chromedriver-win64\\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
        try:
            driver.get(url)
            time.sleep(wait_time)  # Wait for JS to load table
            html = driver.page_source
        finally:
            driver.quit()
        return html

    def _try_url_patterns(self, date):
        """
        Try different URL patterns to find available data using Selenium.
        Args:
            date (str): Date to search for
        Returns:
            tuple: (success, data) where success is bool and data is DataFrame or None
        """
        for base_url in self.base_urls:
            url_patterns = [
                f"{base_url}?date={date}",
                f"{base_url}{date}",
                f"{base_url}{date}/",
            ]
            for url in url_patterns:
                try:
                    print(f"🔗 Trying URL (Selenium): {url}")
                    html = self._get_rendered_html(url)
                    try:
                        dfs = pd.read_html(StringIO(html))
                        if dfs:
                            df = dfs[0]
                            if df.shape[1] > 1 and not str(df.iloc[0, 0]).lower().startswith('bet'):
                                print(f"✅ Found data at {url}")
                                return True, df
                            else:
                                print(f"⚠️  Found table but appears to be promo content")
                        else:
                            print(f"⚠️  No tables found at {url}")
                    except Exception as e:
                        print(f"⚠️  Error parsing tables: {e}")
                except Exception as e:
                    print(f"❌ Error accessing {url} with Selenium: {e}")
        return False, None

    def _reformat_data(self, df, date):
        """
        Reformat raw HTML table data into structured format.
        
        Args:
            df (pandas.DataFrame): Raw data from HTML table
            date (str): Date being processed
            
        Returns:
            pandas.DataFrame: Cleaned and structured data
        """
        new_df = self.schema.copy()
        
        # Process each row (each row represents one game)
        for _, row in df.iterrows():
            try:
                # Extract basic game info
                time = row.iloc[0] if len(row) > 0 else ""  # Time column
                rotation = row.iloc[1] if len(row) > 1 else ""  # Rotation column
                teams_text = row.iloc[2] if len(row) > 2 else ""  # Teams column
                wagers = row.iloc[3] if len(row) > 3 else ""  # WAGERS % column
                opener = row.iloc[4] if len(row) > 4 else ""  # OPENER column
                
                # Parse teams and scores
                team1_name, team1_score, team2_name, team2_score = self._parse_teams_and_scores(teams_text)
                
                # Parse opener
                ou_indicator, opener_total, opener_odds = self._parse_opener(opener)
                
                # Parse sportsbook odds (columns 5-10)
                sportsbooks = []
                for i in range(5, min(11, len(row))):
                    total, odds = self._parse_sportsbook_odds(row.iloc[i] if i < len(row) else "")
                    sportsbooks.append((total, odds))
                
                # Ensure we have enough sportsbook data
                while len(sportsbooks) < 6:
                    sportsbooks.append((0, ""))
                
                # Create two rows - one for each team
                for team_idx in range(2):
                    if team_idx == 0:
                        team_name = team1_name
                        team_score = team1_score
                        opponent_name = team2_name
                        opponent_score = team2_score
                    else:
                        team_name = team2_name
                        team_score = team2_score
                        opponent_name = team1_name
                        opponent_score = team1_score
                    
                    # Add data to schema
                    new_df["date"].append(date)
                    new_df["time"].append(time)
                    new_df["rotation"].append(rotation)
                    new_df["team"].append(self._translate(team_name))
                    new_df["opponent"].append(self._translate(opponent_name))
                    new_df["team_score"].append(team_score)
                    new_df["opponent_score"].append(opponent_score)
                    new_df["wagers_percent"].append(wagers)
                    new_df["opener_ou"].append(ou_indicator)
                    new_df["opener_total"].append(opener_total)
                    new_df["opener_odds"].append(opener_odds)
                    
                    # Add sportsbook data
                    new_df["betmgm_total"].append(sportsbooks[0][0])
                    new_df["betmgm_odds"].append(sportsbooks[0][1])
                    new_df["fanduel_total"].append(sportsbooks[1][0])
                    new_df["fanduel_odds"].append(sportsbooks[1][1])
                    new_df["caesars_total"].append(sportsbooks[2][0])
                    new_df["caesars_odds"].append(sportsbooks[2][1])
                    new_df["bet365_total"].append(sportsbooks[3][0])
                    new_df["bet365_odds"].append(sportsbooks[3][1])
                    new_df["draftkings_total"].append(sportsbooks[4][0])
                    new_df["draftkings_odds"].append(sportsbooks[4][1])
                    new_df["betrivers_total"].append(sportsbooks[5][0])
                    new_df["betrivers_odds"].append(sportsbooks[5][1])
                    
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        return pd.DataFrame(new_df)

    def driver(self):
        """
        Main driver method for scraping 2nd half data across multiple dates.
        
        Returns:
            pandas.DataFrame: Processed 2nd half data
        """
        all_data = []
        successful_dates = 0
        
        print(f"🎯 Starting 2nd half totals scraping for {len(self.dates)} dates")
        print("⚠️  Note: 2nd half totals data availability varies by date")
        
        for date in self.dates:
            print(f"\n📅 Processing date: {date}")
            
            # Try to find data using different URL patterns
            success, df = self._try_url_patterns(date)
            
            if success and df is not None:
                try:
                    # Process the data
                    processed_df = self._reformat_data(df, date)
                    if not processed_df.empty:
                        all_data.append(processed_df)
                        successful_dates += 1
                        print(f"✅ Successfully processed {len(processed_df)} team records for {date}")
                    else:
                        print(f"⚠️  No valid data extracted for {date}")
                except Exception as e:
                    print(f"❌ Error processing data for {date}: {e}")
            else:
                print(f"❌ No data available for {date}")
        
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            print(f"\n🎉 Scraping completed!")
            print(f"📊 Successfully processed {successful_dates}/{len(self.dates)} dates")
            print(f"📊 Total team records: {len(final_df)}")
            return final_df
        else:
            print(f"\n❌ No data collected from any dates")
            print(f"💡 This may be due to:")
            print(f"   - No 2nd half totals available for the specified dates")
            print(f"   - Website structure changes")
            print(f"   - Data requires JavaScript rendering")
            return pd.DataFrame()
