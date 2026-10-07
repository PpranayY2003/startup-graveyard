"""Step 5: tag each startup with a main failure reason using the Excel keyword table."""
from pathlib import Path

import numpy as np
import pandas as pd

CLEAN = Path("data/clean/startups_clean.csv")
KEYWORDS = Path("reference/failure_reasons.xlsx")
TAGGED = Path("data/clean/startups_tagged.csv")
PBI_OUT = Path("powerbi/exports/startup_tagged.csv")
REVIEW = Path("data/clean/review_sample.xlsx")

OUTLIER_USD_M = 10_000  # startups that burned more than $10B are flagged as mega outliers


def load_rules():
    rules = pd.read_excel(KEYWORDS)
    rules.columns = [c.strip().lower() for c in rules.columns]
    out = []
    for _, row in rules.iterrows():
        if pd.isna(row["reason"]) or pd.isna(row["keywords"]):
            continue
        words = [k.strip().lower() for k in str(row["keywords"]).split(";") if k.strip()]
        out.append((str(row["reason"]).strip(), words))
    return out


def tag(text, rules):
    """Return (reason, number_of_keyword_hits, matched_keywords). Highest hit count wins."""
    if not isinstance(text, str):
        return "Other", 0, ""
    t = text.lower()
    best = ("Other", 0, "")
    for reason, words in rules:
        hits = [w for w in words if w in t]
        if len(hits) > best[1]:
            best = (reason, len(hits), "; ".join(hits))
    return best


def main():
    df = pd.read_csv(CLEAN)
    rules = load_rules()
    print("reasons loaded:", [r for r, _ in rules])

    tags = df["failure_analysis"].apply(lambda t: tag(t, rules))
    df["reason"] = tags.map(lambda x: x[0])
    df["keyword_hits"] = tags.map(lambda x: x[1])
    df["matched_keywords"] = tags.map(lambda x: x[2])
    df["is_outlier"] = np.where(df["cash_burned_usd_m"] > OUTLIER_USD_M, "Yes", "No")

    df.to_csv(TAGGED, index=False, encoding="utf-8-sig")

    keep = ["startup_id", "name", "country", "country_group", "sector", "product_type",
            "founding_year", "end_year", "lifespan_years", "end_era", "cash_burned_usd_m",
            "funding_bucket", "quality_flag", "is_outlier", "reason", "keyword_hits",
            "matched_keywords", "url"]
    PBI_OUT.parent.mkdir(parents=True, exist_ok=True)
    df[keep].to_csv(PBI_OUT, index=False, encoding="utf-8-sig")

    # 30 random rows to check by hand in Excel
    sample = df.sample(30, random_state=42)[
        ["startup_id", "name", "reason", "matched_keywords", "failure_analysis"]].copy()
    sample["failure_analysis"] = sample["failure_analysis"].str.slice(0, 600)
    sample["correct"] = ""
    sample.to_excel(REVIEW, index=False)

    print("\n=== TAGGING REPORT ===")
    counts = df["reason"].value_counts()
    print(counts.to_string())
    print("\nshare tagged 'Other':", round((df["reason"] == "Other").mean(), 2))
    print("outliers flagged:", (df["is_outlier"] == "Yes").sum())
    print("saved:", TAGGED, "|", PBI_OUT, "|", REVIEW)


if __name__ == "__main__":
    main()