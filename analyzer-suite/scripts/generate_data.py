from pathlib import Path
import random
import pandas as pd

rng = random.Random(42)
out = Path(__file__).resolve().parents[1] / 'data'
out.mkdir(parents=True, exist_ok=True)
dates = pd.date_range('2026-01-01', '2026-06-30')
stocks = [('NOVA', 'Technology', 35, 120), ('BYTE', 'Technology', 50, 75), ('CARE', 'Healthcare', 45, 95), ('GRID', 'Energy', 80, 42), ('BANK', 'Financials', 60, 65), ('SHOP', 'Consumer', 40, 110)]
rows = []
prices = {s: cost * rng.uniform(.9, 1.1) for s, _, _, cost in stocks}
for date in dates:
    for symbol, sector, shares, cost in stocks:
        prices[symbol] *= 1 + rng.gauss(.0005, .012)
        rows.append([date.date(), symbol, sector, shares, cost, round(prices[symbol], 2)])
pd.DataFrame(rows, columns=['date', 'symbol', 'sector', 'shares', 'cost_basis', 'price']).to_csv(out/'stocks.csv', index=False)
rows = []
for date in dates:
    for platform, campaign, ctr, conv in [('Google', 'Search Intent', .045, .065), ('Meta', 'Social Discovery', .022, .04), ('LinkedIn', 'B2B Leads', .012, .09)]:
        for variant in ['Prospecting', 'Retargeting']:
            impressions = rng.randint(2000, 9000)
            clicks = int(impressions * ctr * rng.uniform(.8, 1.2))
            conversions = int(clicks * conv * (1.3 if variant == 'Retargeting' else 1))
            spend = round(clicks * rng.uniform(.7, 2.3), 2)
            revenue = round(conversions * rng.uniform(30, 90), 2)
            rows.append([date.date(), campaign+' / '+variant, platform, spend, impressions, clicks, conversions, revenue])
pd.DataFrame(rows, columns=['date', 'campaign', 'platform', 'spend', 'impressions', 'clicks', 'conversions', 'revenue']).to_csv(out/'campaigns.csv', index=False)
rows = []
for date in dates:
    if date.day == 1:
        rows.append([date.date(), 'Housing', 'Apartment Rent', 1100, 'Bank transfer'])
    if date.day == 5:
        rows.append([date.date(), 'Utilities', 'City Utilities', round(rng.uniform(100, 160), 2), 'Bank transfer'])
    for _ in range(rng.randint(0, 3)):
        category, merchant, low, high = rng.choice([('Groceries', 'Fresh Market', 15, 85), ('Dining', 'Corner Cafe', 5, 38), ('Transport', 'Metro & Rides', 3, 22), ('Shopping', 'Everyday Store', 15, 95), ('Entertainment', 'Cinema & Events', 10, 45)])
        rows.append([date.date(), category, merchant, round(rng.uniform(low, high), 2), rng.choice(['Debit card', 'Credit card', 'Cash'])])
pd.DataFrame(rows, columns=['date', 'category', 'merchant', 'amount', 'payment_method']).to_csv(out/'expenses.csv', index=False)
print('Created three sample CSVs')

