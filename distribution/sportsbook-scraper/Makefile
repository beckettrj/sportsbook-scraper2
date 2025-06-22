# Sportsbook Review Scraper Makefile

.PHONY: help install install-dev clean test lint format run-nfl run-nba run-nhl run-mlb run-all archive-data

# Default target
help:
	@echo "Sportsbook Review Scraper - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "Data Scraping:"
	@echo "  run-nfl      - Scrape NFL data (2015-2021)"
	@echo "  run-nba      - Scrape NBA data (2015-2021)"
	@echo "  run-nhl      - Scrape NHL data (2015-2021)"
	@echo "  run-mlb      - Scrape MLB data (2015-2021)"
	@echo "  run-all      - Scrape all sports data"
	@echo ""
	@echo "Development:"
	@echo "  test         - Run tests (if available)"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean generated files"
	@echo ""
	@echo "Examples:"
	@echo "  make run-nfl"
	@echo "  python cli.py --sport nfl --start 2020 --end 2021 --filename nfl_2020_2021"

# Installation
install:
	pip install -r requirements.txt

install-dev: install
	pip install black flake8 pytest pytest-cov

# Data scraping targets
run-nfl:
	python cli.py --sport nfl --start 2015 --end 2021 --filename nfl_archive_7Y

run-nba:
	python cli.py --sport nba --start 2015 --end 2021 --filename nba_archive_7Y

run-nhl:
	python cli.py --sport nhl --start 2015 --end 2021 --filename nhl_archive_7Y

run-mlb:
	python cli.py --sport mlb --start 2015 --end 2021 --filename mlb_archive_7Y

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

# Create data directory if it doesn't exist
setup:
	mkdir -p data
	@echo "Setup complete. Data directory created."

# Show project info
info:
	@echo "Sportsbook Review Scraper"
	@echo "========================="
	@echo "Supported sports: NFL, NBA, NHL, MLB"
	@echo "Year range: 2007-2021"
	@echo "Output formats: JSON, CSV"
	@echo ""
	@echo "Usage:"
	@echo "  python cli.py --sport <sport> --start <year> --end <year> --filename <name> [--format json|csv]" 