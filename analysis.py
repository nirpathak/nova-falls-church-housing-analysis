"""
Housing Price Analysis — Northern Virginia & Falls Church

Loads monthly median housing prices from an Excel file, visualizes trends,
and fits OLS and Ridge regression models to quantify price growth over time.

Regions analyzed:
  - Northern Virginia (NOVA)
  - Falls Church

Models:
  - OLS (overall, and split pre/post-2020)
  - Ridge regression with time-series cross-validation
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import Ridge
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import TimeSeriesSplit



DATA_FILE = Path(__file__).parent / "Housing Price Data.xlsx"
SHEET_NAME = "Price Data"
START_DATE = "2018-06-01"
REGIONS = ["Northern_VA", "Falls_Church"]
REGION_COLORS = {"Northern_VA": "tab:blue", "Falls_Church": "tab:orange"}
REGION_LABELS = {"Northern_VA": "Northern Virginia", "Falls_Church": "Falls Church"}


# Data Loading



def load_data(filepath: Path) -> pd.DataFrame:
    """
    Load and reshape the housing price Excel file into long format.

    Parameters:
        filepath: Path to the Excel sheet

    Returns:
        A dataframe with columns region, price, date, t (1-based month index).
    """
    df_wide = pd.read_excel(filepath, sheet_name=SHEET_NAME)

    df_long = df_wide.melt(
        id_vars=["Month Index"],
        value_vars=["NOVA Price", "Falls Church Price"],
        var_name="region",
        value_name="price",
    )

    df_long["region"] = df_long["region"].replace(
        {"NOVA Price": "Northern_VA", "Falls Church Price": "Falls_Church"}
    )

    # Build calendar dates from the numeric month index
    n_months = df_long["Month Index"].max()
    all_dates = pd.date_range(start=START_DATE, periods=n_months, freq="MS")
    zero_based_index = df_long["Month Index"] - 1
    df_long["date"] = all_dates[zero_based_index.values]
    df_long["t"] = df_long["Month Index"]

    print(f"Loaded {len(df_long)} rows | {df_long['region'].nunique()} regions | "
          f"{df_long['price'].isna().sum()} missing prices")
    return df_long


# Visualization — Price Trends


def plot_price_trends(df: pd.DataFrame) -> None:
    """
    Plot monthly median housing prices for each region over time.
    """
    _, ax = plt.subplots(figsize=(10, 4))

    for region in REGIONS:
        region_df = df[df["region"] == region]
        ax.plot(
            region_df["date"],
            region_df["price"],
            label=REGION_LABELS[region],
            color=REGION_COLORS[region],
            linewidth=2,
        )

    ax.set_xlabel("Date")
    ax.set_ylabel("Median Price ($)")
    ax.set_title("Monthly Median Housing Prices Over Time")
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()


# OLS Regression (Ordinary Least Squares)


def run_ols_regression(df: pd.DataFrame, region: str):
    """
    Fit an OLS linear regression of price and time for a single region.

    Parameters:
        df: long DataFrame.
        region: Region string (e.g. 'Northern_VA').

    Returns:
        Fitted statsmodels RegressionResults object.
    """
    region_df = df[df["region"] == region]
    X = sm.add_constant(region_df["t"])
    y = region_df["price"]
    return sm.OLS(y, X).fit()


def plot_regression_results(df: pd.DataFrame, region: str, results) -> None:
    """
    Plot the OLS fitted line and residuals for a region.

    Parameters:
        df:      Full long DataFrame.
        region:  Region identifier string.
        results: Fitted statsmodels RegressionResults object.
    """
    region_df = df[df["region"] == region].copy()
    region_df["fitted"] = results.fittedvalues
    region_df["residuals"] = results.resid

    label = REGION_LABELS[region]
    color = REGION_COLORS[region]
    slope = results.params["t"]
    r2 = results.rsquared

    _, (ax_fit, ax_resid) = plt.subplots(1, 2, figsize=(13, 4))

    # actual vs fitted 
    ax_fit.scatter(region_df["date"], region_df["price"],
                   color=color, alpha=0.6, s=25, label="Actual")
    ax_fit.plot(region_df["date"], region_df["fitted"],
                color="black", linewidth=2, label="OLS fit")
    ax_fit.set_title(
        f"{label} — OLS Regression\n"
        f"Slope: ${slope:,.0f}/month  |  R² = {r2:.3f}"
    )
    ax_fit.set_xlabel("Date")
    ax_fit.set_ylabel("Median Price ($)")
    ax_fit.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax_fit.legend()

    #  Right: residuals
    ax_resid.axhline(0, color="black", linewidth=1, linestyle="--")
    ax_resid.scatter(region_df["date"], region_df["residuals"],
                     color=color, alpha=0.6, s=25)
    ax_resid.set_title(f"{label} — Residuals")
    ax_resid.set_xlabel("Date")
    ax_resid.set_ylabel("Residual ($)")
    ax_resid.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    plt.tight_layout()


# Windowed Analysis (Pre / Post 2020)


def run_windowed_analysis(df: pd.DataFrame) -> None:
    """
    Fit separate OLS models for pre-2020 and post-2020 periods and plot results.

    Prints slope and R² for each window/region combination, and visualizes
    the fitted lines for both windows on a single chart per region.
    """
    windows = {
        "Pre-2020": df["date"] < "2020-01-01",
        "Post-2020": df["date"] >= "2020-01-01",
    }
    window_colors = {"Pre-2020": "steelblue", "Post-2020": "darkorange"}

    print("\n--- Windowed OLS (Pre / Post 2020) ---")

    _, axes = plt.subplots(1, len(REGIONS), figsize=(13, 4), sharey=False)

    for ax, region in zip(axes, REGIONS):
        region_df = df[df["region"] == region]
        ax.scatter(region_df["date"], region_df["price"],
                   color=REGION_COLORS[region], alpha=0.4, s=20, label="Actual")

        for window_name, mask in windows.items():
            subset = df[mask & (df["region"] == region)]
            X = sm.add_constant(subset["t"])
            model = sm.OLS(subset["price"], X).fit()
            slope = model.params["t"]
            r2 = model.rsquared

            print(f"  {REGION_LABELS[region]} | {window_name}: "
                  f"slope=${slope:,.0f}/mo  R²={r2:.3f}")

            ax.plot(subset["date"], model.fittedvalues,
                    color=window_colors[window_name], linewidth=2,
                    label=f"{window_name} fit")

        ax.set_title(f"{REGION_LABELS[region]} — Pre vs Post 2020")
        ax.set_xlabel("Date")
        ax.set_ylabel("Median Price ($)")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.legend(fontsize=8)

    plt.tight_layout()


# Ridge Regression with Time-Series Cross-Validation


def run_ridge_crossval(df: pd.DataFrame) -> None:
    """
    Evaluate Ridge regression models using time-series cross-validation.

    Tests three regularization strengths (alpha = 0, 1, 10) and prints
    the mean RMSE across 5 time-series folds.
    """
    X = df[["t"]]
    y = df["price"]
    tscv = TimeSeriesSplit(n_splits=5)
    alphas = [0.0, 1.0, 10.0]

    print("\n--- Ridge Regression Cross-Validation (all regions combined) ---")

    mean_rmses = []
    for alpha in alphas:
        fold_rmses = []
        for train_idx, test_idx in tscv.split(X):
            model = Ridge(alpha=alpha)
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            y_pred = model.predict(X.iloc[test_idx])
            rmse = root_mean_squared_error(y.iloc[test_idx], y_pred)
            fold_rmses.append(rmse)

        mean_rmse = np.mean(fold_rmses)
        mean_rmses.append(mean_rmse)
        label = "≈ OLS" if alpha == 0.0 else f"alpha={alpha}"
        print(f"  Ridge ({label}): mean RMSE = ${mean_rmse:,.0f}")

    # Bar chart comparing mean RMSE across alpha values
    _, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        [str(a) for a in alphas],
        mean_rmses,
        color=["steelblue", "darkorange", "seagreen"],
        edgecolor="black",
        width=0.5,
    )
    ax.set_xlabel("Ridge Alpha (regularization strength)")
    ax.set_ylabel("Mean RMSE ($)")
    ax.set_title(
        "Ridge Regression — Mean RMSE by Alpha\n"
        "(Time-Series Cross-Validation, 5 folds)"
    )
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()


# Main Function

def main() -> None:
    """
    Run the full housing price analysis pipeline.
    """
    # 1. Load data
    df = load_data(DATA_FILE)

    # 2. Visualize raw price trends
    plot_price_trends(df)

    # 3. OLS regression — overall trend
    print("\n--- OLS Regression (overall) ---")
    ols_results = {}
    for region in REGIONS:
        results = run_ols_regression(df, region)
        ols_results[region] = results
        print(f"  {REGION_LABELS[region]}: "
              f"slope=${results.params['t']:,.0f}/mo  "
              f"R²={results.rsquared:.3f}  "
              f"Residual variance=${results.mse_resid:,.0f}")

    # 4. Visualize OLS fits and residuals
    for region in REGIONS:
        plot_regression_results(df, region, ols_results[region])

    # 5. Windowed analysis (pre / post 2020)
    run_windowed_analysis(df)

    # 6. Ridge regression cross-validation
    run_ridge_crossval(df)

    # Show all figures at once
    plt.show()

#Only run the main() function the script is being run directly. 
if __name__ == "__main__":
    main()
