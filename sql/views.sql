DROP VIEW IF EXISTS v_sector_summary;
DROP VIEW IF EXISTS v_year_trend;
DROP VIEW IF EXISTS v_funding_vs_lifespan;
DROP VIEW IF EXISTS v_top_burns;
DROP VIEW IF EXISTS v_country_summary;
DROP VIEW IF EXISTS v_rebuild_by_sector;

CREATE VIEW v_sector_summary AS
SELECT s.sector_name AS sector,
       COUNT(*) AS startups,
       ROUND(SUM(f.cash_burned_usd) / 1e6, 1) AS total_burn_usd_m,
       ROUND(AVG(f.cash_burned_usd) / 1e6, 1) AS avg_burn_usd_m,
       ROUND(AVG(f.lifespan_years), 1) AS avg_lifespan_years
FROM fact_startup f
JOIN dim_sector s ON s.sector_key = f.sector_key
GROUP BY s.sector_name;

CREATE VIEW v_year_trend AS
SELECT end_year_key AS end_year,
       COUNT(*) AS startups_died,
       ROUND(SUM(cash_burned_usd) / 1e6, 1) AS total_burn_usd_m
FROM fact_startup
GROUP BY end_year_key;

CREATE VIEW v_funding_vs_lifespan AS
SELECT funding_bucket,
       CASE funding_bucket
            WHEN '<$5M' THEN 1 WHEN '$5-20M' THEN 2 WHEN '$20-50M' THEN 3
            WHEN '$50-100M' THEN 4 WHEN '$100-500M' THEN 5 WHEN '$500M+' THEN 6 END AS bucket_order,
       COUNT(*) AS startups,
       ROUND(AVG(lifespan_years), 1) AS avg_lifespan_years
FROM fact_startup
WHERE funding_bucket IS NOT NULL
GROUP BY funding_bucket;

CREATE VIEW v_top_burns AS
SELECT name, country, product_type,
       ROUND(cash_burned_usd / 1e6, 1) AS burned_usd_m,
       founded_year_key AS founded, end_year_key AS ended, lifespan_years
FROM fact_startup
WHERE cash_burned_usd IS NOT NULL
ORDER BY cash_burned_usd DESC
LIMIT 20;

CREATE VIEW v_country_summary AS
SELECT country_group AS country,
       COUNT(*) AS startups,
       ROUND(SUM(cash_burned_usd) / 1e6, 1) AS total_burn_usd_m,
       ROUND(AVG(lifespan_years), 1) AS avg_lifespan_years
FROM fact_startup
GROUP BY country_group;

CREATE VIEW v_rebuild_by_sector AS
SELECT s.sector_name AS sector,
       COUNT(*) AS startups,
       ROUND(AVG(f.rebuild_difficulty_score), 2) AS avg_rebuild_difficulty,
       ROUND(AVG(f.scalability_score), 2) AS avg_scalability,
       SUM(CASE WHEN f.market_potential_level = 'High' THEN 1 ELSE 0 END) AS high_potential_count
FROM fact_startup f
JOIN dim_sector s ON s.sector_key = f.sector_key
GROUP BY s.sector_name;