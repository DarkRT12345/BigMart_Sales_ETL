CREATE TABLE IF NOT EXISTS staging.stg_bigmart_train (
    product_id TEXT,
    weight NUMERIC,
    fat_content TEXT,
    product_visibility NUMERIC,
    product_type TEXT,
    mrp NUMERIC,
    outlet_id TEXT,
    establishment_year INTEGER,
    outlet_size TEXT,
    location_type TEXT,
    outlet_type TEXT,
    outlet_sales NUMERIC,
    source_dataset TEXT NOT NULL DEFAULT 'train',
    load_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_bigmart_test (
    product_id TEXT,
    weight NUMERIC,
    fat_content TEXT,
    product_visibility NUMERIC,
    product_type TEXT,
    mrp NUMERIC,
    outlet_id TEXT,
    establishment_year INTEGER,
    outlet_size TEXT,
    location_type TEXT,
    outlet_type TEXT,
    outlet_sales NUMERIC,
    source_dataset TEXT NOT NULL DEFAULT 'test',
    load_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    product_type TEXT,
    fat_content TEXT,
    weight NUMERIC,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.dim_outlet (
    outlet_key BIGSERIAL PRIMARY KEY,
    outlet_id TEXT NOT NULL UNIQUE,
    establishment_year INTEGER,
    outlet_size TEXT,
    location_type TEXT,
    outlet_type TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    product_key BIGINT NOT NULL REFERENCES warehouse.dim_product(product_key),
    outlet_key BIGINT NOT NULL REFERENCES warehouse.dim_outlet(outlet_key),
    mrp NUMERIC,
    product_visibility NUMERIC,
    outlet_sales NUMERIC,
    source_dataset TEXT NOT NULL,
    load_ts TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_product_key ON warehouse.fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_outlet_key ON warehouse.fact_sales(outlet_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_source_dataset ON warehouse.fact_sales(source_dataset);
