-- SQLite schema: staging + star schema
DROP TABLE IF EXISTS fact_startup;
DROP TABLE IF EXISTS dim_sector;
DROP TABLE IF EXISTS dim_reason;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS stg_startup;

-- Staging: cleaned rows loaded from Python as-is
CREATE TABLE stg_startup (
    startup_id        INTEGER,
    name              TEXT,
    slug              TEXT,
    url               TEXT,
    country           TEXT,
    sector            TEXT,
    product_type      TEXT,
    cash_burned_usd   INTEGER,
    founding_year     INTEGER,
    end_year          INTEGER,
    lifespan_years    INTEGER,
    description       TEXT,
    failure_analysis  TEXT,
    market_analysis   TEXT,
    startup_learnings TEXT,
    market_potential  TEXT,
    difficulty        TEXT,
    scalability       TEXT
);

-- Dimensions
CREATE TABLE dim_sector (
    sector_key   INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_name  TEXT NOT NULL UNIQUE,
    sector_group TEXT              -- filled from sector_map.xlsx
);

CREATE TABLE dim_reason (
    reason_key  INTEGER PRIMARY KEY AUTOINCREMENT,
    reason_name TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_date (            -- year grain (the site only has years)
    year_key INTEGER PRIMARY KEY,
    decade   INTEGER NOT NULL
);

WITH RECURSIVE y(yr) AS (
    SELECT 1950
    UNION ALL
    SELECT yr + 1 FROM y WHERE yr < 2030
)
INSERT INTO dim_date (year_key, decade)
SELECT yr, yr / 10 * 10 FROM y;

-- Fact
CREATE TABLE fact_startup (
    startup_id         INTEGER PRIMARY KEY,
    name               TEXT NOT NULL,
    slug               TEXT,
    url                TEXT,
    country            TEXT,
    product_type       TEXT,
    sector_key         INTEGER REFERENCES dim_sector(sector_key),
    founded_year_key   INTEGER REFERENCES dim_date(year_key),
    end_year_key       INTEGER REFERENCES dim_date(year_key),
    cash_burned_usd    INTEGER,
    lifespan_years     INTEGER,
    description        TEXT,
    failure_analysis   TEXT,
    market_analysis    TEXT,
    startup_learnings  TEXT,
    market_potential   TEXT,
    difficulty         TEXT,
    scalability        TEXT,
    reason_key         INTEGER REFERENCES dim_reason(reason_key),
    reason_confidence  REAL,
    reason_method      TEXT            -- 'keyword' or 'ml'
);
