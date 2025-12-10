import pandas as pd
import numpy as np

# Config
lookback_months = 2   # change to 1 or 2 etc.

# Load data
df = pd.read_csv("Nifty750_tradetiger(Goldbees).csv", low_memory=False)

# Standardize columns
# df.rename(columns={
#     "DATE": "Date",
#     "SERIES": "Series",
#     "OPEN": "Open",
#     "HIGH": "High",
#     "LOW": "Low",
#     "PREV. CLOSE": "Prev.close",
#     "LTP": "Ltp",
#     "CLOSE": "Close",
#     "VWAP": "Vwap",
#     "52W H": "52W H",
#     "52W L": "52W L",
#     "VOLUME": "Volume",
#     "VALUE": "Value",
#     "NO OF TRADES": "No Of Trades",
#     "SYMBOL": "Symbol"
# }, inplace=True)
# --- WATCHLIST FILTERING ---
# Define your watchlist
Nifty_fno = [
    '360ONE', 'ABB', 'APLAPOLLO', 'AUBANK', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS',
    'ABCAPITAL', 'ALKEM', 'AMBER', 'AMBUJACEM', 'ANGELONE', 'APOLLOHOSP', 'ASHOKLEY', 'ASIANPAINT',
    'ASTRAL', 'AUROPHARMA', 'DMART', 'AXISBANK', 'BSE', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV',
    'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'BDL', 'BEL', 'BHARATFORG', 'BHEL', 'BPCL', 'BHARTIARTL',
    'BIOCON', 'BLUESTARCO', 'BOSCHLTD', 'BRITANNIA', 'CGPOWER', 'CANBK', 'CDSL', 'CHOLAFIN', 'CIPLA',
    'COALINDIA', 'COFORGE', 'COLPAL', 'CAMS', 'CONCOR', 'CROMPTON', 'CUMMINSIND', 'CYIENT', 'DLF',
    'DABUR', 'DALBHARAT', 'DELHIVERY', 'DIVISLAB', 'DIXON', 'DRREDDY', 'ETERNAL', 'EICHERMOT',
    'EXIDEIND', 'NYKAA', 'FORTIS', 'GAIL', 'GMRAIRPORT', 'GLENMARK', 'GODREJCP', 'GODREJPROP',
    'GRASIM', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HFCL', 'HAVELLS', 'HEROMOTOCO',
    'HINDALCO', 'HAL', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'POWERINDIA', 'HUDCO', 'ICICIBANK',
    'ICICIGI', 'ICICIPRULI', 'IDFCFIRSTB', 'IIFL', 'ITC', 'INDIANB', 'IEX', 'IOC', 'IRCTC', 'IRFC',
    'IREDA', 'INDUSTOWER', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INOXWIND', 'INDIGO', 'JINDALSTEL',
    'JSWENERGY', 'JSWSTEEL', 'JIOFIN', 'JUBLFOOD', 'KEI', 'KPITTECH', 'KALYANKJIL', 'KAYNES',
    'KFINTECH', 'KOTAKBANK', 'LTF', 'LICHSGFIN', 'LTIM', 'LT', 'LAURUSLABS', 'LICI', 'LODHA',
    'LUPIN', 'M&M', 'MANAPPURAM', 'MANKIND', 'MARICO', 'MARUTI', 'MFSL', 'MAXHEALTH', 'MAZDOCK',
    'MPHASIS', 'MCX', 'MUTHOOTFIN', 'NBCC', 'NCC', 'NHPC', 'NMDC', 'NTPC', 'NATIONALUM', 'NESTLEIND',
    'NUVAMA', 'OBEROIRLTY', 'ONGC', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PGEL', 'PIIND', 'PNBHOUSING',
    'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PIDILITIND', 'PPLPHARMA', 'POLYCAB', 'PFC',
    'POWERGRID', 'PRESTIGE', 'PNB', 'RBLBANK', 'RECLTD', 'RVNL', 'RELIANCE', 'SBICARD', 'SBILIFE',
    'SHREECEM', 'SRF', 'SAMMAANCAP', 'MOTHERSON', 'SHRIRAMFIN', 'SIEMENS', 'SOLARINDS', 'SONACOMS',
    'SBIN', 'SAIL', 'SUNPHARMA', 'SUPREMEIND', 'SUZLON', 'SYNGENE', 'TATACONSUM', 'TITAGARH',
    'TVSMOTOR', 'TCS', 'TATAELXSI', 'TMPV', 'TATAPOWER', 'TATASTEEL', 'TATATECH', 'TECHM', 'FEDERALBNK',
    'INDHOTEL', 'PHOENIXLTD', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TIINDIA', 'UNOMINDA',
    'UPL', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'IDEA', 'VOLTAS', 'WIPRO',
    'YESBANK', 'ZYDUSLIFE'
]

# Ensure GOLDBEES is included if it exists in the data (Required for Strategy 1)
# We append it to the filter list so it isn't removed during the filtering step.
filter_list = Nifty_fno + ['GOLDBEES']

# Filter the DataFrame to keep only symbols in the watchlist
if "symbol" in df.columns:
    df = df[df["symbol"].isin(filter_list)]
elif "Symbol" in df.columns:
    df = df[df["Symbol"].isin(filter_list)]
else:
    print("⚠ Warning: Could not find 'symbol' or 'Symbol' column for filtering. Skipping watchlist filter.")
# -----------------------------

# Clean
df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
df = df.dropna(subset=["Date", "Close"])
df = df.sort_values(["symbol", "Date"]).drop_duplicates(["symbol", "Date"])
df["Month"] = df["Date"].dt.to_period("M")

# Dict of first and last trading days per month
first_days = df.groupby("Month")["Date"].min().sort_values()
last_days = df.groupby("Month")["Date"].max().sort_values()

# Symbol-wise DataFrames
dfs = {symbol: g.set_index("Date").sort_index() for symbol, g in df.groupby("symbol")}

results = []

for month, signal_day in last_days.items():  # last day = signal day
    # Find lookback start month (n months ago)
    lookback_start_month = list(first_days.index)
    idx = lookback_start_month.index(month)
    if idx - (lookback_months - 1) < 0:
        continue  # not enough history
    
    start_month = lookback_start_month[idx - (lookback_months - 1)]
    start_day = first_days[start_month]

    rankings = []
    for symbol, stock_df in dfs.items():
        if start_day not in stock_df.index or signal_day not in stock_df.index:
            continue
        start_close = stock_df.loc[start_day, "Close"]
        end_close = stock_df.loc[signal_day, "Close"]
        if pd.isna(start_close) or pd.isna(end_close) or start_close == 0:
            continue
        ret = (end_close / start_close) - 1
        rankings.append((symbol, ret))

    # Pick top 5
    top_5 = sorted(rankings, key=lambda x: x[1], reverse=True)[:10]

    # Buy date = first trading day of next month
    months_list = list(first_days.index)
    if month in months_list:
        pos = months_list.index(month)
        buy_day = first_days[months_list[pos + 1]] if pos + 1 < len(months_list) else None
    else:
        buy_day = None

    for symbol, ret in top_5:
        results.append({
            "Signal_Date": signal_day.strftime("%Y-%m-%d"),
            "Buy_on": buy_day.strftime("%Y-%m-%d") if buy_day else "N/A",
            "Symbol": symbol,
            f"Return_Past{lookback_months}M(%)": round(ret * 100, 2)
        })

# Save results
final_df = pd.DataFrame(results)
output_file = f"top_10_stocks_{lookback_months}M_signals.csv"
final_df.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")
