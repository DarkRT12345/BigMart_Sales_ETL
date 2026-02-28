# BigMart Sales ETL + Power BI Analytics

## Purpose

This project builds an end-to-end analytics pipeline for the BigMart dataset:

- ingest raw CSV files
- clean and standardize data
- load into a PostgreSQL star-schema warehouse
- dashboard analysis in Power BI

The goal of this project is business analysis.

## Project Objectives

- Build a reproducible ETL workflow from raw files to analytics-ready tables.
- Create a warehouse structure suitable for BI tools.
- Publish clear executive, outlet, and product performance dashboards.

## Tech Stack

- Python 3.10+
- Pandas (data wrangling)
- Psycopg 3 (PostgreSQL connectivity and loading)
- PostgreSQL (data warehouse)
- SQL (DDL, views)
- Power BI Desktop (`.pbix`) for reporting

## Data Source

- Train: `data/raw/bigmart/train/bigmart_train.csv` (contains `OutletSales`)
- Test: `data/raw/bigmart/test/bigmart_test.csv` (no `OutletSales`)

`OutletSales` for test rows is stored as `NULL`.

## Repository Structure

```text
big_mart_sales/
|-- data/
|   `-- raw/bigmart/
|       |-- train/bigmart_train.csv
|       `-- test/bigmart_test.csv
|-- etl/
|   |-- config.py
|   |-- extract_transform.py
|   |-- load.py
|   `-- run_etl.py
|-- sql/
|   |-- 01_create_schemas.sql
|   |-- 02_create_tables.sql
|   `-- 03_create_views.sql
|-- Dashboards/
|   |-- Executive Overview Dashboard.PNG
|   |-- Outlet Sales Analysis.PNG
|   `-- Product Analysis.PNG
|-- PowerBI/
|   `-- big_mart_sales_dashboard.pbix
|-- requirements.txt
`-- README.md
```

## Warehouse Design

### Staging

- `staging.stg_bigmart_train`
- `staging.stg_bigmart_test`

### Core Warehouse

- `warehouse.dim_product`
- `warehouse.dim_outlet`
- `warehouse.fact_sales`

### BI Views

- `warehouse.vw_sales_overview`
- `warehouse.vw_outlet_performance`
- `warehouse.vw_product_performance`

## ETL Logic

`etl/run_etl.py` orchestrates:

1. Load environment/config values.
2. Ensure target database exists (optional auto-create behavior).
3. Create schemas/tables/views from `sql/`.
4. Extract train/test CSVs.
5. Transform:
   - normalize `FatContent` variants (`LF`, `low fat`, `reg`)
   - fill missing `OutletSize` with `Unknown`
   - fill missing `ProductVisibility` with `0.0`
   - impute missing `Weight` using product median, then global median
6. Load to staging with bulk copy.
7. Upsert dimensions.
8. Rebuild `warehouse.fact_sales`.

## Setup

1. Create `.env` in project root:

```env
PGHOST=localhost
PGPORT=5432
PGDATABASE=bigmart_dw
PGUSER=postgres
PGPASSWORD=your_password
```

2. Optional DB auto-create controls:

```env
PGAUTO_CREATE_DB=true
PGADMIN_DB=postgres
# or: PGADMIN_DATABASES=postgres,template1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run ETL:

```powershell
python etl/run_etl.py
```

## Power BI Assets

- Dashboard file: `PowerBI/big_mart_sales_dashboard.pbix`
- Snapshot images: `Dashboards/*.PNG`

Power BI should connect to the PostgreSQL views in the `warehouse` schema (recommended primary table: `vw_sales_overview`).

## Key KPIs Used in Dashboard

- Total Sales
- Average Sales
- Total Products
- Total Outlets
- Sales by Outlet Type
- Sales by Product Type
- Sales Mix by Fat Content

## Analytical Summary

Detailed interpretation of visuals is documented in:

- `PowerBI_Analysis.md`

## Future Enhancements

- Add automated data quality tests post-load.
- Add incremental loading strategy for larger datasets.
- Add CI checks for ETL lint + SQL validation.
