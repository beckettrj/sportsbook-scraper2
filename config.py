"""
Sportsbook Review Scraper - Configuration

This module contains global configuration settings for the sportsbook scraper.
These settings define the valid year range for data scraping and can be
modified to adjust the application's behavior.

Author: Finn Lancaster, Rod Beckett (NCAA add-on)
License: MIT
"""

# Year range configuration for data scraping
# These values define the minimum and maximum years that can be scraped
# from sportsbookreview.com. Adjust these based on available data.

# Minimum year for which data is available on the website
MIN_YEAR = 2007

# Maximum year for which data is available on the website
# Note: Some years may not have complete data for all sports
MAX_YEAR = 2023
