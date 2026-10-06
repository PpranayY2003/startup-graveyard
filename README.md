# Startup Graveyard Analytics

Analysis of failed startups using data from Loot Drop (loot-drop.io): Python scraping and cleaning, a SQLite star schema with SQL views, failure-reason tagging (keyword rules, then a TF-IDF + logistic regression model), Excel lookup tables, and a Power BI dashboard.

## Tech stack

- Python (pandas, requests, BeautifulSoup/Playwright, scikit-learn)
- SQLite and SQL
- Power BI
- Excel
- Git

## Pipeline

Python (scrape, clean, tag) -> SQLite (star schema + views) -> CSV/Excel exports -> Power BI.

## Data note

Source data is AI-assisted summaries of public sources and may contain errors, so findings describe patterns in this dataset, not verified facts.

## Project structure

```text
data/
notebooks/
src/
sql/
reference/
powerbi/
docs/
```

## Status

Step 0 (setup) complete; scraping next.