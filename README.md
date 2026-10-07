# Startup Graveyard Analytics

An end-to-end data analysis of ~1,000 failed startups: scraped from [Loot Drop](https://www.loot-drop.io/), cleaned with Python and pandas, modelled in a SQLite star schema, tagged with failure reasons using a keyword table in Excel, and visualised in an interactive Power BI dashboard.

**Questions this project answers:** Which sectors and countries lose the most? When did failures peak? How long do startups survive? Why do they fail?

## Dashboard preview

![Overview page](docs/dashboard_overview.png)
![Why startups fail page](docs/dashboard_reasons.png)

The report is in [`powerbi/Graveyard_report.pbix`](powerbi/Graveyard_report.pbix) (open with Power BI Desktop).

- **Overview:** KPI cards, capital burned by sector, failures by year, country mix, and the 10 most expensive failures. Slicers for era, sector, country and outliers.
- **Why startups fail:** share of each failure reason, how the reason mix shifts across eras, a scorecard by reason, and capital burned versus survival time.

## Key insights

1. **A few mega-failures dominate the totals.** The dataset records about **$510B** in cash burned across 994 startups, but four companies (Silicon Valley Bank, Wirecard, WeWork and Northvolt, about $274B combined) account for roughly **54%** of it. The other 990 startups total about $236B. The dashboard therefore has an outlier slicer, and averages are less meaningful than medians here.
2. **The typical failure is small and quick.** The median startup burned about **$8.5M** and survived a median of **4 years**, far from the headline billion-dollar collapses.
3. **Competition is the most common failure reason, followed by regulation and market timing.** Of 994 startups, about **28%** were tagged Competition, **18%** Regulatory / legal and **14%** Market timing / macro. Weak demand, high costs and running out of cash each account for roughly 9 to 10%. Fraud and technology problems are rare (about 1 to 2% each). These tags come from keyword rules and have not been manually validated, so Competition in particular is likely overstated.
4. **Failures in this dataset rise sharply after 2010 and peak in 2024.** 2025 and 2026 are partial years. The pattern reflects both real failures and how Loot Drop catalogues them, so it is not a true failure rate.
5. **The US dominates, and three sectors hold most startups.** The US accounts for about 58% of startups, China about 17%, then India and the UK at roughly 4 to 5% each. Consumer, Communication Services and Information Technology together hold about 7 in 10 startups, while Financials leads on capital burned because of the mega-failures above.

## Pipeline

```
Loot Drop (public pages)
        |  src/scrape_lootdrop.py
        v
data/raw/lootdrop_raw.jsonl
        |  src/clean.py            (pandas: parse money, lifespans, buckets, quality flags)
        v
data/clean/startups_clean.csv
        |-- src/load_db.py --> SQLite star schema (fact_startup, dim_sector, dim_date)
        |                          |  src/export.py (SQL views -> CSV / Excel)
        |                          v
        |                    powerbi/exports/*.csv
        |
        '-- src/tag_reasons.py (+ reference/failure_reasons.xlsx keyword table)
                   v
        powerbi/exports/startup_tagged.csv  -->  Power BI dashboard
```

## Tech stack

| Area | Tools |
|---|---|
| Collection and cleaning | Python, pandas, requests, BeautifulSoup |
| Database and SQL | SQLite, star schema, SQL views (aggregations, joins) |
| Reference data | Excel (failure-reason keyword table) |
| Visualisation | Power BI (DAX measures, slicers, treemap, ribbon, matrix and more) |
| Version control | Git and GitHub (feature branches, tagged releases) |

## How failure reasons were tagged

`reference/failure_reasons.xlsx` lists nine failure reasons with keywords for each. `src/tag_reasons.py` counts keyword matches in each startup's failure write-up and assigns the reason with the most matches (or "Other" if none match). Editing the Excel table and re-running the script updates the tags, so no code changes are needed. It is a simple, transparent rule-based method, and it is **not** a trained model.

## Project structure

```
startup-graveyard/
├── data/            raw and cleaned data (git-ignored, rebuilt by the scripts)
├── docs/            dashboard screenshots
├── powerbi/         Graveyard_report.pbix and exported CSVs
├── reference/       failure_reasons.xlsx (keyword table)
├── sql/             schema.sql and views.sql
├── src/             scrape, clean, load, export and tagging scripts
├── .env.example     database path setting
└── requirements.txt
```

## How to run

Requires Python 3.11 and Power BI Desktop (Windows).

```powershell
git clone https://github.com/PpranayY2003/startup-graveyard.git
cd startup-graveyard
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env

python src\scrape_lootdrop.py   # collect raw data
python src\clean.py             # clean and enrich
python src\load_db.py           # build the SQLite star schema
python src\export.py            # export SQL views for Power BI
python src\tag_reasons.py       # tag failure reasons and flag outliers
```

Then open `powerbi/Graveyard_report.pbix`. To refresh the report with new data, point its data source at `powerbi/exports/startup_tagged.csv`.

## Data source and ethics

All data comes from [Loot Drop](https://www.loot-drop.io/), a catalogue of failed startups compiled from public sources such as news articles, press releases and founder statements. Loot Drop states that its entries include AI-assisted analysis that is then human-reviewed. The scraper only requested public startup pages and never the path disallowed in the site's `robots.txt`. This project is non-commercial and for portfolio purposes, and the raw scraped data is not redistributed in this repository. Credit for the underlying data belongs to Loot Drop.

## Limitations

- **Source quality:** the data is AI-assisted and may contain errors. Findings describe patterns in this dataset, not verified facts about all startups.
- **Selection bias:** Loot Drop includes only the failures it chose to catalogue, so counts by year or country are not true failure rates.
- **Outliers:** four mega-failures (including a bank) skew totals, and "cash burned" is the figure stated by the source.
- **Reason tags:** keyword-based and not manually validated. Competition is probably over-counted.
- **Partial years:** 2025 and 2026 are incomplete.
- **Ratings:** market potential, difficulty and scalability exist mostly as long text with explicit ratings in only a small share of records, so they are not used in the dashboard.

## What I practised

Web scraping with polite constraints, data cleaning and quality flags in pandas, star-schema design and SQL views, a keyword-driven classification with an Excel lookup table, DAX measures and dashboard design in Power BI, and a feature-branch Git workflow with tagged releases.

## Possible next steps

Validate the reason tags on a manual sample and tighten the keywords, add a dim_reason table to the star schema, compare sectors by median instead of total burn, and schedule the pipeline to refresh automatically.

## Author

Pranay Malhotra
GitHub: [@PpranayY2003](https://github.com/PpranayY2003)