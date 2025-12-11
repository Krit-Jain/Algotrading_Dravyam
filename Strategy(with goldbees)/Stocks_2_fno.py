
"""
STOCKS signal generator (STRICT Strategy-3 applied to all months).

Rule:
  For each signal month M, ranking window = Start(M-3) -> End(M-2).
  Emit a signal only if full window exists (strict).
  Ranking excludes certain stocks and uses Close > 25 filter.
Output:
  CSV with columns:
    Signal_Month, Signal_Date, Lookback_Start_Month, Lookback_Start_Date,
    Buy_on, Symbol, Return_Past2M(%)
"""

import os
import pandas as pd
import numpy as np

# -------- USER CONFIG ----------
INPUT_CSV = "Nifty750_tradetiger(Goldbees).csv"
OUTPUT_FILE_TEMPLATE = "top_10_stocks_{lookback}M_signals.csv"
LOOKBACK_MONTHS = 2   # used for file name and return label (strategy uses 2-month window strictly)
TOP_N = 10            # how many top stocks to output per signal month
MIN_PRICE = 25        # Close > MIN_PRICE filter for universe
# Exclusions (kept out of ranking)
EXCLUDED_STOCKS = {"BOMDYEING", "PATANJALI", "ALOKINDS", "ORCHPHARMA", "GOLDBEES"}
# -------------------------------

# Basic validation
if LOOKBACK_MONTHS != 2:
    # Strategy-3 is defined as a "past 2 completed months" window; we enforce LOOKBACK_MONTHS=2 for naming consistency.
    print("⚠ NOTE: Strategy-3 uses a fixed 2-month return window. LOOKBACK_MONTHS variable is used only for filename/label.")
if not os.path.exists(INPUT_CSV):
    raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

# Load CSV
df = pd.read_csv(INPUT_CSV, low_memory=False)

# Robust column detection & normalization
date_col = next((c for c in df.columns if c.lower() == "date"), None)
symbol_col = next((c for c in df.columns if c.lower() == "symbol"), None)
close_col = next((c for c in df.columns if c.lower() == "close"), None)

if not (date_col and symbol_col and close_col):
    raise KeyError("CSV must contain Date, Symbol and Close columns (case-insensitive).")

df.rename(columns={date_col: "Date", symbol_col: "symbol", close_col: "Close"}, inplace=True)

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
filter_list = list(set(Nifty_fno))

# Apply filter only if the symbol column exists
if "symbol" in df.columns:
    df = df[df["symbol"].isin(filter_list)]
else:
    # This should not happen because we normalized, but keep safe
    print("⚠ Warning: 'symbol' column not found after normalization; skipping watchlist filter")

# Ensure Date is datetime and drop bad rows
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "Close", "symbol"])
df = df.sort_values(["symbol", "Date"]).drop_duplicates(subset=["symbol", "Date"], keep="first")

# MONTH markers
df["Month"] = df["Date"].dt.to_period("M")
first_days = df.groupby("Month")["Date"].min().sort_values()   # first trading day each month
last_days = df.groupby("Month")["Date"].max().sort_values()    # last trading day each month

# Ordered months list (Period objects)
months_list = list(first_days.index)

# maps for quick access
month_to_first = {m: first_days[m] for m in first_days.index}
month_to_last = {m: last_days[m] for m in last_days.index}

# Prepare per-symbol DataFrames
# dfs_full contains all symbols (for potential lookups); dfs is filtered universe for ranking
dfs_full = {s: g.set_index("Date").sort_index() for s, g in df.groupby("symbol")}
df_filtered = df[df["Close"] > MIN_PRICE].copy()
dfs = {s: g.set_index("Date").sort_index() for s, g in df_filtered.groupby("symbol")}

# Remove excluded stocks from ranking universe
for ex in list(EXCLUDED_STOCKS):
    if ex in dfs:
        del dfs[ex]

# Helper: nearest earlier date lookup (we won't use it for strictness; kept for safety per-ticker)
def get_nearest_available_date(stock_df, target_date):
    """
    Return the target_date if present in index; otherwise nearest earlier index date.
    For strict monthly logic we will require exact month boundary dates; still using this helper if needed.
    """
    if target_date in stock_df.index:
        return target_date
    pos = stock_df.index.searchsorted(target_date)
    if pos == 0:
        return None
    return stock_df.index[pos - 1]

# RESULTS container
results = []

# Iterate through months (use months present in last_days as signal months)
for idx, month in enumerate(months_list):
    # signal day = last trading day of month (must exist in month_to_last)
    if month not in month_to_last:
        continue
    signal_day = month_to_last[month]

    # Strict Strategy-3 window: rs_idx = idx - 3  (M-3 start) ; re_idx = idx - 2 (M-2 end)
    rs_idx = idx - 3
    re_idx = idx - 2

    # Ensure full window exists in the months_list
    if rs_idx < 0 or re_idx < 0 or rs_idx >= len(months_list) or re_idx >= len(months_list):
        # Not enough history; skip this month (strict requirement)
        continue

    start_month = months_list[rs_idx]
    end_month = months_list[re_idx]
    start_day = month_to_first[start_month]   # first trading day of start_month
    end_day = month_to_last[end_month]        # last trading day of end_month

    # Build rankings using exact boundary dates (strict)
    rankings = []
    for symbol, stock_df in dfs.items():
        # require both exact dates in symbol history
        if (start_day not in stock_df.index) or (end_day not in stock_df.index):
            continue
        s0 = stock_df.loc[start_day, "Close"]
        s1 = stock_df.loc[end_day, "Close"]
        if pd.isna(s0) or pd.isna(s1) or s0 == 0:
            continue
        ret = (s1 / s0) - 1
        rankings.append((symbol, ret))

    if not rankings:
        # no eligible tickers for this month after filters
        continue

    # select top N
    top_n = sorted(rankings, key=lambda x: x[1], reverse=True)[:TOP_N]

    # Buy date = first trading day of NEXT month (if exists)
    if idx + 1 < len(months_list):
        next_month = months_list[idx + 1]
        buy_day = month_to_first.get(next_month, None)
        buy_day_str = buy_day.strftime("%Y-%m-%d") if buy_day is not None else "N/A"
    else:
        buy_day_str = "N/A"

    # Append results using the original-style field names
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

# Save output (same filename pattern as original)
output_file = OUTPUT_FILE_TEMPLATE.format(lookback=LOOKBACK_MONTHS)
final_df = pd.DataFrame(results)

final_df.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")
print(f"Signals generated for {final_df['Signal_Month'].nunique()} months, {len(final_df)} rows total.")
