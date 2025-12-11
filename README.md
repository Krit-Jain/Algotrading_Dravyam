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
