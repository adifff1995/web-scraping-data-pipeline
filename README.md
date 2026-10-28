# Web Scraping & Data Pipeline Portfolio Project

A small, reproducible data pipeline that collects quote records from the public demo website
[Quotes to Scrape](https://quotes.toscrape.com/), cleans and validates the data, exports CSV files,
and generates a simple summary report and chart.

> Portfolio/demo project: the target website is explicitly designed for scraping practice. This is
> not production financial data and does not claim experience scraping private or restricted systems.

## What it demonstrates
- HTTP requests and HTML parsing with `requests` and `BeautifulSoup`
- Multi-page scraping with a polite delay between requests
- Data cleaning, validation, and duplicate removal with `pandas`
- Reproducible CSV outputs and a summary report
- A simple visualization of the most common tags

## Requirements
- Python 3.10+
- Internet connection to fetch the demo website

## Run it

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the pipeline:
```bash
python -m src.pipeline
```

The pipeline writes:
- `data/quotes_raw.csv` — extracted records
- `data/quotes_clean.csv` — cleaned records
- `reports/summary.md` — summary report
- `reports/top_tags.png` — chart (if matplotlib is available)

## Data fields
- `quote`: quote text
- `author`: author displayed on the page
- `tags`: comma-separated tags
- `source_page`: page URL from which the record was collected

## Responsible scraping
Use this project only against the included practice website or other sources where you have
permission. Check the site's terms and robots.txt, keep request rates low, and do not bypass
authentication, access controls, or rate limits.

## Suggested next improvements
- Add automated tests for parsing and cleaning
- Store records in SQLite
- Schedule the pipeline with cron or Task Scheduler
- Build a Power BI dashboard from `data/quotes_clean.csv`
