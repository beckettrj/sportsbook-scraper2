# Sportsbookreview.com Scraper
> Scrape 15+ years of sportsbookreview.com data. Currently supports NFL, NBA, MLB, NHL, and NCAA Basketball, with easy extensibility to other sports.

Keywords: ``sportsbookreview.com``, ``sportsbookreview``, ``sportsbook``, ``scraper``, ``sports``, ``sports betting``, ``sportsbookreview.com scraper``, ``sportsbookreview scraper``, ``odds``, ``odds scraper``, ``ncaa basketball``

## What is this?
This is a scraper for sportsbookreview.com. It scrapes the data from the website and saves it to a file. This is useful for data analysis, machine learning, and other applications, where you need a large amount of data, particularly odds. For many betting hobbyists and analysts, it is hard to acquire odds data going past the current season for free. This scraper solves that problem by allowing you to scrape 15+ years of data from sportsbookreview.com. Additionally, pre-scraped datasets are provided in the ``data`` folder for each sport, ranging from 2007 to 2023.

## Features
- **Multiple Sports**: NFL, NBA, MLB, NHL, and NCAA Basketball
- **Extensive Data Range**: 2007-2023 (15+ years of data)
- **Flexible Output**: JSON and CSV formats
- **Error Handling**: Gracefully handles missing years and unavailable data
- **Team Name Translation**: Automatic translation of team names to full names
- **Comprehensive Stats**: Scores, odds, spreads, totals, and more

## Installation

### Prerequisites
- **Python 3.7 or higher** (Python 3.8+ recommended)
- **pip** (usually comes with Python)

### 🚀 Quick Installation (Recommended)

#### Windows Users
1. Download and extract the project files
2. Double-click `install.bat` or run it from Command Prompt
3. Follow the on-screen instructions

#### Mac/Linux Users
1. Download and extract the project files
2. Open Terminal and navigate to the project folder
3. Run: `chmod +x install.sh && ./install.sh`

#### Manual Installation
If the automated scripts don't work, you can install manually:

```sh
# Clone the repository
git clone https://github.com/finned-tech/sportsbookreview-scraper.git
cd sportsbookreview-scraper

# Install dependencies (specific versions for compatibility)
pip install -r requirements.txt

# Create data directory
mkdir -p data
```

### 📦 Dependencies (Automatically Installed)
The following packages are installed with specific versions for compatibility:

- **requests==2.31.0** - HTTP requests
- **pandas==2.2.3** - Data manipulation
- **lxml==5.4.0** - XML/HTML parsing
- **html5lib==1.1** - HTML parser
- **beautifulsoup4==4.13.3** - HTML parsing
- **openpyxl==3.1.5** - Excel file support
- **xlrd==2.0.2** - Excel file reading

### Using Makefile (Linux/Mac)
```sh
# Install dependencies
make install

# Install development dependencies (includes linting and formatting tools)
make install-dev

# Setup project
make setup
```

## Usage

### Basic Usage
```sh
python cli.py --sport <sport> --start <year> --end <year> --filename <filename> [--format json|csv]
```

### Examples
```sh
# Scrape NFL data for 2020-2021
python cli.py --sport nfl --start 2020 --end 2021 --filename nfl_2020_2021

# Scrape NBA data for full range (2007-2023)
python cli.py --sport nba --start 2007 --end 2023 --filename nba_archive_17Y

# Scrape NCAA Basketball data as CSV
python cli.py --sport ncaa --start 2021 --end 2022 --filename ncaa_2021_2022 --format csv

# Scrape MLB data for specific years
python cli.py --sport mlb --start 2015 --end 2020 --filename mlb_2015_2020
```

### Using Makefile Commands (Linux/Mac)
```sh
# Quick scraping for recent years (2015-2023)
make run-nfl      # NFL data
make run-nba      # NBA data
make run-nhl      # NHL data
make run-mlb      # MLB data
make run-all      # All sports

# Full archive scraping (2007-2023)
make archive-nfl  # NFL full archive
make archive-nba  # NBA full archive
make archive-nhl  # NHL full archive
make archive-mlb  # MLB full archive
make archive-all  # All sports full archive

# Development tasks
make format       # Format code with black
make lint         # Run linting with flake8
make test         # Run tests (if available)
make clean        # Clean generated files
```

## Supported Sports and Data

