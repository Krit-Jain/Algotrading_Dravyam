# --- Unified Return Logic for Consistent Stock Ranking ---

import pandas as pd
import numpy as np
from datetime import date
import matplotlib.pyplot as plt
# from jugaad_data.nse import stock_df # Not used in the provided script, can be removed
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

# --- DATA PREPARATION ---

# Read and clean the CSV
# Make sure your CSV file is in the same directory as this script
try:
    df = pd.read_csv("Nifty750_tradetiger.csv", low_memory=False)
except FileNotFoundError:
    print("❌ Error: 'Nifty750_tradetiger.csv' not found. Please place it in the correct directory.")
    exit()


# # Rename columns for consistency
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

# Map old symbols to new ones for data consistency
# symbol_map = {
#     "IIFLWAM": "360ONE",
#     "TWL": "TITAGARH",
#     "RUCHI": "PATANJALI",
#     "TIPSINDLTD": "TIPSMUSIC",
#     "IBVENTURES": "DHANI",
#     "MFL": "EPIGRAL",
#     "ZOMATO": "ETERNAL",
#     "LSIL": "LLOYDSENGG",
#     "TRIL": "TARIL",
#     "MAGMA": "POONAWALLA"
# }
# df["Symbol"] = df["Symbol"].replace(symbol_map)

df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
df = df.dropna(subset=["Close", "Date"]) # Drop rows where essential data is missing

# Sort and deduplicate to ensure data integrity
df = df.sort_values(["symbol", "Date"])
df = df.drop_duplicates(subset=["symbol", "Date"], keep="first")

# Group by symbol for quick lookups
dfs = {s: g.set_index("Date").sort_index() for s, g in df.groupby("symbol")}

# This ensures GOLDBEES data is available later, even after it's filtered out for momentum trades.
dfs_full = dfs.copy()


# --- STOCK FILTERING ---
# GOLDBEES is added here to exclude it from the momentum part of the strategy.
excluded_stocks = ["BOMDYEING", "PATANJALI", "ALOKINDS", "ORCHPHARMA", "GOLDBEES"]

for symbol in list(dfs.keys()):
    if symbol in excluded_stocks:
        if symbol in dfs: # Check if it exists before deleting
            del dfs[symbol]
        continue

    df_symbol = dfs[symbol]
    df_symbol = df_symbol[df_symbol["Close"] > 25] # Only keep stocks with Close > ₹25

    if df_symbol.empty:
        del dfs[symbol]
    else:
        dfs[symbol] = df_symbol

# --- DATE & PERIOD SETUP ---
df_dates_only = df.set_index('Date')
month_markers = df_dates_only.index.to_period("M").unique()
first_days = df.groupby(df['Date'].dt.to_period("M"))["Date"].min()
last_days = df.groupby(df['Date'].dt.to_period("M"))["Date"].max()

time_range_mask = (first_days.index >= "2020-01") & (last_days.index <= "2025-11")
month_starts = list(first_days[time_range_mask].sort_values())
month_ends = list(last_days[time_range_mask].sort_values())


# --- BACKTESTING PARAMETERS ---
month_lookback = 2
holding_period = 2
results = []


# --- MAIN BACKTESTING LOOP ---
print("🚀 Starting Hybrid Strategy Backtest...")

