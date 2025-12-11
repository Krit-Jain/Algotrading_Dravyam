# 📈 Past N Months Gainer Based Strategy  
### Algorithmic Trading Framework for Dravyam

A modular, research-driven algorithmic trading framework developed for **Dravyam**, focused on multi-factor momentum, seasonal patterns, and hybrid signal-generation/backtesting engines across NSE universes (**Nifty 750** & **FnO**).

This repository contains two categories of systems:

- **STOCKS files → Signal Generators**  
- **STRATEGY files → Full Backtesting Engines**

Both Strategy-1 and Strategy-2 use the same hybrid core (Seasonal + Momentum) but differ in *gainer selection logic*, *return window mechanics*, and *holding-period behavior*.

---

## 📂 Repository Structure

Use this tree as a reference for the repo layout:

    Algotrading_Dravyam/
    │
    ├── Strategy(with goldbees)/
    │   ├── Stocks_1_Nifty750.py
    │   ├── Stocks_1_fno.py
    │   ├── Stocks_2_Nifty750.py
    │   ├── Stocks_2_fno.py
    │   ├── Strategy_1_Nifty750.py
    │   ├── Strategy_1_fno.py
    │   ├── Strategy_2_Nifty750.py
    │   ├── Strategy_2_fno.py
    │
    ├── Nifty750_tradetiger(Goldbees).csv
    │
    └── README.md

---

## 🧠 Core Strategy Philosophy

All strategies follow these principles:

- **Hybrid Model** → Seasonal logic + Momentum logic  
- **Return Window (fixed):**

    Start = Beginning of month (M - 3)  
    End   = End of month       (M - 2)

- **Buy Day** = First trading day of month M  
- **Sell Day** = End of month (M + holding_period - 1)  
- **Flexible Holding Period** → 1M / 2M / 3M  
- **Rank Buckets** → e.g., 0–5, 5–10, 10–15  
- **Filtered Universe**
  - Close > 25  
  - Excluded symbols removed  
- **Strategy-1 and Strategy-2 differ only in how they pick gainers**

---

## 🔥 Differences Between Strategy-1 and Strategy-2

| Feature | Strategy-1 | Strategy-2 |
|--------|------------|------------|
| Seasonal Component | Yes | Yes |
| Momentum Window | Past N-Month Returns (M-3 → M-2) | Same window but different ranking filters |
| Holding Period | Flexible (1/2/3 months) | Flexible (1/2/3 months) |
| Gainer Selection | Hybrid seasonal + momentum | Alternate gainer ranking approach |
| Universe | Nifty750 & FnO variants | Nifty750 & FnO variants |

---

## ⚫ Excluded Symbols (Momentum Universe)

To avoid abnormal/penny-stock distortions the following symbols are excluded from the momentum-ranking universe:

- BOMDYEING  
- PATANJALI  
- ALOKINDS  
- ORCHPHARMA  
- GOLDBEES  (GOLDBEES is retained only for the Jan–Mar seasonal trade in Strategy files)

---

## ⚙️ Installation

Install Python dependencies:

```bash
pip install pandas numpy matplotlib
```
If you plan to visualize equity curves, matplotlib is useful (already included above).

---

## 🚀 Running STOCKS Signal Generators

STOCKS scripts generate monthly TOP N stock signals (they do NOT perform backtests). Example:

```bash
python Stocks_1_Nifty750.py
```
This will create a file like:
```
top_10_stocks_2M_signals.csv
```
Each row contains:

- Signal_Month
- Signal_Date
- Lookback_Start_Month
- Lookback_Start_Date
- Buy_on (first trading day of next month)
- Symbol
- Return_Past2M(%) (or similar label)

---

## 🧪 Running STRATEGY Backtests

To run a full backtest (seasonal + momentum + metrics), run:

```bash
python Strategy_1_Nifty750.py
```
The backtester will:
- Run GOLD BEES seasonal trade (Jan → Mar) where applicable
- Run the Strategy-3 momentum engine (M-3 → M-2 window) across valid months
- Run December special logic where implemented
- Compute and save metrics: Final capital, CAGR, Sharpe, Max Drawdown
- Export trade logs and results under the **Results(YYYY-YYYY)** directory

Example output file:
```bash
Results(2016-2025)/results_hybrid_rank0_5_tradetiger.csv
```

---

## 📊 Backtest Metrics Provided
Each STRATEGY run produces:

- Entry/Exit Dates
- Symbol
- Buy/Sell Price
- Shares
- PnL
- Past Return (%) used for ranking
- Final Capital
- CAGR (%)
- Max Drawdown (%)
- Sharpe Ratio

---

## 🧱 System Architecture
Simple flow (ASCII diagram):
```
Raw CSV (NSE data)
      │
      ▼
Data Cleaning (normalize, dedupe)
      │
      ▼
Monthly Calendar Builder (first/last trading days)
      │
      ▼
Strategy Engine (Seasonal + Momentum)
      │
 ┌────┴────┐
 │         │
STOCKS   STRATEGY
(Signals) (Backtests + Metrics)
      │
      ▼
CSV Outputs (signals & results)
```

---

## ⚙️ Output Files & Locations
- Signal CSVs (from STOCKS scripts): top_10_stocks_2M_signals.csv (or similar naming based on LOOKBACK_MONTHS)
- Backtest results (from STRATEGY scripts): Results(YYYY-YYYY)/results_hybrid_rank<start>_<end>_tradetiger.csv
- Trade logs: saved alongside backtest results as CSVs (same folder)

---

## 🚫 Filtering & Exclusions (Important)
-Minimum price filter: Close > 25 (configurable in code)
-Excluded symbols (removed from momentum ranking):
 - BOMDYEING
 - PATANJALI
 - ALOKINDS
 - ORCHPHARMA
 - GOLDBEES (excluded from momentum universe but used for seasonal trade)

## ✅ Best Practices & Tips
- Ensure Nifty750_tradetiger(Goldbees).csv is placed in the repository root before running scripts.
- Use a dedicated Python virtual environment to isolate dependencies.
- Verify Date, symbol, and Close columns exist and are normalized — the scripts try to auto-detect differing cases but consistent headers help.
- Start with holding_period = 1 for sanity checks, then test 2 and 3. The backtest engine supports flexible holding; ensure sell-month indices exist for larger holding periods.
- If you want signals for very early months (dataset start), convert to the flexible mode (nearest-available-date fallback) — modify the helper in the STOCKS script.

## 📬 Contact  
This framework is part of Dravyam’s quantitative research initiative.  
Feel free to open issues or request enhancements.

## 📘 License  
Internal research project for Dravyam.
