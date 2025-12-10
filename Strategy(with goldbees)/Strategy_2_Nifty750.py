# --- Unified Return Logic for Consistent Stock Ranking ---
import os
from datetime import date

import numpy as np
import pandas as pd

# --- CONFIG ---
INPUT_CSV = "Nifty750_tradetiger(Goldbees).csv"
OUTPUT_FOLDER = "Results(2016-2025)"

month_lookback = 2
holding_period = 1  # change to 1, 2, or 3 as desired (April->Nov block is flexible)
results = []

# --- DATA PREPARATION ---
try:
    df = pd.read_csv(INPUT_CSV, low_memory=False)
except FileNotFoundError:
    print(f"❌ Error: '{INPUT_CSV}' not found. Please place it in the correct directory.")
    raise SystemExit(1)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Robustly find key columns (handles different CSV column casing / naming)
date_col = next((c for c in df.columns if c.lower() == "date"), None)
symbol_col = next((c for c in df.columns if c.lower() == "symbol"), None)
close_col = next((c for c in df.columns if c.lower() == "close"), None)

if not (date_col and symbol_col and close_col):
    raise KeyError("CSV must contain columns for Date, Symbol and Close (case-insensitive).")

# normalize names to expected ones used in code
df.rename(columns={date_col: "Date", symbol_col: "symbol", close_col: "Close"}, inplace=True)

# ensure datetime and required data present
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "Close"])
df = df.sort_values(["symbol", "Date"])
df = df.drop_duplicates(subset=["symbol", "Date"], keep="first")

# Group by symbol into individual DataFrames
dfs = {s: g.set_index("Date").sort_index() for s, g in df.groupby("symbol")}

# keep a separate dictionary with full data (so filtering doesn't remove GOLDBEES from original)
dfs_full = {k: v.copy() for k, v in dfs.items()}

# --- STOCK FILTERING ---
excluded_stocks = ["BOMDYEING", "PATANJALI", "ALOKINDS", "ORCHPHARMA", "GOLDBEES"]

for symbol in list(dfs.keys()):
    if symbol in excluded_stocks:
        # Remove from the momentum universe but keep in dfs_full
        if symbol in dfs:
            del dfs[symbol]
        continue

    df_symbol = dfs[symbol]
    df_symbol = df_symbol[df_symbol["Close"] > 25]  # keep only Close > ₹25

    if df_symbol.empty:
        del dfs[symbol]
    else:
        dfs[symbol] = df_symbol

# --- DATE & PERIOD SETUP ---
df_dates_only = df.set_index("Date")
first_days = df.groupby(df["Date"].dt.to_period("M"))["Date"].min()
last_days = df.groupby(df["Date"].dt.to_period("M"))["Date"].max()

time_range_mask = (first_days.index >= "2016-01") & (last_days.index <= "2025-11")
month_starts = list(first_days[time_range_mask].sort_values())
month_ends = list(last_days[time_range_mask].sort_values())

if not month_starts or not month_ends:
    raise SystemExit("No valid months found in the specified time range. Check your CSV and time_range_mask.")

# --- MAIN BACKTESTING LOOP ---
print("🚀 Starting Hybrid Strategy Backtest...")

