CREATE OR REPLACE VIEW warehouse.vw_sales_overview AS
SELECT
    fs.sales_key,
    dp.product_id,
    dp.product_type,
    dp.fat_content,
    dp.weight,
    do2.outlet_id,
    do2.establishment_year,
    do2.outlet_size,
    do2.location_type,
    do2.outlet_type,
    fs.mrp,
    fs.product_visibility,
    fs.outlet_sales,
    fs.source_dataset,
    fs.load_ts
FROM warehouse.fact_sales fs
JOIN warehouse.dim_product dp ON fs.product_key = dp.product_key
JOIN warehouse.dim_outlet do2 ON fs.outlet_key = do2.outlet_key;

CREATE OR REPLACE VIEW warehouse.vw_outlet_performance AS
SELECT
    outlet_id,
    outlet_type,
    location_type,
    outlet_size,
    COUNT(*) AS total_rows,
    SUM(outlet_sales) AS total_sales,
    AVG(outlet_sales) AS avg_sales,
    AVG(mrp) AS avg_mrp
FROM warehouse.vw_sales_overview
WHERE outlet_sales IS NOT NULL
GROUP BY outlet_id, outlet_type, location_type, outlet_size;

CREATE OR REPLACE VIEW warehouse.vw_product_performance AS
SELECT
    product_type,
    fat_content,
    COUNT(*) AS total_rows,
    SUM(outlet_sales) AS total_sales,
    AVG(outlet_sales) AS avg_sales,
    AVG(product_visibility) AS avg_visibility
FROM warehouse.vw_sales_overview
WHERE outlet_sales IS NOT NULL
GROUP BY product_type, fat_content;
