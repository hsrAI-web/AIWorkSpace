# Insight Studio Project Guide

Insight Studio brings three functional Streamlit analyzers into one application: a stock portfolio analyzer, an ad campaign performance analyzer, and a personal expense analyzer. Each runs with included fictional data and accepts a matching CSV upload. This guide records what was built, how to run it, how the calculations work, and the fixes and visual improvements made during development.

Repository: [hsrAI-web/AIWorkSpace](https://github.com/hsrAI-web/AIWorkSpace/tree/main/analyzer-suite). The project lives in `analyzer-suite/`. The local browser address is `http://127.0.0.1:8501/` while the Streamlit server is running.

## What was built

| Original path | Delivered application | Main capabilities |
| --- | --- | --- |
| Path A | Stock Portfolio Analyzer | Portfolio value, cost basis, unrealized gains, sector allocation, holding details, and historical snapshots |
| Path B | Ad Campaign Performance Analyzer | Spend, clicks, conversions, revenue, ROI, platform comparisons, campaign details, and time series |
| Path C | Personal Expense Analyzer | Expense totals, category and merchant breakdowns, daily trends, transactions, and monthly budget comparisons |

All three use a shared application shell. The **Choose an app** radio selector in the sidebar switches between them; they are not separate servers or separate web addresses. Select **Ad Campaigns** to open Path B.

## Getting started

Install Python 3.11 or later, download or clone the repository, and open a terminal in `analyzer-suite/`:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Open `http://localhost:8501/`. On Windows, `launch.bat` automates environment creation, dependency installation, and startup. It requires Python on PATH and internet access to install packages. Keep the server terminal running; Ctrl+C stops it. The local address does not host the app for other people or remain available after the server stops.

The current requirements are Streamlit 1.65 or later below version 2, and pandas 2.2 or later below version 4. No API key, live market feed, ad account, or database is needed.

## Using the dashboards

1. Choose an analyzer in the sidebar. It loads the included sample CSV automatically.
2. Adjust its date range and category filters. Campaign views also share platform and campaign filters; stocks also support symbol selection.
3. Switch among the tabs to explore the filtered data.
4. Use **Upload your CSV** to replace the sample dataset for that analyzer.
5. Use **Download sample CSV** as a template or **Export filtered data** to download the displayed records or summaries where available.

Empty filter results show an explanatory message. A partially selected date range prompts for both dates. A malformed CSV shows an error instead of attempting analysis.

## Stock portfolio features and calculations

The latest date in the filtered dataset supplies the holdings snapshot. Its metrics show total portfolio value, total cost basis, unrealized gain, and return on cost. Overview charts compare sector allocation and gains by symbol; an insight identifies the largest holding. The Holdings tab includes a return percentage and CSV export. History plots aggregate value and cost by date and exports filtered historical rows.

| Measure | Calculation |
| --- | --- |
| Holding value | Shares × price |
| Holding cost | Shares × average purchase price per share |
| Unrealized gain | Holding value − holding cost |
| Portfolio return on cost | Total unrealized gain / total cost |
| Holding return percentage | Holding unrealized gain / holding cost × 100 |

Each date/symbol pair must be unique. Provide complete dated snapshots to make history comparable. The latest snapshot includes only symbols present on that date; missing symbols are not carried forward. Historical value changes can reflect both price movements and changes in holdings. These calculations exclude dividends, fees, and realized gains and are not time-weighted returns.

## Ad campaign features and calculations

The campaign dashboard has four tabs: **Overview**, **Platform comparison**, **Campaign details**, and **Time series**. Sidebar date, platform, and campaign selections apply to all four. Overview reports spend, clicks, conversions, ROI, revenue, ROAS, click-through rate, and conversion rate. Platform and campaign summaries include additional acquisition-cost metrics and exports. The time-series view lets the user chart spend, clicks, conversions, or revenue by platform.

| Measure | Calculation |
| --- | --- |
| ROI | (Attributed revenue − spend) / spend |
| ROAS | Attributed revenue / spend |
| Click-through rate | Clicks / impressions |
| Conversion rate | Conversions / clicks |
| CPC | Spend / clicks |
| CPA | Spend / conversions |

Summary ratios are calculated from summed inputs rather than averaged row percentages. Zero denominators produce a dash in formatted metrics or a blank numeric result in summary tables. ROI uses advertising spend only; it does not include product costs, salaries, or other business expenses. Revenue comes from the CSV and no attribution model is implemented.

## Personal expense features and calculations

Path C was implemented as a personal expense analyzer. Its metrics show total expenses, transaction count, average transaction amount, and average spending across months present in the filtered data. Overview shows category totals, daily spending, and the five merchants with the highest totals. Transactions can be exported. The Budget tracker compares each represented month's spending against an editable monthly budget, with remaining budget calculated as budget minus spending.

Budget comparisons use the full monthly budget against filtered expenses. Selecting a partial month or a subset of categories can understate overall spending. Months with no filtered transactions are not added to the monthly average. Negative amounts and refunds are not supported.

## Sample data and CSV contracts

All sample data is synthetic, denominated in USD, and dated from January 1 through June 30, 2026. The generator uses random seed 42 for reproducible examples. Stock samples contain six fictional symbols across five sectors. Campaign samples contain six campaigns across Google, Meta, and LinkedIn. Expenses include housing, utilities, groceries, dining, transport, shopping, and entertainment.

| File | Required columns |
| --- | --- |
| `data/stocks.csv` | `date,symbol,sector,shares,cost_basis,price` |
| `data/campaigns.csv` | `date,campaign,platform,spend,impressions,clicks,conversions,revenue` |
| `data/expenses.csv` | `date,category,merchant,amount,payment_method` |

Use YYYY-MM-DD dates and numeric amounts without currency signs or thousands separators. Required columns and values must be present. Numbers must be finite, nonnegative, and no greater than 10^15. Text labels are trimmed and cannot be blank. Campaign conversions cannot exceed clicks, and clicks cannot exceed impressions. Additional columns are ignored. Campaign counts are numeric but integer-only validation is not implemented.

Regenerate the included samples with:

```powershell
.\.venv\Scripts\python scripts/generate_data.py
```

This replaces the three included sample CSVs.

## Visual improvements

The initial neutral interface was updated with a soft blue-to-mint-to-lavender page gradient and a navy-to-teal sidebar. Metric cards have white backgrounds, rounded corners, subtle shadows, and teal, purple, amber, or pink top accents. Charts and tables have bordered white containers. Tabs received additional styling, and metric text was reduced responsively to improve fit in the narrow preview.

Theme colors are configured in `.streamlit/config.toml`; additional CSS is embedded near the beginning of `app.py`. These shared styles apply to all three analyzers. Some CSS selectors depend on Streamlit's rendered structure and may need adjustment after a framework upgrade. Browser inspection confirmed that the updated dashboard rendered; automated visual regression tests are not included.

## Testing performed

The Streamlit AppTest script exercised all three analyzers and passed before publication. It checks initial rendering without exceptions, stock valuation against the sample CSV, stock sector filters, empty selections, campaign total spend and aggregate ROI, Google-only spend after filtering, time-series metric selection, expense totals, and a zero monthly budget.

Run the checks with:

```powershell
.\.venv\Scripts\python scripts/test_apps.py
```

The tests cover sample-data interactions and selected calculations. They do not exhaustively test malformed uploads, file downloads, visual contrast, or every date-range combination. The styling update was inspected in the browser.

## Fix for the Not Found error

The first local server started with Streamlit's internal development mode enabled. The Python server responded to its health endpoint, but development mode expected a separate frontend server, so the dashboard page returned **Not Found**. Checking server health alone did not catch the missing page.

The configuration now explicitly sets:

```toml
[global]
developmentMode = false
```

Restarting with this setting enabled the packaged frontend and the dashboard was verified in the browser. If the page cannot be reached later, first confirm that the server is running, check the address printed by Streamlit, and review the terminal for errors. Refresh after changes; configuration changes may require a restart.

## Repository publication

The source and supporting files were published to the private `hsrAI-web/AIWorkSpace` repository on `main`. Existing repository content was retained and the root README now links to the suite. Initial Git access attempts failed because local credentials were unavailable; publication succeeded after the GitHub connection became available.

- [Initial application publication](https://github.com/hsrAI-web/AIWorkSpace/commit/3cd01c39bb7170b645dbfeb882d1a602689a4c34)
- [Background and styling update](https://github.com/hsrAI-web/AIWorkSpace/commit/72afa9fe5c74ea8814195c69052c21218425dfa5)

Publishing source to GitHub did not deploy a public hosted dashboard. The app currently runs locally. Temporary downloaded dependencies, scratch files, and virtual environments were excluded from publication.

## Project file map

| Location | Purpose |
| --- | --- |
| `app.py` | Shared navigation, CSV validation, filters, metrics, charts, exports, and styling |
| `.streamlit/config.toml` | Frontend mode and theme configuration |
| `requirements.txt` | Python dependencies |
| `launch.bat` | Windows setup and launch helper |
| `README.md` | Quick setup and CSV reference |
| `data/` | Three sample CSVs |
| `scripts/generate_data.py` | Reproducible synthetic data generator |
| `scripts/test_apps.py` | Automated interaction and calculation checks |
| `docs/PROJECT_GUIDE.md` | Detailed implementation and usage guide |
| `docs/dashboard-working.png` | Original working-dashboard screenshot |
| `.gitignore` | Excludes virtual environments, Python caches, and local secrets |

## Current scope and possible extensions

This is a functional CSV-based demonstration. It has no user accounts, persistent database, live data synchronization, portfolio trading, ad-account integration, or public deployment. Uploaded data is processed for the active app session and the code does not deliberately save uploaded files to disk.

Possible next steps include independent page URLs, hosted deployment, live data connectors, more detailed input validation, improved currency selection and table formatting, and broader tests. These are extensions, not features currently delivered.
