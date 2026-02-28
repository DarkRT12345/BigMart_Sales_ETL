from __future__ import annotations

import pandas as pd

from config import TEST_PATH, TRAIN_PATH


FAT_CONTENT_MAP = {
    "lf": "Low Fat",
    "low fat": "Low Fat",
    "reg": "Regular",
}


def _standardize_fat_content(series: pd.Series) -> pd.Series:
    clean = series.astype(str).str.strip()
    return clean.str.lower().replace(FAT_CONTENT_MAP).str.title().replace({"Low Fat": "Low Fat"})


def _fill_weight(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    product_weight_median = result.groupby("ProductID")["Weight"].transform("median")
    global_median = result["Weight"].median()
    result["Weight"] = result["Weight"].fillna(product_weight_median).fillna(global_median)
    return result


def _normalize_common(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["FatContent"] = _standardize_fat_content(result["FatContent"])
    result["OutletSize"] = result["OutletSize"].fillna("Unknown")
    result["ProductVisibility"] = result["ProductVisibility"].fillna(0.0)
    return _fill_weight(result)


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(
        columns={
            "ProductID": "product_id",
            "Weight": "weight",
            "FatContent": "fat_content",
            "ProductVisibility": "product_visibility",
            "ProductType": "product_type",
            "MRP": "mrp",
            "OutletID": "outlet_id",
            "EstablishmentYear": "establishment_year",
            "OutletSize": "outlet_size",
            "LocationType": "location_type",
            "OutletType": "outlet_type",
            "OutletSales": "outlet_sales",
        }
    )


def extract_and_transform() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(TRAIN_PATH)
    test = pd.read_csv(TEST_PATH)

    train = _normalize_common(train)
    test = _normalize_common(test)
    test["OutletSales"] = None

    train["source_dataset"] = "train"
    test["source_dataset"] = "test"

    train = _rename_columns(train)
    test = _rename_columns(test)

    expected_cols = [
        "product_id",
        "weight",
        "fat_content",
        "product_visibility",
        "product_type",
        "mrp",
        "outlet_id",
        "establishment_year",
        "outlet_size",
        "location_type",
        "outlet_type",
        "outlet_sales",
        "source_dataset",
    ]

    return train[expected_cols], test[expected_cols]
