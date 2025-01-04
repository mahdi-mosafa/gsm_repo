# GSMArena Mobile Data Scraper

A Python-based web crawler leveraging Playwright to scrape detailed information about mobile phones from GSMArena. This project is designed for structured data extraction and comes in two versions:
- **Text-only scraping** (current branch): Extracts specifications, comments, and metadata.
- **Image-inclusive scraping** (separate branch): Downloads associated images alongside textual data.

## Features
- **Human-like Interactions**: Simulates mouse movements and actions to evade bot detection.
- **CSV Storage**: Saves data in a structured CSV format with robust error handling.
- **Asynchronous Operations**: Ensures high efficiency and performance.
- **Configurable Scraping Range**: Easily adjust the range of pages to be scraped.

## Requirements
- Python 3.x
- pandas
- openpyxl
- playwright
- httpx

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mahdi-mosafa/mobile-specs-crawler.git
   cd mobile-specs-crawler