for rank_start in range(0, 10, 5):
    rank_end = rank_start + 5
    capital = 1000000
    initial_capital = capital
    equity_curve = []
    trade_log = []

    i = month_lookback
    while i < len(month_starts):
        buy_day = month_starts[i]
        
        # --- NEW STRATEGY LOGIC ---

        # Strategy 1: GOLDBEES trade from January to March (3 months)
        if buy_day.month == 1:
            if i + 3 < len(month_ends):
                sell_day = month_ends[i + 2] # Sell at the end of March
                goldbees_df = dfs_full.get("GOLDBEES")
                if goldbees_df is not None and buy_day in goldbees_df.index and sell_day in goldbees_df.index:
                    buy_price = goldbees_df.loc[buy_day, "Close"]
                    sell_price = goldbees_df.loc[sell_day, "Close"]
                    if pd.notna(buy_price) and pd.notna(sell_price) and buy_price > 0:
                        shares = capital // buy_price
                        pnl = shares * (sell_price - buy_price)
                        capital += pnl
                        trade_log.append({
                            "Entry_Date": buy_day.date(), "Exit_Date": sell_day.date(), "Symbol": "GOLDBEES", 
                            "Buy_Price": round(buy_price, 2), "Sell_Price": round(sell_price, 2), 
                            "Shares": int(shares), "PnL": round(pnl, 2), "Return_2M(%)": "N/A (Seasonal)"
                        })
                        equity_curve.append({"Date": sell_day.date(), "Capital": round(capital, 2)})
            i += 3 # Jump 3 months to April
            continue

        # Strategy 2: Special 1-month momentum trade in December
        if buy_day.month == 12:
            if i < len(month_ends):
                sell_day = month_ends[i] # Sell at the end of December
                return_start_day = month_starts[i - month_lookback]
                return_end_day = month_ends[i - 1]
                # --- (This is the momentum trade logic, adapted for 1 month) ---
                rankings = []
                for symbol, stock_df in dfs.items():
                    required_dates = [buy_day, sell_day, return_start_day, return_end_day]
                    if not all(date in stock_df.index for date in required_dates): continue
                    start_price, end_price = stock_df.loc[return_start_day, "Close"], stock_df.loc[return_end_day, "Close"]
                    buy_price, sell_price = stock_df.loc[buy_day, "Close"], stock_df.loc[sell_day, "Close"]
                    if any(pd.isna([start_price, end_price, buy_price, sell_price])) or start_price == 0: continue
                    past_return = (end_price / start_price) - 1
                    rankings.append((symbol, past_return, buy_price, sell_price))
                if rankings:
                    top_n = sorted(rankings, key=lambda x: x[1], reverse=True)[rank_start:rank_end]
                    allocation = capital / len(top_n) if top_n else 0
                    pnl_month = 0
                    for symbol, past_return, buy_price, sell_price in top_n:
                        shares = allocation // buy_price
                        pnl = shares * (sell_price - buy_price)
                        pnl_month += pnl
                        trade_log.append({
                            "Entry_Date": buy_day.date(), "Exit_Date": sell_day.date(), "Symbol": symbol, 
                            "Buy_Price": round(buy_price, 2), "Sell_Price": round(sell_price, 2), 
                            "Shares": int(shares), "PnL": round(pnl, 2), "Return_2M(%)": round(past_return * 100, 2)
                        })
                    capital += pnl_month
                    equity_curve.append({"Date": sell_day.date(), "Capital": round(capital, 2)})
            i += 1 # Move 1 month to January
            continue

        # Strategy 3: Standard 2-month momentum trades (Buy months: April - October)
        if buy_day.month in [4, 5, 6, 7, 8, 9, 10] and i + holding_period < len(month_ends):
            sell_day = month_ends[i + holding_period - 1]
            return_start_day = month_starts[i - month_lookback]
            return_end_day = month_ends[i - 1]
            # --- (This is the standard momentum trade logic) ---
            rankings = []
            for symbol, stock_df in dfs.items():
                required_dates = [buy_day, sell_day, return_start_day, return_end_day]
                if not all(date in stock_df.index for date in required_dates): continue
                start_price, end_price = stock_df.loc[return_start_day, "Close"], stock_df.loc[return_end_day, "Close"]
                buy_price, sell_price = stock_df.loc[buy_day, "Close"], stock_df.loc[sell_day, "Close"]
                if any(pd.isna([start_price, end_price, buy_price, sell_price])) or start_price == 0: continue
                past_return = (end_price / start_price) - 1
                rankings.append((symbol, past_return, buy_price, sell_price))
            if rankings:
                top_n = sorted(rankings, key=lambda x: x[1], reverse=True)[rank_start:rank_end]
                allocation = capital / len(top_n) if top_n else 0
                pnl_month = 0
                for symbol, past_return, buy_price, sell_price in top_n:
                    shares = allocation // buy_price
                    pnl = shares * (sell_price - buy_price)
                    pnl_month += pnl
                    trade_log.append({
                        "Entry_Date": buy_day.date(), "Exit_Date": sell_day.date(), "Symbol": symbol, 
                        "Buy_Price": round(buy_price, 2), "Sell_Price": round(sell_price, 2), 
                        "Shares": int(shares), "PnL": round(pnl, 2), "Return_2M(%)": round(past_return * 100, 2)
                    })
                capital += pnl_month
                equity_curve.append({"Date": sell_day.date(), "Capital": round(capital, 2)})
            i += holding_period # Jump 2 months
        else:
            i += 1 # Skip other months (Feb, Mar, Nov)

    # --- PERFORMANCE CALCULATION ---
    if not equity_curve:
        print(f"⚠️ No trades were executed for Rank={rank_start}-{rank_end}. Skipping.")
        continue
        
    equity_df = pd.DataFrame(equity_curve)
    equity_df["Date"] = pd.to_datetime(equity_df["Date"])
    
    trades_df = pd.DataFrame(trade_log) if trade_log else pd.DataFrame()

    # Create the final merged DataFrame by joining trades with the equity curve
    if not trades_df.empty:
        trades_df['Exit_Date'] = pd.to_datetime(trades_df['Exit_Date'])
        final_df = pd.merge(trades_df, equity_df, left_on="Exit_Date", right_on="Date", how="left")
        final_df.drop(columns=["Date"], inplace=True) # Drop redundant date column
    else:
        final_df = pd.DataFrame()

    equity_df.set_index("Date", inplace=True)
    
    cumulative_return = (capital / initial_capital - 1) * 100
    returns = equity_df["Capital"].pct_change().dropna()
    std_dev = returns.std()
    sharpe = (returns.mean() / std_dev) * np.sqrt(6) if std_dev != 0 else 0 
    cagr = ((capital / initial_capital) ** (1 / ((equity_df.index[-1] - equity_df.index[0]).days / 365.25)) - 1) * 100
    running_max = equity_df["Capital"].cummax()
    drawdown = (equity_df["Capital"] - running_max) / running_max
    max_drawdown = drawdown.min() * 100
    
    # Add all metrics to the final merged DataFrame
    if not final_df.empty:
        final_df["Rank_Start"] = rank_start
        final_df["Rank_End"] = rank_end
        final_df["Initial_Capital"] = initial_capital
        final_df["Final_Capital"] = round(capital, 2)
        final_df["Cumulative_Return_%"] = round(cumulative_return, 2)
        final_df["CAGR_%"] = round(cagr, 2)
        final_df["Max_Drawdown_%"] = round(max_drawdown, 2)
        final_df["Sharpe_Ratio"] = round(sharpe, 2)
        
        filename = f"results_hybrid_rank{rank_start}_{rank_end}_tradetiger.csv"
        final_df.to_csv(filename, index=False)

    print(f"✅ Completed: Rank={rank_start}-{rank_end}, Final Capital=₹{capital:.2f}, CAGR={cagr:.2f}%, Max DD={max_drawdown:.2f}%")
    results.append((holding_period, rank_start, rank_end, capital))


if results:
    best = max(results, key=lambda x: x[3])
    print(f"\n📈 Best Strategy: Holding={best[0]}M, Rank={best[1]}–{best[2]}, Final Capital=₹{round(best[3],2)}")
else:
    print("\nNo results were generated from the backtest.")

