"""Create views and export each to CSV plus one Excel workbook for Power BI."""
from pathlib import Path

import pandas as pd

from db import get_conn

OUT = Path("powerbi/exports")
VIEWS = ["v_sector_summary", "v_year_trend", "v_funding_vs_lifespan",
         "v_top_burns", "v_country_summary", "v_rebuild_by_sector"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    conn.executescript(Path("sql/views.sql").read_text(encoding="utf-8"))
    with pd.ExcelWriter(OUT / "startup_graveyard.xlsx", engine="openpyxl") as xl:
        for v in VIEWS:
            df = pd.read_sql_query(f"SELECT * FROM {v}", conn)
            df.to_csv(OUT / f"{v}.csv", index=False, encoding="utf-8-sig")
            df.to_excel(xl, sheet_name=v[2:31], index=False)
            print(f"{v:<24} {len(df):>4} rows")
    detail = pd.read_sql_query(
        "SELECT f.startup_id, f.name, f.country, f.country_group, s.sector_name AS sector, "
        "f.product_type, f.founded_year_key AS founded, f.end_year_key AS ended, "
        "f.lifespan_years, f.cash_burned_usd, f.funding_bucket, f.end_era, "
        "f.market_potential_level, f.rebuild_difficulty_score, f.scalability_score "
        "FROM fact_startup f LEFT JOIN dim_sector s ON s.sector_key = f.sector_key", conn)
    detail.to_csv(OUT / "startup_detail.csv", index=False, encoding="utf-8-sig")
    print(f"{'startup_detail':<24} {len(detail):>4} rows")
    conn.close()


if __name__ == "__main__":
    main()