# 📈 Past N Months Gainer Based Strategy  
### **Algorithmic Trading Framework for Dravyam**  
A modular, research-driven algorithmic trading framework developed for **Dravyam**, focused on multi-factor momentum, seasonal patterns, and hybrid signal-generation/backtesting systems across NSE universes (**Nifty 750** & **FnO**).

This repository contains **two categories of systems**:

## **1. STOCKS Files → Signal Generators**
Generate **monthly stock picks** based on configurable lookback windows.  
These scripts do **NOT** execute trades — they only output signals.

## **2. STRATEGY Files → Full Backtesting Engines**
Run complete simulations with capital, PnL, holding-period logic, seasonal models, and equity curves.

---

# 🧠 **Core Framework Philosophy**
Both Strategy-1 and Strategy-2 follow a **hybrid model** consisting of:

- ✅ **Seasonal Components** (e.g., GOLD BEES Jan–Mar seasonal behavior)  
- ✅ **Momentum Components** (top gainers using return windows)  
- ✅ **Flexible Holding-Period Engine** (1M / 2M / 3M)  
- ✅ **Different Gainer Selection Logic** (Strategy-1 vs Strategy-2)

The strategies share the same architecture but differ in **how gainers are selected** and **which months they are applied to**.

---

# 📂 **Repository Structure**
Algotrading_Dravyam/
│
├── Strategy(with goldbees)/
│ ├── Stocks_1_Nifty750.py
│ ├── Stocks_1_fno.py
│ ├── Stocks_2_Nifty750.py
│ ├── Stocks_2_fno.py
│ ├── Strategy_1_Nifty750.py
│ ├── Strategy_1_fno.py
│ ├── Strategy_2_Nifty750.py
│ ├── Strategy_2_fno.py
│
├── Nifty750_tradetiger(Goldbees).csv
└── README.md

---

# 🔍 **How Strategy 1 & Strategy 2 Differ**

| Feature | Strategy 1 | Strategy 2 |
|--------|------------|------------|
| Seasonal Component | Yes | Yes |
| Momentum Window | Fixed return window (M-3 → M-2) | Same but with different ranking logic |
| Holding Period | Flexible | Flexible |
| Gainer Logic | Hybrid seasonal + monthly momentum | Pure momentum with hybrid filters |
| Coverage Months | Jan→Dec | Jan→Dec |

Both systems **use Strategy-3 as the backbone**, applied across valid months with consistent return computation.

---

# ⚙️ **Installation**

To install all required dependencies:

```bash
pip install pandas numpy matplotlib

If you plan to visualize equity curves:

pip install matplotlib


