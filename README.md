# Data Cleaning & Visualization — E-Commerce Sales

Cleans, analyzes, and visualizes an India retail order dataset (2018) using Python (Pandas, NumPy, Matplotlib, Seaborn).

## Project Overview

This project takes a raw e-commerce order dataset, cleans it, performs exploratory analysis, and produces a set of visualizations and business insights. It follows a full data-analysis workflow: dataset selection → cleaning → analysis → visualization → insights → documentation.

## Dataset

Two source files, combined on `Order ID`:

| File | Description |
|---|---|
| `data/raw/List_of_Orders.csv` | Order metadata — Order ID, Order Date, Customer Name, State, City (560 rows) |
| `data/raw/Order_Details.csv` | Order line items — Amount, Profit, Quantity, Category, Sub-Category, Payment Mode (764 rows) |

Both raw files are kept **unmodified** in `data/raw/`. The dataset contains realistic data-quality issues: missing values, duplicate rows, inconsistent text casing/spelling, mixed data types, negative quantities, and Amount outliers.

## Project Structure

```
data-cleaning-visualization/
├── data/
│   ├── raw/                    # Original, unmodified data
│   │   ├── List_of_Orders.csv
│   │   └── Order_Details.csv
│   └── cleaned/
│       └── sales_cleaned.csv   # Cleaned, merged dataset
├── notebooks/
│   └── sales_analysis.ipynb    # Full walkthrough: load → clean → analyze → visualize
├── src/
│   ├── data_cleaning.py        # Reusable cleaning functions
│   └── analysis_and_viz.py     # Analysis + chart generation script
├── visualizations/
│   ├── category_sales.png
│   ├── monthly_sales.png
│   ├── regional_sales.png
│   ├── amount_distribution.png
│   ├── boxplot_outliers.png
│   └── correlation_heatmap.png
├── README.md
├── requirements.txt
└── .gitignore
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Project

**Option A — scripts:**
```bash
python src/data_cleaning.py       # produces data/cleaned/sales_cleaned.csv
python src/analysis_and_viz.py    # produces charts in visualizations/
```

**Option B — notebook (recommended, includes narrative + insights):**
```bash
jupyter notebook notebooks/sales_analysis.ipynb
```

## Data-Cleaning Steps

- Dropped fully blank rows (export artifact) and rows with no Order ID
- Standardized column names (spaces → underscores)
- Parsed `Order Date` from text to datetime
- Removed exact duplicate rows in both source files
- Fixed mixed-type `Quantity` values (e.g. `"6 units"` → `6`) and corrected negative quantities
- Standardized inconsistent `Category` / `Sub-Category` / `PaymentMode` text (casing, spelling, whitespace)
- Imputed missing `Amount` and `Profit` using category-level medians
- Detected and capped `Amount` outliers using the IQR method
- Merged the two cleaned tables into one analysis-ready dataset

## Analysis & Visualizations

| Chart | Shows |
|---|---|
| `category_sales.png` | Total sales by category (bar chart) |
| `monthly_sales.png` | Sales trend over time (line chart) |
| `regional_sales.png` | Top 10 states by sales |
| `amount_distribution.png` | Distribution of order amounts (histogram) |
| `boxplot_outliers.png` | Order amount spread & outliers by category (box plot) |
| `correlation_heatmap.png` | Correlation between Amount, Profit, and Quantity |

## Key Findings

1. **Furniture** drives the most revenue; **Electronics** is the most profitable category by total profit.
2. **Clothing** underperforms on both revenue and profit.
3. **Maharashtra** and **Madhya Pradesh** lead all states in total sales.
4. Order amounts are **right-skewed**, with a long tail of high-value Furniture/Electronics orders.
5. **Quantity has little correlation with Profit** — profitability is driven more by category/pricing than order size.

See `notebooks/sales_analysis.ipynb` for the full narrative and the final report for a formatted write-up.

## License

The raw data in this project is a synthetically-completed dataset built around real Indian order records for educational/portfolio use.
