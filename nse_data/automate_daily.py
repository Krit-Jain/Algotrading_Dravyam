#Ready to use
import requests
import pandas as pd
import os
import subprocess
from datetime import datetime, timedelta

# ===================== PATHS =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "Daily_Bhavcopy")
OUTPUT_FILE = os.path.join(BASE_DIR, "NiftyDaily750.csv")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ===================== NSE HEADERS =====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive"
}

# ===================== SYMBOL LIST =====================
from symbols import symbols   # keep your full list here

# ===================== DATE HELPERS =====================
def is_weekday(d):
    return d.weekday() < 5

def get_last_saved_date():
    if not os.path.exists(OUTPUT_FILE):
        return None
    df = pd.read_csv(OUTPUT_FILE)
    if df.empty:
        return None
    return pd.to_datetime(df["Date"], format="%d-%b-%y").max().date()

def trading_dates_between(start, end):
    dates = []
    d = start
    while d <= end:
        if is_weekday(d):
            dates.append(d)
        d += timedelta(days=1)
    return dates

# ===================== DOWNLOAD =====================
def download_bhavcopy(date):
    ddmmyyyy = date.strftime("%d%m%Y")
    filename = f"sec_bhavdata_full_{ddmmyyyy}.csv"
    path = os.path.join(DOWNLOAD_DIR, filename)

    if os.path.exists(path):
        return path

    url = f"https://archives.nseindia.com/products/content/{filename}"
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get("https://www.nseindia.com", timeout=10)

    r = session.get(url, timeout=20)

    if r.status_code == 200 and len(r.content) > 1000:
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ Downloaded {filename}")
        return path

    # Not available yet (likely NSE delay)
    print(f"⏳ Bhavcopy not available yet: {date.strftime('%d-%b-%Y')}")
    return None

# ===================== TRANSFORM + MERGE =====================
def extract_and_merge(bhavcopy_path):
    df = pd.read_csv(bhavcopy_path, low_memory=False)
    df.columns = df.columns.str.strip()
    df["DATE1"] = df["DATE1"].astype(str).str.strip()

    df = df[df["SYMBOL"].isin(symbols)]

    out_df = pd.DataFrame({
        "Date": pd.to_datetime(df["DATE1"], format="%d-%b-%Y").dt.strftime("%d-%b-%y"),
        "Time": 0.0,
        "Open": df["OPEN_PRICE"],
        "High": df["HIGH_PRICE"],
        "Low": df["LOW_PRICE"],
        "Close": df["CLOSE_PRICE"],
        "Quantity": df["TTL_TRD_QNTY"],
        "Average": df["AVG_PRICE"],
        "RSIR-1": 0,
        "RSIAVG-1": 0,
        "MAVG-2": 0,
        "MAVGF-3": 0,
        "MAVGS-3": 0,
        "MAVG-4": 0,
        "symbol": df["SYMBOL"],
        "Unnamed: 0": "",
        "MAVG-1": 0,
        "RSIR-2": 0,
        "RSIAVG-2": 0,
        "MAVG-3": 0,
        "MAVGF-4": 0,
        "MAVGS-4": 0,
        "MAVGF-2": 0,
        "MAVGS-2": 0,
        "RSIR-3": 0,
        "RSIAVG-3": 0
    })

    if os.path.exists(OUTPUT_FILE):
        existing = pd.read_csv(OUTPUT_FILE)
        final = pd.concat([existing, out_df], ignore_index=True)
        final.drop_duplicates(subset=["Date", "symbol"], keep="last", inplace=True)
    else:
        final = out_df

    final.to_csv(OUTPUT_FILE, index=False)
    print(f"➕ Added {len(out_df)} rows")

# ===================== MAIN =====================
if __name__ == "__main__":
    today = datetime.today().date()
    last_saved = get_last_saved_date()

    if last_saved is None:
        start_date = today - timedelta(days=5)
    else:
        start_date = last_saved + timedelta(days=1)

    dates = trading_dates_between(start_date, today)

    for d in dates:
        bhav = download_bhavcopy(d)
        if bhav:
            extract_and_merge(bhav)
