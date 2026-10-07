"""Step 4: load data/clean/startups_clean.csv into SQLite (staging -> dims -> fact)."""
from pathlib import Path

import pandas as pd

from db import get_conn

CSV = Path("data/clean/startups_clean.csv")
SCHEMA = Path("sql/schema.sql")

STG_COLS = ["startup_id", "name", "slug", "url", "country", "country_group", "sector",
            "product_type", "cash_burned_usd", "founding_year", "end_year", "lifespan_years",
            "end_era", "funding_bucket", "market_potential_level", "rebuild_difficulty_score",
            "scalability_score", "quality_flag", "description", "failure_analysis",
            "market_analysis", "startup_learnings", "market_potential", "difficulty",
            "scalability"]

FACT_SQL = """
INSERT INTO fact_startup (
    startup_id, name, slug, url, country, country_group, product_type, sector_key,
    founded_year_key, end_year_key, cash_burned_usd, lifespan_years, end_era, funding_bucket,
    market_potential_level, rebuild_difficulty_score, scalability_score, quality_flag,
    description, failure_analysis, market_analysis, startup_learnings,
    market_potential, difficulty, scalability)
SELECT
    s.startup_id, s.name, s.slug, s.url, s.country, s.country_group, s.product_type, d.sector_key,
    s.founding_year, s.end_year, s.cash_burned_usd, s.lifespan_years, s.end_era, s.funding_bucket,
    s.market_potential_level, s.rebuild_difficulty_score, s.scalability_score, s.quality_flag,
    s.description, s.failure_analysis, s.market_analysis, s.startup_learnings,
    s.market_potential, s.difficulty, s.scalability
FROM stg_startup s
LEFT JOIN dim_sector d ON d.sector_name = s.sector;
"""


def main():
    df = pd.read_csv(CSV)
    df = df.rename(columns={
        "market_potential_text": "market_potential",
        "rebuild_difficulty_text": "difficulty",
        "scalability_text": "scalability",
    })
    df["cash_burned_usd"] = (df["cash_burned_usd_m"] * 1_000_000).round().astype("Int64")
    df["lifespan_years"] = df["lifespan_years"].round().astype("Int64")
    df = df[STG_COLS]
    df = df.astype(object).where(df.notna(), None)

    conn = get_conn()
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    df.to_sql("stg_startup", conn, if_exists="append", index=False)
    conn.execute("INSERT OR IGNORE INTO dim_sector (sector_name) "
                 "SELECT DISTINCT sector FROM stg_startup WHERE sector IS NOT NULL")
    conn.execute(FACT_SQL)
    conn.commit()

    print("rows in csv       :", len(df))
    for table in ["stg_startup", "dim_sector", "dim_date", "fact_startup"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:<18}:", n)
    orphans = conn.execute("SELECT COUNT(*) FROM fact_startup WHERE sector_key IS NULL").fetchone()[0]
    print("facts w/o sector  :", orphans)
    print("PRAGMA foreign_key_check:", conn.execute("PRAGMA foreign_key_check").fetchall() or "OK")
    conn.close()


if __name__ == "__main__":
    main()