for rank_start in range(0, 50, 5):
    rank_end = rank_start + 5
    capital = 1_000_000.0
    initial_capital = capital
    equity_curve = []
    trade_log = []

    i = month_lookback  # start index (so we have enough history for lookback)
    while i < len(month_starts):
        buy_day = month_starts[i]

        # ------------------------
        # Strategy 1: GOLDBEES (Jan -> Mar, fixed 3-month seasonal)
        # ------------------------
        if buy_day.month == 1:
            # Need i + 2 to exist (sell at end of March => i + 2)
            if i + 2 < len(month_ends):
                sell_day = month_ends[i + 2]  # end of March
                goldbees_df = dfs_full.get("GOLDBEES")
                if (
                    goldbees_df is not None
                    and buy_day in goldbees_df.index
                    and sell_day in goldbees_df.index
                ):
                    buy_price = goldbees_df.loc[buy_day, "Close"]
                    sell_price = goldbees_df.loc[sell_day, "Close"]
                    if pd.notna(buy_price) and pd.notna(sell_price) and buy_price > 0:
                        shares = capital // buy_price
                        pnl = shares * (sell_price - buy_price)
                        capital += pnl
                        trade_log.append(
                            {
                                "Entry_Date": buy_day.date(),
                                "Exit_Date": sell_day.date(),
                                "Symbol": "GOLDBEES",
                                "Buy_Price": round(buy_price, 2),
                                "Sell_Price": round(sell_price, 2),
                                "Shares": int(shares),
                                "PnL": round(pnl, 2),
                                "Return_2M(%)": "N/A (Seasonal)",
                            }
                        )
                        equity_curve.append({"Date": sell_day.date(), "Capital": round(capital, 2)})
            i += 3  # jump to April
            continue

        # ------------------------
        # Strategy 2: December 1-month special (fixed)
        # ------------------------
        if buy_day.month == 12:
            if i < len(month_ends):
                sell_day = month_ends[i]  # end of December

                # Compute return window safely: (M-3 start -> M-2 end)
                rs_idx = i - (month_lookback + 1)
                re_idx = i - 2
                if rs_idx < 0 or re_idx < 0 or rs_idx >= len(month_starts) or re_idx >= len(month_ends):
                    i += 1
                    continue

                return_start_day = month_starts[rs_idx]
                return_end_day = month_ends[re_idx]

                # Momentum ranking for December (1-month hold)
                rankings = []
                for symbol, stock_df in dfs.items():
                    required_dates = [return_start_day, return_end_day, buy_day, sell_day]
                    if not all(d in stock_df.index for d in required_dates):
                        continue

                    start_price = stock_df.loc[return_start_day, "Close"]
                    end_price = stock_df.loc[return_end_day, "Close"]
                    buy_price = stock_df.loc[buy_day, "Close"]
                    sell_price = stock_df.loc[sell_day, "Close"]

                    if any(pd.isna([start_price, end_price, buy_price, sell_price])) or start_price == 0:
                        continue

                    past_return = (end_price / start_price) - 1
                    rankings.append((symbol, past_return, buy_price, sell_price))

                if rankings:
                    top_n = sorted(rankings, key=lambda x: x[1], reverse=True)[rank_start:rank_end]
                    if top_n:
                        allocation = capital / len(top_n)
                        pnl_month = 0
                        for symbol, past_return, buy_price, sell_price in top_n:
                            shares = allocation // buy_price if buy_price > 0 else 0
                            pnl = shares * (sell_price - buy_price)
                            pnl_month += pnl
                            trade_log.append(
                                {
                                    "Entry_Date": buy_day.date(),
                                    "Exit_Date": sell_day.date(),
                                    "Symbol": symbol,
                                    "Buy_Price": round(buy_price, 2),
                                    "Sell_Price": round(sell_price, 2),
                                    "Shares": int(shares),
                                    "PnL": round(pnl, 2),
                                    "Return_2M(%)": round(past_return * 100, 2),
                                }
                            )
                        capital += pnl_month
                        equity_curve.append({"Date": sell_day.date(), "Capital": round(capital, 2)})

            i += 1  # move to next month (Jan)
            continue

        # ------------------------
        # Strategy 3: Flexible Momentum Strategy (April -> November)
        # ------------------------
        if buy_day.month in [4, 5, 6, 7, 8, 9, 10, 11]:
            # Return window always fixed: M-3 start -> M-2 end
            rs_idx = i - (month_lookback + 1)  # i - 3 when lookback=2
            re_idx = i - 2

            if rs_idx < 0 or re_idx < 0 or rs_idx >= len(month_starts) or re_idx >= len(month_ends):
                i += 1
                continue

            return_start_day = month_starts[rs_idx]
            return_end_day = month_ends[re_idx]

            # Sell day based on holding_period (flexible)
            sell_idx = i + holding_period - 1
            if sell_idx >= len(month_ends):
                i += 1
                continue
            sell_day = month_ends[sell_idx]

            # Optional DEBUG print to verify windows:
            # print(f"[DEBUG] Buy {buy_day.date()} window {return_start_day.date()} -> {return_end_day.date()} sell {sell_day.date()}")

            # Momentum ranking
            rankings = []
            for symbol, stock_df in dfs.items():
                required_dates = [return_start_day, return_end_day, buy_day, sell_day]
                if not all(d in stock_df.index for d in required_dates):
                    continue

                start_price = stock_df.loc[return_start_day, "Close"]
                end_price = stock_df.loc[return_end_day, "Close"]
                buy_price = stock_df.loc[buy_day, "Close"]
                sell_price = stock_df.loc[sell_day, "Close"]

                if any(pd.isna([start_price, end_price, buy_price, sell_price])):
                    continue
                if start_price <= 0:
                    continue

                past_return = (end_price / start_price) - 1
                rankings.append((symbol, past_return, buy_price, sell_price))

            if not rankings:
                i += 1
                continue

            top_n = sorted(rankings, key=lambda x: x[1], reverse=True)[rank_start:rank_end]
            if not top_n:
                i += 1
                continue

            allocation = capital / len(top_n) if len(top_n) > 0 else 0
            pnl_month = 0
            for symbol, past_return, buy_price, sell_price in top_n:
                shares = allocation // buy_price if buy_price > 0 else 0
                pnl = shares * (sell_price - buy_price)
                pnl_month += pnl
                trade_log.append(
                    {
                        "Entry_Date": buy_day.date(),
                        "Exit_Date": sell_day.date(),
                        "Symbol": symbol,
                        "Buy_Price": round(buy_price, 2),
                        "Sell_Price": round(sell_price, 2),
                        "Shares": int(shares),
                        "PnL": round(pnl, 2),
                        "Return_2M(%)": round(past_return * 100, 2),
                    }
                )

            capital += pnl_month
            equity_curve.append({"Date": sell_day.date(), "Capital": round(capital, 2)})

            # Move forward by holding_period months for the April->Nov engine
            i += holding_period
            continue

        # If month doesn't match any strategy, move forward
        i += 1

    # --- PERFORMANCE CALCULATION ---
    if not equity_curve:
        print(f"⚠ No trades were executed for Rank={rank_start}-{rank_end}. Skipping.")
        continue

    equity_df = pd.DataFrame(equity_curve)
    equity_df["Date"] = pd.to_datetime(equity_df["Date"])
    trades_df = pd.DataFrame(trade_log) if trade_log else pd.DataFrame()

    if not trades_df.empty:
        trades_df["Exit_Date"] = pd.to_datetime(trades_df["Exit_Date"])
        final_df = pd.merge(trades_df, equity_df, left_on="Exit_Date", right_on="Date", how="left")
        final_df.drop(columns=["Date"], inplace=True)
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

    if not final_df.empty:
        final_df["Rank_Start"] = rank_start
        final_df["Rank_End"] = rank_end
        final_df["Initial_Capital"] = initial_capital
        final_df["Final_Capital"] = round(capital, 2)
        final_df["Cumulative_Return_%"] = round(cumulative_return, 2)
        final_df["CAGR_%"] = round(cagr, 2)
        final_df["Max_Drawdown_%"] = round(max_drawdown, 2)
        final_df["Sharpe_Ratio"] = round(sharpe, 2)

        filename = os.path.join(OUTPUT_FOLDER, f"results_hybrid_rank{rank_start}_{rank_end}_tradetiger.csv")
        final_df.to_csv(filename, index=False)

    print(f"✅ Completed: Rank={rank_start}-{rank_end}, Final Capital=₹{capital:.2f}, CAGR={cagr:.2f}%, Max DD={max_drawdown:.2f}%")
    results.append((holding_period, rank_start, rank_end, capital))

# Summary best
if results:
    best = max(results, key=lambda x: x[3])
    print(f"\n📈 Best Strategy: Holding={best[0]}M, Rank={best[1]}–{best[2]}, Final Capital=₹{round(best[3],2)}")
else:
    print("\nNo results were generated from the backtest.")
