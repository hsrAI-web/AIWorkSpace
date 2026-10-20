# AIWorkSpace
AI related work

## Insight Studio — three Streamlit analyzers

[Open the project and setup instructions](analyzer-suite/README.md).

- Stock Portfolio Analyzer: holdings, allocation, unrealized returns, and history.
- Ad Campaign Performance Analyzer: overview, platform comparisons, campaign details, and time series with shared filters.
- Personal Expense Analyzer: spending trends and monthly budgets.

Includes synthetic sample CSVs, uploads, exports, a Windows launcher, sample-data generator, and interaction tests.

```powershell
cd analyzer-suite
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

## Health claim preparation assistant

[Open the project and setup instructions](claim-preparation-assistant/README.txt).

Insurance reimbursement paperwork prototype with LangGraph, local hybrid retrieval, four chunking comparisons, cited draft answers, and a 15-question evaluation. Includes documented failures and limitations; it does not determine coverage or claim approval.
