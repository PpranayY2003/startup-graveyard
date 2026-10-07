"""Step 3: clean the raw Loot Drop scrape -> data/clean/startups_clean.csv"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/lootdrop_raw.jsonl")
OUT = Path("data/clean/startups_clean.csv")

UNIT_TO_MILLIONS = {"K": 1e-3, "M": 1.0, "B": 1e3, "T": 1e6}
Q = "['\"\u201c\u201d]?"
LEVEL = "(low|medium|high)"

LEVEL_PATTERNS = [
    r"market potential (?:today )?(?:is|gets|rates|=|:)\s*" + Q + LEVEL,
    r"potential (?:is|remains|=|:)\s*" + Q + LEVEL,
    r"market (?:is|remains)\s*" + Q + LEVEL + Q + r"\s+because",
    r"\b" + LEVEL + r" potential remains",
]


def money_to_millions(value):
    """'$944.0M' -> 944.0 | '$1.1B' -> 1100.0 | '$500K' -> 0.5 | unparseable -> NaN"""
    if pd.isna(value):
        return np.nan
    s = str(value).replace(",", "").replace("$", "").strip().upper()
    m = re.fullmatch(r"([\d.]+)\s*([KMBT])?", s)
    if not m:
        return np.nan
    try:
        number = float(m.group(1))
    except ValueError:
        return np.nan
    unit = m.group(2)
    return number * UNIT_TO_MILLIONS[unit] if unit else number / 1e6


def extract_score(text, keyword):
    """'... rebuild difficulty is 5/5 because ...' -> 5.0 (NaN when no number)."""
    if not isinstance(text, str):
        return np.nan
    m = re.search(keyword + r"[^.]{0,60}?\b([1-5])\s*/\s*5\b", text, re.I | re.S)
    return float(m.group(1)) if m else np.nan


def extract_level(text):
    """Find 'market potential is medium' style statements -> Low / Medium / High / Unknown."""
    if not isinstance(text, str):
        return "Unknown"
    for pattern in LEVEL_PATTERNS:
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1).capitalize()
    return "Unknown"


def main():
    df = pd.read_json(RAW, lines=True)
    print("raw rows:", len(df))

    # 1. tidy text columns and drop duplicates
    text_cols = ["slug", "url", "name", "country", "description", "sector",
                 "product_type", "total_cash_burned", "failure_analysis",
                 "market_analysis", "startup_learnings", "market_potential",
                 "difficulty", "scalability"]
    for c in text_cols:
        df[c] = df[c].astype("string").str.strip()
    before = len(df)
    df = df.drop_duplicates(subset="startup_id").drop_duplicates(subset="slug")
    print("duplicates removed:", before - len(df))

    # 2. money text -> USD millions
    df["cash_burned_usd_m"] = df["total_cash_burned"].map(money_to_millions)
    bad = df.loc[df["cash_burned_usd_m"].isna(), "total_cash_burned"].unique()
    print("unparseable cash values:", list(bad)[:10])

    # 3. lifespan and data-quality flags
    df["lifespan_years"] = df["end_year"] - df["founding_year"]
    df["quality_flag"] = "ok"
    df.loc[df["founding_year"] < 1950, "quality_flag"] = "check_founding_year"
    df.loc[df["lifespan_years"] < 0, "quality_flag"] = "end_before_founding"
    df.loc[df["lifespan_years"] < 0, "lifespan_years"] = np.nan
    df.loc[df["cash_burned_usd_m"].isna(), "quality_flag"] = "missing_cash"

    # 4. buckets and groups for the dashboard
    bins = [0, 5, 20, 50, 100, 500, np.inf]
    labels = ["<$5M", "$5-20M", "$20-50M", "$50-100M", "$100-500M", "$500M+"]
    df["funding_bucket"] = pd.cut(df["cash_burned_usd_m"], bins=bins, labels=labels, right=False)

    era_bins = [1999, 2009, 2014, 2019, 2022, 2100]
    era_labels = ["2000-2009", "2010-2014", "2015-2019", "2020-2022", "2023+"]
    df["end_era"] = pd.cut(df["end_year"], bins=era_bins, labels=era_labels)

    top_countries = df["country"].value_counts().head(5).index
    df["country_group"] = np.where(df["country"].isin(top_countries), df["country"], "Other")

    # 5. pull ratings out of the long analysis paragraphs
    df["market_potential_level"] = df["market_potential"].map(extract_level)
    df["rebuild_difficulty_score"] = df["difficulty"].map(lambda t: extract_score(t, "difficulty"))
    df["scalability_score"] = df["scalability"].map(lambda t: extract_score(t, "scalability"))

    df = df.rename(columns={
        "market_potential": "market_potential_text",
        "difficulty": "rebuild_difficulty_text",
        "scalability": "scalability_text",
    })

    cols = ["startup_id", "slug", "name", "country", "country_group", "sector",
            "product_type", "founding_year", "end_year", "lifespan_years", "end_era",
            "cash_burned_usd_m", "funding_bucket", "market_potential_level",
            "rebuild_difficulty_score", "scalability_score", "quality_flag",
            "description", "failure_analysis", "market_analysis", "startup_learnings",
            "market_potential_text", "rebuild_difficulty_text", "scalability_text",
            "url", "scraped_at"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df[cols].to_csv(OUT, index=False, encoding="utf-8-sig")

    print("\n=== CLEANING REPORT ===")
    print("clean rows:", len(df))
    print("quality flags:")
    print(df["quality_flag"].value_counts().to_string())
    print(f"total capital burned: ${df['cash_burned_usd_m'].sum() / 1000:.1f}B")
    print("median lifespan (years):", df["lifespan_years"].median())
    print("market potential extracted:", round((df["market_potential_level"] != "Unknown").mean(), 2))
    print("difficulty score extracted:", round(df["rebuild_difficulty_score"].notna().mean(), 2))
    print("scalability score extracted:", round(df["scalability_score"].notna().mean(), 2))
    print("\ntop 5 burns:")
    print(df.nlargest(5, "cash_burned_usd_m")[["name", "country", "cash_burned_usd_m"]].to_string(index=False))
    print("\nsaved:", OUT)


if __name__ == "__main__":
    main()
