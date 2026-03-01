# Northern Virginia & Falls Church Housing Price Analysis

Statistical analysis of housing price appreciation in Northern Virginia vs Falls Church, with pre/post-2020 comparison.

## Overview

This project analyzes monthly median housing prices for two Northern Virginia submarkets —
**Northern Virginia (NOVA)** and **Falls Church** — from June 2018 onwards.

The analysis includes:

- **Price trend visualization** — monthly price charts for both regions over time
- **OLS regression** — linear fit over the full period, with fitted line and residual plots annotated with slope and R²
- **Pre/post-2020 windowed analysis** — separate trend lines to capture the COVID-era acceleration in prices
- **Ridge regression cross-validation** — time-series CV comparing regularization strengths (α = 0, 1, 10)

## Explanation of Charts
**1 - Price Trends Over Time** 

  This chart shows the monthly median sale prices for Falls Church, VA and Northern Virginia as a whole. It gives a view of how prices in both markets changed pre-, post, and during 2020. It makes it easy to compare the regions side by side. 
  
**2 - NOVA OLS Regression & Residuals**

  This chart has two panels. The left pannel shows a best-fit linear trend line for Northern Virginia's prices. The title displays the slope (dollars gained per month on average) and R^2, which measures how well the line explains the price movement. The right panel displays the residuals, which are the differences between the actual price and the model's prediction. This is important because it makes it clear that linear models don't always capture everything.
  
**3 - Falls Church OLS Regression & Residuals**

  This chart has the same layout as the previous chart but for Falls Church. Comparing the two reveals the differences in the regions and how well a simple linear model fits each one. 

**4 - Pre vs Post-202 Windowed Analysis**

  This chart fits two separate lines for each region, one before January 2020 and one onwards. This is used to help answer the question: did the pandemic-era market represent a genuine structural shift in price growth, or a temporary spike?
  
## Requirements

- Python 3.8+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Data

Housing price data is sourced from [Zillow Research](https://www.zillow.com/research/data/).
The data file is **not included** in this repository.

To run the script, place an Excel file named `Housing Price Data.xlsx` in the project root
with a sheet named `Price Data` containing the following columns:

| Column | Description |
|---|---|
| `Month Index` | 1-based integer month index (1 = June 2018) |
| `NOVA Price` | Northern Virginia median sale price |
| `Falls Church Price` | Falls Church median sale price |

## Usage

```bash
python analysis.py
```

## Output

Running the script produces 4 matplotlib figures and printed summaries:

1. **Price Trends** — Line chart of monthly median prices for both regions over time.
2. **NOVA OLS Regression** — Actual prices vs fitted line, plus a residual plot annotated with slope and R².
3. **Falls Church OLS Regression** — Same layout as above for Falls Church.
4. **Pre vs Post-2020 Windowed Analysis** — Side-by-side panels showing how each region's price trend shifted before and after January 2020.

Printed output includes slope ($/month), R², and residual variance for each model, plus mean RMSE
from Ridge regression cross-validation.
