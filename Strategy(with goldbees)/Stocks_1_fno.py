import pandas as pd
import numpy as np
import os

# -------- CONFIG ----------
INPUT_CSV = "Nifty750_tradetiger(Goldbees).csv"
OUTPUT_FILE_TEMPLATE = "top_10_stocks_{lookback}M_signals.csv"
LOOKBACK_MONTHS = 2         # change to 1, 2 or 3 (must be >= 1)
TOP_N = 10                  # how many top stocks to output per signal month
# ---------------------------

# Basic validation
if LOOKBACK_MONTHS < 1:
    raise ValueError("LOOKBACK_MONTHS must be >= 1")

# Load CSV
if not os.path.exists(INPUT_CSV):
    raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

df = pd.read_csv(INPUT_CSV, low_memory=False)

# Robust column detection and normalization
date_col = next((c for c in df.columns if c.lower() == "date"), None)
symbol_col = next((c for c in df.columns if c.lower() == "symbol"), None)
close_col = next((c for c in df.columns if c.lower() == "close"), None)

if not (date_col and symbol_col and close_col):
    raise KeyError("CSV must contain Date, Symbol and Close columns (case-insensitive).")

df.rename(columns={date_col: "Date", symbol_col: "symbol", close_col: "Close"}, inplace=True)

# Optional: Filter universe / watchlist
# If you want to apply a watchlist, define it here; otherwise comment this block.
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
# Ensure GOLDBEES present if you rely on it elsewhere
filter_list = list(set(Nifty_fno + ['GOLDBEES']))

# Apply filter only if the symbol column exists
if "symbol" in df.columns:
    df = df[df["symbol"].isin(filter_list)]
else:
    # This should not happen because we normalized, but keep safe
    print("⚠ Warning: 'symbol' column not found after normalization; skipping watchlist filter")

# Ensure Date column is datetime and drop bad rows
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "Close", "symbol"])

# Sort, dedupe
df = df.sort_values(["symbol", "Date"]).drop_duplicates(subset=["symbol", "Date"], keep="first")

# Add Month period column and compute first/last trading days per month
df["Month"] = df["Date"].dt.to_period("M")
first_days = df.groupby("Month")["Date"].min().sort_values()
last_days = df.groupby("Month")["Date"].max().sort_values()

# Convert period index to a sorted list for reliable indexing
months_list = list(first_days.index)  # PeriodIndex values, sorted

# Prepare symbol -> dataframe map
dfs = {symbol: g.set_index("Date").sort_index() for symbol, g in df.groupby("symbol")}

# RESULTS container
results = []

# Iterate over months where we have signal (we use last_days as the signal day)
for month in last_days.index:
    # index of current month within months_list
    try:
        idx = months_list.index(month)
    except ValueError:
        # shouldn't happen but skip if it does
        continue

    # compute start month index for lookback window
    # We interpret LOOKBACK_MONTHS = N as returns from start of (month - (N-1)) to end of (month)
    # Example: N=2 (past 2 months) -> start = month-1 start, end = month end (signal)
    start_idx = idx - (LOOKBACK_MONTHS - 1)
    if start_idx < 0:
        # not enough history for this lookback at this month -> skip silently
        continue

    start_month = months_list[start_idx]
    start_day = first_days[start_month]   # first trading day of start_month
    signal_day = last_days[month]         # last trading day of current month (signal)

    # compute returns for each symbol over [start_day .. signal_day]
    rankings = []
    for symbol, stock_df in dfs.items():
        # require both dates to exist in this symbol's history
        if start_day not in stock_df.index or signal_day not in stock_df.index:
            continue

        start_close = stock_df.loc[start_day, "Close"]
        end_close = stock_df.loc[signal_day, "Close"]

        if pd.isna(start_close) or pd.isna(end_close) or start_close == 0:
            continue

        ret = (end_close / start_close) - 1
        rankings.append((symbol, ret))

    if not rankings:
        # nothing to do this month
        continue

    # sort and pick top N
    top_n = sorted(rankings, key=lambda x: x[1], reverse=True)[:TOP_N]

    # Buy date is first trading day of NEXT month (if exists)
    if idx + 1 < len(months_list):
        next_month = months_list[idx + 1]
        buy_day = first_days[next_month]
        buy_day_str = buy_day.strftime("%Y-%m-%d")
    else:
        buy_day = None
        buy_day_str = "N/A"

    # append results - include safe formatting
    for symbol, ret in top_n:
        results.append({
            "Signal_Month": str(month),
            "Signal_Date": signal_day.strftime("%Y-%m-%d"),
            "Lookback_Start_Month": str(start_month),
            "Lookback_Start_Date": start_day.strftime("%Y-%m-%d"),
            "Buy_on": buy_day_str,
            "Symbol": symbol,
            f"Return_Past{LOOKBACK_MONTHS}M(%)": round(ret * 100, 2)
        })

# Save results
output_file = OUTPUT_FILE_TEMPLATE.format(lookback=LOOKBACK_MONTHS)
final_df = pd.DataFrame(results)
final_df.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")
