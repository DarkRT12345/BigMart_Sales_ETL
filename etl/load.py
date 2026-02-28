from __future__ import annotations

from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row
from psycopg import sql

from config import (
    SQL_DIR,
    get_pg_admin_candidates,
    get_pg_config,
    is_pg_auto_create_enabled,
)


SQL_FILES = [
    "01_create_schemas.sql",
    "02_create_tables.sql",
    "03_create_views.sql",
]


def _ensure_database_exists(pg_config: dict) -> None:
    target_db = pg_config["dbname"]

    # Fast path: target database already exists and is reachable.
    try:
        with psycopg.connect(**pg_config):
            return
    except psycopg.OperationalError as target_err:
        if "does not exist" not in str(target_err).lower():
            raise

    if not is_pg_auto_create_enabled():
        raise RuntimeError(
            f"Database '{target_db}' does not exist and PGAUTO_CREATE_DB is disabled."
        )

    admin_errors: list[str] = []
    for admin_db in get_pg_admin_candidates(pg_config):
        admin_cfg = dict(pg_config)
        admin_cfg["dbname"] = admin_db
        try:
            with psycopg.connect(**admin_cfg, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
                    exists = cur.fetchone() is not None
                    if not exists:
                        cur.execute(
                            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db))
                        )
            return
        except psycopg.Error as err:
            admin_errors.append(f"{admin_db}: {err.__class__.__name__}: {err}")
            continue

    raise RuntimeError(
        f"Unable to auto-create database '{target_db}'. "
        f"Tried admin DB candidates: {', '.join(get_pg_admin_candidates(pg_config))}. "
        "Set PGADMIN_DB/PGADMIN_DATABASES to a reachable database with CREATE DATABASE permission, "
        "or create the target DB manually.\n"
        + "\n".join(admin_errors)
    )


def _run_sql_files(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        for file_name in SQL_FILES:
            sql_path = SQL_DIR / file_name
            sql_text = Path(sql_path).read_text(encoding="utf-8")
            cur.execute(sql_text)
    conn.commit()


def _truncate_staging(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE staging.stg_bigmart_train;")
        cur.execute("TRUNCATE TABLE staging.stg_bigmart_test;")
    conn.commit()


def _copy_dataframe(
    conn: psycopg.Connection,
    df: pd.DataFrame,
    target_table: str,
) -> None:
    cols = list(df.columns)
    copy_sql = f"COPY {target_table} ({', '.join(cols)}) FROM STDIN"
    with conn.cursor() as cur:
        with cur.copy(copy_sql) as copy:
            for row in df.itertuples(index=False, name=None):
                copy.write_row(row)
    conn.commit()


def _upsert_dimensions(conn: psycopg.Connection) -> None:
    sql = """
    WITH combined AS (
        SELECT
            product_id,
            product_type,
            fat_content,
            weight,
            outlet_id,
            establishment_year,
            outlet_size,
            location_type,
            outlet_type
        FROM staging.stg_bigmart_train
        UNION ALL
        SELECT
            product_id,
            product_type,
            fat_content,
            weight,
            outlet_id,
            establishment_year,
            outlet_size,
            location_type,
            outlet_type
        FROM staging.stg_bigmart_test
    ),
    product_ranked AS (
        SELECT
            product_id,
            product_type,
            fat_content,
            weight,
            ROW_NUMBER() OVER (
                PARTITION BY product_id
                ORDER BY
                    CASE WHEN source_dataset = 'train' THEN 0 ELSE 1 END,
                    weight DESC NULLS LAST
            ) AS rn
        FROM (
            SELECT product_id, product_type, fat_content, weight, 'train'::text AS source_dataset
            FROM staging.stg_bigmart_train
            UNION ALL
            SELECT product_id, product_type, fat_content, weight, 'test'::text AS source_dataset
            FROM staging.stg_bigmart_test
        ) p
        WHERE product_id IS NOT NULL
    )
    INSERT INTO warehouse.dim_product (product_id, product_type, fat_content, weight)
    SELECT
        product_id,
        product_type,
        fat_content,
        weight
    FROM product_ranked
    WHERE rn = 1
    ON CONFLICT (product_id) DO UPDATE
    SET
        product_type = EXCLUDED.product_type,
        fat_content = EXCLUDED.fat_content,
        weight = EXCLUDED.weight,
        updated_at = CURRENT_TIMESTAMP;

    WITH combined AS (
        SELECT
            outlet_id,
            establishment_year,
            outlet_size,
            location_type,
            outlet_type
        FROM staging.stg_bigmart_train
        UNION ALL
        SELECT
            outlet_id,
            establishment_year,
            outlet_size,
            location_type,
            outlet_type
        FROM staging.stg_bigmart_test
    ),
    outlet_ranked AS (
        SELECT
            outlet_id,
            establishment_year,
            outlet_size,
            location_type,
            outlet_type,
            ROW_NUMBER() OVER (
                PARTITION BY outlet_id
                ORDER BY
                    CASE WHEN source_dataset = 'train' THEN 0 ELSE 1 END
            ) AS rn
        FROM (
            SELECT outlet_id, establishment_year, outlet_size, location_type, outlet_type, 'train'::text AS source_dataset
            FROM staging.stg_bigmart_train
            UNION ALL
            SELECT outlet_id, establishment_year, outlet_size, location_type, outlet_type, 'test'::text AS source_dataset
            FROM staging.stg_bigmart_test
        ) o
        WHERE outlet_id IS NOT NULL
    )
    INSERT INTO warehouse.dim_outlet (outlet_id, establishment_year, outlet_size, location_type, outlet_type)
    SELECT
        outlet_id,
        establishment_year,
        outlet_size,
        location_type,
        outlet_type
    FROM outlet_ranked
    WHERE rn = 1
    ON CONFLICT (outlet_id) DO UPDATE
    SET
        establishment_year = EXCLUDED.establishment_year,
        outlet_size = EXCLUDED.outlet_size,
        location_type = EXCLUDED.location_type,
        outlet_type = EXCLUDED.outlet_type,
        updated_at = CURRENT_TIMESTAMP;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def _reload_fact(conn: psycopg.Connection) -> None:
    sql = """
    TRUNCATE TABLE warehouse.fact_sales;

    INSERT INTO warehouse.fact_sales (
        product_key,
        outlet_key,
        mrp,
        product_visibility,
        outlet_sales,
        source_dataset,
        load_ts
    )
    SELECT
        dp.product_key,
        do2.outlet_key,
        s.mrp,
        s.product_visibility,
        s.outlet_sales,
        s.source_dataset,
        s.load_ts
    FROM (
        SELECT * FROM staging.stg_bigmart_train
        UNION ALL
        SELECT * FROM staging.stg_bigmart_test
    ) s
    JOIN warehouse.dim_product dp ON s.product_id = dp.product_id
    JOIN warehouse.dim_outlet do2 ON s.outlet_id = do2.outlet_id;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def load_to_postgres(train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    pg_config = get_pg_config()
    _ensure_database_exists(pg_config)
    conn = psycopg.connect(**pg_config, row_factory=dict_row)
    try:
        _run_sql_files(conn)
        _truncate_staging(conn)
        _copy_dataframe(conn, train_df, "staging.stg_bigmart_train")
        _copy_dataframe(conn, test_df, "staging.stg_bigmart_test")
        _upsert_dimensions(conn)
        _reload_fact(conn)
    finally:
        conn.close()
