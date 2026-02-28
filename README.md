# Big Mart Sales ETL (PostgreSQL Warehouse)

This project builds an end-to-end ETL pipeline from raw BigMart CSV files into a PostgreSQL warehouse designed for Tableau/Power BI.

## Source Data

- Train: `data/raw/bigmart/train/bigmart_train.csv`
- Test: `data/raw/bigmart/test/bigmart_test.csv`

Only analysis is in scope. The pipeline loads train and test records into a unified warehouse model. `OutletSales` exists only in train and is left `NULL` for test rows.

## Warehouse Model

- `staging.stg_bigmart_train`
- `staging.stg_bigmart_test`
- `warehouse.dim_product`
- `warehouse.dim_outlet`
- `warehouse.fact_sales`

BI-ready views:

- `warehouse.vw_sales_overview`
- `warehouse.vw_outlet_performance`
- `warehouse.vw_product_performance`

## Setup

1. Create `.env` in project root with PostgreSQL credentials:

```env
PGHOST=localhost
PGPORT=5432
PGDATABASE=bigmart_dw
PGUSER=postgres
PGPASSWORD=your_password
```

2. Optional DB auto-create settings:

```env
PGAUTO_CREATE_DB=true
PGADMIN_DB=postgres
# or: PGADMIN_DATABASES=postgres,template1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run ETL

From project root:

```powershell
python etl/run_etl.py
```

What it does:

1. Creates schemas/tables/views from `sql/`.
2. Reads raw CSV files.
3. Cleans and standardizes values (for example `LF/reg/low fat` normalization).
4. Loads staging tables.
5. Upserts dimensions.
6. Rebuilds `warehouse.fact_sales`.

## Sample BI Queries

Total sales by outlet type:

```sql
SELECT outlet_type, SUM(outlet_sales) AS total_sales
FROM warehouse.vw_sales_overview
WHERE outlet_sales IS NOT NULL
GROUP BY outlet_type
ORDER BY total_sales DESC;
```

Average sales by product category:

```sql
SELECT product_type, AVG(outlet_sales) AS avg_sales
FROM warehouse.vw_sales_overview
WHERE outlet_sales IS NOT NULL
GROUP BY product_type
ORDER BY avg_sales DESC;
```