### NFL (National Football League)
- **Years Available**: 2007-2023
- **Data Fields**: Scores by quarter, spreads, totals, money lines, 2H lines
- **URL Format**: `nfl-odds-YYYY-YY`

### NBA (National Basketball Association)
- **Years Available**: 2007-2023
- **Data Fields**: Scores by quarter, spreads, totals, money lines, 2H lines
- **URL Format**: `nba-odds-YYYY-YY`

### NHL (National Hockey League)
- **Years Available**: 2007-2023
- **Data Fields**: Scores by period, spreads, totals, money lines
- **URL Format**: `nhl-odds-YYYY-YY`

### MLB (Major League Baseball)
- **Years Available**: 2007-2023
- **Data Format**: Excel files
- **Data Fields**: Scores by inning, spreads, totals, money lines
- **URL Format**: `mlb-odds-YYYY.xlsx`

### NCAA Basketball
- **Years Available**: 2007-2023 (varies by year)
- **Data Fields**: Scores by half, spreads, totals, money lines, 2H lines
- **URL Format**: `ncaa-basketball-YYYY-YY/`

## Command Line Arguments

| Argument | Required | Options | Description |
|----------|----------|---------|-------------|
| `--sport` | Yes | `nfl`, `nba`, `nhl`, `mlb`, `ncaa` | The sport to scrape data for |
| `--start` | Yes | 2007-2023 | The year to start scraping data from |
| `--end` | Yes | 2007-2023 | The year to stop scraping data at |
| `--filename` | Yes | Any string | The filename to save the scraped data to |
| `--format` | No | `json` (default), `csv` | The format to save the scraped data in |

## Data Schema

All sports follow a similar schema with sport-specific variations:

### Common Fields
- `season`: Year of the season
- `date`: Game date (YYYYMMDD format)
- `home_team`: Home team name (translated to full name)
- `away_team`: Away team name (translated to full name)
- `home_final`: Home team final score
- `away_final`: Away team final score

### Sport-Specific Fields
- **NFL/NBA**: `home_1stQtr`, `away_1stQtr`, `home_2ndQtr`, etc.
- **NHL**: `home_1stPeriod`, `away_1stPeriod`, etc.
- **MLB**: `home_1stInn`, `away_1stInn`, etc.
- **NCAA**: `home_1st`, `away_1st`, `home_2nd`, `away_2nd`

### Odds Fields
- `home_open_spread`, `away_open_spread`: Opening point spreads
- `home_close_spread`, `away_close_spread`: Closing point spreads
- `open_over_under`, `close_over_under`: Total points/goals
- `home_close_ml`, `away_close_ml`: Money lines

## Error Handling

The scraper includes robust error handling:
- **Missing Years**: Automatically skips years with no available data
- **Network Issues**: Retries with appropriate delays
- **Invalid Data**: Graceful handling of malformed data
- **Rate Limiting**: User-agent headers to avoid blocking

## Troubleshooting

### Common Issues

**"Python is not recognized"**
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

**"pip is not recognized"**
- Python may not have been installed with pip
- Try: `python -m ensurepip --upgrade`

**"Permission denied" (Linux/Mac)**
- Run: `chmod +x install.sh`
- Or use: `sudo python3 install.py`

**Package installation errors**
- Try upgrading pip: `python -m pip install --upgrade pip`
- Check your internet connection
- Try installing packages one by one

### Getting Help
If you encounter issues:
1. Check that Python 3.7+ is installed: `python --version`
2. Ensure pip is available: `pip --version`
3. Try the automated installation scripts first
4. Check the error messages for specific issues

## Development

### Project Structure
```
sportsbookreview-scraper/
├── cli.py                 # Command line interface
├── config.py             # Configuration (year ranges)
├── config/
│   └── translated.json   # Team name translations
├── scrapers/
│   └── sportsbookreview.py  # Scraper classes
├── data/                 # Output directory
├── requirements.txt      # Python dependencies (specific versions)
├── install.py           # Automated installation script
├── install.bat          # Windows installation script
├── install.sh           # Mac/Linux installation script
├── Makefile             # Build automation (Linux/Mac)
└── README.md            # This file
```

### Adding New Sports
1. Create a new scraper class in `scrapers/sportsbookreview.py`
2. Add team translations to `config/translated.json`
3. Update the scraper dictionary in `cli.py`
4. Test with available data

## License
Copyright © 2023 Finn Lancaster

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.