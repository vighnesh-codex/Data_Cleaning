"""
analysis_and_viz.py
--------------------
Loads the cleaned dataset, computes summary statistics, and generates
the required visualizations into the visualizations/ folder.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "cleaned" / "sales_cleaned.csv"
VIZ_DIR = ROOT / "visualizations"
VIZ_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110


def load():
    df = pd.read_csv(CLEAN_PATH, parse_dates=["Order_Date"])
    return df


def summary_stats(df: pd.DataFrame):
    print("=== Summary statistics ===")
    print(df[["Amount", "Profit", "Quantity"]].describe())

    print("\n=== Sales by Category ===")
    print(df.groupby("Category")["Amount"].sum().sort_values(ascending=False))

    print("\n=== Sales by State (top 10) ===")
    print(df.groupby("State")["Amount"].sum().sort_values(ascending=False).head(10))

    print("\n=== Profit by Category ===")
    print(df.groupby("Category")["Profit"].sum().sort_values(ascending=False))

    return df


def chart_category_sales(df):
    cat_sales = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=cat_sales.index, y=cat_sales.values, hue=cat_sales.index,
                      palette="viridis", legend=False)
    ax.set_title("Total Sales Amount by Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Category")
    ax.set_ylabel("Total Sales Amount (₹)")
    for i, v in enumerate(cat_sales.values):
        ax.text(i, v, f"₹{v:,.0f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "category_sales.png")
    plt.close()


def chart_monthly_trend(df):
    monthly = df.set_index("Order_Date").resample("ME")["Amount"].sum()
    plt.figure(figsize=(9, 5))
    plt.plot(monthly.index, monthly.values, marker="o", color="#2563eb", linewidth=2)
    plt.title("Monthly Sales Trend", fontsize=14, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("Total Sales Amount (₹)")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "monthly_sales.png")
    plt.close()


def chart_regional_sales(df):
    state_sales = df.groupby("State")["Amount"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(9, 6))
    ax = sns.barplot(y=state_sales.index, x=state_sales.values, hue=state_sales.index,
                      palette="mako", legend=False, orient="h")
    ax.set_title("Top 10 States by Sales Amount", fontsize=14, fontweight="bold")
    ax.set_xlabel("Total Sales Amount (₹)")
    ax.set_ylabel("State")
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "regional_sales.png")
    plt.close()


def chart_amount_histogram(df):
    plt.figure(figsize=(8, 5))
    sns.histplot(df["Amount"], bins=30, kde=True, color="#7c3aed")
    plt.title("Distribution of Order Amounts", fontsize=14, fontweight="bold")
    plt.xlabel("Order Amount (₹)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "amount_distribution.png")
    plt.close()


def chart_boxplot_outliers(df):
    plt.figure(figsize=(8, 5))
    ax = sns.boxplot(x="Category", y="Amount", hue="Category", data=df,
                      palette="Set2", legend=False)
    ax.set_title("Order Amount by Category (Outlier Detection)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Category")
    ax.set_ylabel("Order Amount (₹)")
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "boxplot_outliers.png")
    plt.close()


def chart_correlation_heatmap(df):
    numeric_cols = df[["Amount", "Profit", "Quantity"]]
    corr = numeric_cols.corr()
    plt.figure(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1, square=True)
    plt.title("Correlation Heatmap (Amount, Profit, Quantity)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "correlation_heatmap.png")
    plt.close()


def main():
    df = load()
    summary_stats(df)
    chart_category_sales(df)
    chart_monthly_trend(df)
    chart_regional_sales(df)
    chart_amount_histogram(df)
    chart_boxplot_outliers(df)
    chart_correlation_heatmap(df)
    print(f"\nSaved 6 charts to {VIZ_DIR}")


if __name__ == "__main__":
    main()
