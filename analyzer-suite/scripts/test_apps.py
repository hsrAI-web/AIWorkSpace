from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest

root = Path(__file__).resolve().parents[1]
at = AppTest.from_file(str(root/'app.py'), default_timeout=30).run()
assert not at.exception, at.exception
stocks = pd.read_csv(root/'data/stocks.csv')
latest = stocks[stocks.date.eq(stocks.date.max())]
expected = (latest.shares * latest.price).sum()
assert at.metric[0].value == f'${expected:,.2f}'
at.multiselect[0].set_value(['Technology']).run()
assert not at.exception
at.multiselect[0].set_value([]).run()
assert not at.exception and any('No rows' in x.value for x in at.info)
at.radio[0].set_value('Ad Campaigns').run()
assert not at.exception, at.exception
ads = pd.read_csv(root/'data/campaigns.csv')
assert at.metric[0].value == f'${ads.spend.sum():,.2f}'
expected_roi = (ads.revenue.sum()-ads.spend.sum())/ads.spend.sum()
assert at.metric[3].value == f'{expected_roi:.1%}'
at.multiselect[0].set_value(['Google']).run()
assert not at.exception
assert at.metric[0].value == f'${ads[ads.platform.eq("Google")].spend.sum():,.2f}'
at.selectbox[0].set_value('conversions').run()
assert not at.exception
at.radio[0].set_value('Personal Expenses').run()
assert not at.exception, at.exception
expenses = pd.read_csv(root/'data/expenses.csv')
assert at.metric[0].value == f'${expenses.amount.sum():,.2f}'
at.number_input[0].set_value(0).run()
assert not at.exception
at.multiselect[0].set_value([]).run()
assert not at.exception and any('No rows' in x.value for x in at.info)
print('PASS: all three apps, portfolio values, weighted ROI, platform filters, empty filters, trend selection, and zero budget')

