# Sportsbook Review Scraper Makefile

.PHONY: help install install-dev install-choco install-tesseract setup-ocr clean test lint format run-nfl run-nba run-nhl run-mlb run-ncaa-ocr run-all archive-data

# Default target
help:
	@echo "Sportsbook Review Scraper - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install         - Install production dependencies"
	@echo "  install-dev     - Install development dependencies"
	@echo "  install-choco   - Install Chocolatey package manager"
	@echo "  install-tesseract - Install Tesseract OCR"
	@echo "  setup-ocr       - Setup OCR environment (Chocolatey + Tesseract)"
	@echo ""
	@echo "Data Scraping:"
	@echo "  run-nfl         - Scrape NFL data (2015-2021)"
	@echo "  run-nba         - Scrape NBA data (2015-2021)"
	@echo "  run-nhl         - Scrape NHL data (2015-2021)"
	@echo "  run-mlb         - Scrape MLB data (2015-2021)"
	@echo "  run-ncaa-ocr    - Scrape NCAA 2nd half data using OCR"
	@echo "  run-all         - Scrape all sports data"
	@echo ""
	@echo "Development:"
	@echo "  test            - Run tests (if available)"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"
	@echo "  clean           - Clean generated files"
	@echo ""
	@echo "Examples:"
	@echo "  make run-nfl"
	@echo "  make run-ncaa-ocr"
	@echo "  python cli.py --sport nfl --start 2020 --end 2021 --filename nfl_2020_2021"

# Installation
install:
	pip install -r requirements.txt

install-dev: install
	pip install black flake8 pytest pytest-cov

# Install Chocolatey package manager
install-choco:
	@echo "Installing Chocolatey package manager..."
	@powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
	@echo "Chocolatey installed successfully!"

# Install Tesseract OCR using Chocolatey
install-tesseract:
	@echo "Installing Tesseract OCR..."
	@if command -v choco >/dev/null 2>&1; then \
		choco install tesseract -y; \
	else \
		echo "Chocolatey not found. Run 'make install-choco' first."; \
		exit 1; \
	fi
	@echo "Tesseract OCR installed successfully!"

# Setup complete OCR environment
setup-ocr: install-choco install-tesseract
	@echo "OCR environment setup complete!"
	@echo "You can now run: make run-ncaa-ocr"

# Data scraping targets
run-nfl:
	python cli.py --sport nfl --start 2015 --end 2021 --filename nfl_archive_7Y

run-nba:
	python cli.py --sport nba --start 2015 --end 2021 --filename nba_archive_7Y

run-nhl:
	python cli.py --sport nhl --start 2015 --end 2021 --filename nhl_archive_7Y

run-mlb:
	python cli.py --sport mlb --start 2015 --end 2021 --filename mlb_archive_7Y

# NCAA 2nd half OCR scraping
run-ncaa-ocr:
	@echo "Running NCAA 2nd half OCR scraping..."
	python example_ncaa_2ndhalf.py

# Test OCR functionality
test-ocr:
	@echo "Testing OCR functionality..."
	python setup_tesseract.py

run-all: run-nfl run-nba run-nhl run-mlb

# Archive all available years (2007-2021)
archive-nfl:
	python cli.py --sport nfl --start 2007 --end 2021 --filename nfl_archive_15Y

archive-nba:
	python cli.py --sport nba --start 2007 --end 2021 --filename nba_archive_15Y

archive-nhl:
	python cli.py --sport nhl --start 2007 --end 2021 --filename nhl_archive_15Y

archive-mlb:
	python cli.py --sport mlb --start 2007 --end 2021 --filename mlb_archive_15Y

archive-all: archive-nfl archive-nba archive-nhl archive-mlb

# Development tasks
test:
	@echo "Running tests..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v; \
	else \
		echo "pytest not found. Install with: make install-dev"; \
	fi

lint:
	@echo "Running linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 . --max-line-length=88 --ignore=E203,W503; \
	else \
		echo "flake8 not found. Install with: make install-dev"; \
	fi

format:
	@echo "Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black . --line-length=88; \
	else \
		echo "black not found. Install with: make install-dev"; \
	fi

# Clean up generated files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -f odds_table.png
	rm -f data/odds_table.png
	rm -f data/ncaa_2ndhalf_extracted.csv
	rm -f data/ocr_ncaa_2ndhalf.csv

# Create data directory if it doesn't exist
setup:
	mkdir -p data
	@echo "Setup complete. Data directory created."

# Show project info
info:
	@echo "Sportsbook Review Scraper"
	@echo "========================="
	@echo "Supported sports: NFL, NBA, NHL, MLB, NCAA (OCR)"
	@echo "Year range: 2007-2021"
	@echo "Output formats: JSON, CSV"
	@echo ""
	@echo "Usage:"
	@echo "  python cli.py --sport <sport> --start <year> --end <year> --filename <name> [--format json|csv]"
	@echo "  make run-ncaa-ocr  # For NCAA 2nd half OCR scraping" 