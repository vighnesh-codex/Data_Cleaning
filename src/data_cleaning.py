"""
data_cleaning.py
-----------------
Loads the two raw files (List_of_Orders.csv, Order_Details.csv), merges them,
cleans the combined dataset, and saves the result to data/cleaned/sales_cleaned.csv.

Run from the project root:
    python src/data_cleaning.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CLEAN_DIR = Path(__file__).resolve().parent.parent / "data" / "cleaned"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)


def load_raw():
    orders = pd.read_csv(RAW_DIR / "List_of_Orders.csv")
    details = pd.read_csv(RAW_DIR / "Order_Details.csv")
    return orders, details


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    df = orders.copy()

    # Drop fully blank rows (trailing empty rows in the original export)
    df = df.dropna(how="all")

    # Standardize column names
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    # Drop rows with no Order_ID - can't be linked to anything
    df = df.dropna(subset=["Order_ID"])

    # Strip whitespace from text columns
    for col in ["CustomerName", "State", "City"]:
        df[col] = df[col].astype(str).str.strip()

    # Parse dates (source format is DD-MM-YYYY)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%d-%m-%Y", errors="coerce")

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    return df


def clean_details(details: pd.DataFrame) -> pd.DataFrame:
    df = details.copy()

    # Standardize column names
    df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]

    # Drop rows with no Order_ID - can't be linked to an order
    df = df.dropna(subset=["Order_ID"])

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # --- Quantity: fix mixed types ("6 units" -> 6), coerce to numeric ---
    df["Quantity"] = (
        df["Quantity"].astype(str).str.extract(r"(-?\d+)").astype(float)
    )
    # Negative quantities are impossible - treat magnitude as the real value
    df["Quantity"] = df["Quantity"].abs()
    df["Quantity"] = df["Quantity"].fillna(df["Quantity"].median()).astype(int)

    # --- Category: standardize casing / spelling ---
    cat_map = {
        "clothing": "Clothing", "clothing ": "Clothing",
        "electronics": "Electronics", "electronic": "Electronics",
        "furniture": "Furniture", "furniture ": "Furniture",
    }
    df["Category"] = df["Category"].astype(object).where(df["Category"].notna(), np.nan)
    df["Category"] = df["Category"].apply(
        lambda x: cat_map.get(str(x).strip().lower(), str(x).strip().title())
        if pd.notna(x) else np.nan
    )
    df.loc[df["Category"].isna(), "Category"] = df["Category"].mode()[0]

    # --- Sub-Category: fix common typos ---
    subcat_map = {
        "trouser": "Trousers", "trousers": "Trousers",
        "sarees": "Saree", "saree": "Saree",
        "tshirt": "T-Shirt", "t shirt": "T-Shirt", "t-shirt": "T-Shirt",
    }
    df["Sub_Category"] = df["Sub_Category"].astype(object).where(df["Sub_Category"].notna(), np.nan)
    df["Sub_Category"] = df["Sub_Category"].apply(
        lambda x: subcat_map.get(str(x).strip().lower(), str(x).strip())
        if pd.notna(x) else np.nan
    )
    df["Sub_Category"] = df["Sub_Category"].fillna("Unknown")

    # --- PaymentMode: standardize casing ---
    df["PaymentMode"] = df["PaymentMode"].astype(object).where(df["PaymentMode"].notna(), np.nan)
    df["PaymentMode"] = df["PaymentMode"].apply(
        lambda x: "COD" if pd.notna(x) and str(x).strip().lower() == "cod"
        else (str(x).strip() if pd.notna(x) else np.nan)
    )
    df["PaymentMode"] = df["PaymentMode"].fillna(df["PaymentMode"].mode()[0])

    # --- Amount: handle outliers (data-entry "extra digit" errors) ---
    # Impute missing Amount using the median for that Category
    df["Amount"] = df.groupby("Category")["Amount"].transform(
        lambda s: s.fillna(s.median())
    )
    # Cap extreme outliers using the IQR method (winsorize rather than drop,
    # to preserve row count for the linked order data)
    q1, q3 = df["Amount"].quantile([0.25, 0.75])
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    df["Amount_Outlier"] = df["Amount"] > upper_bound
    df["Amount"] = df["Amount"].clip(upper=upper_bound)

    # --- Profit: fill missing with category median ---
    df["Profit"] = df.groupby("Category")["Profit"].transform(
        lambda s: s.fillna(s.median())
    )

    return df


def merge_and_finalize(orders: pd.DataFrame, details: pd.DataFrame) -> pd.DataFrame:
    merged = details.merge(orders, on="Order_ID", how="inner")

    # Drop rows that still have no valid order date (can't analyze trends without it)
    merged = merged.dropna(subset=["Order_Date"])

    # Final duplicate check on the merged table
    merged = merged.drop_duplicates()

    # Reasonable column order
    cols = ["Order_ID", "Order_Date", "CustomerName", "State", "City",
            "Category", "Sub_Category", "Quantity", "Amount", "Profit",
            "PaymentMode", "Amount_Outlier"]
    merged = merged[cols]

    return merged.reset_index(drop=True)


def main():
    orders_raw, details_raw = load_raw()
    print(f"Raw orders: {orders_raw.shape}, Raw details: {details_raw.shape}")

    orders_clean = clean_orders(orders_raw)
    details_clean = clean_details(details_raw)
    print(f"Cleaned orders: {orders_clean.shape}, Cleaned details: {details_clean.shape}")

    final = merge_and_finalize(orders_clean, details_clean)
    print(f"Final merged & cleaned dataset: {final.shape}")

    out_path = CLEAN_DIR / "sales_cleaned.csv"
    final.to_csv(out_path, index=False)
    print(f"Saved cleaned dataset to {out_path}")

    print("\nMissing values remaining:\n", final.isna().sum())
    print("\nDuplicate rows remaining:", final.duplicated().sum())
    return final


if __name__ == "__main__":
    main()
