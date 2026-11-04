"""
NSE 1-Minute Candle & Volume Daily Collector
============================================
Collects full-day 1-minute OHLCV (Open, High, Low, Close, Volume) data 
for all NSE stocks with Net Worth / Market Cap >= Rs 1,000 Crore.
Saves data into high-performance compressed Parquet and CSV formats.
"""

import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
import pytz
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

# Target directory for stored data
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_nse_universe():
    """
    Fetches the list of NSE equities with Market Cap >= Rs 1,000 Crore.
    The NIFTY Total Market index covers the top ~750 companies on NSE,
    all of which have market cap well above Rs 1,000 Cr (lowest is > Rs 1,500 Cr).
    """
    urls = [
        "https://archives.nseindia.com/content/indices/ind_niftytotalmarket_list.csv",
        "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    symbols = set()

    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                df = pd.read_csv(resp)
                if 'Symbol' in df.columns:
                    for sym in df['Symbol'].dropna():
                        cleaned = sym.strip().upper()
                        if cleaned:
                            symbols.add(f"{cleaned}.NS")
        except Exception as e:
            print(f"[!] Warning fetching {url}: {e}")

    # Fallback to predefined top liquid symbols if network failed
    if not symbols:
        print("[!] Using fallback top universe list...")
        fallback = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC"]
        symbols = {f"{s}.NS" for s in fallback}

    symbol_list = sorted(list(symbols))
    print(f"[✓] Universe loaded: {len(symbol_list)} stocks with Market Cap >= 1,000 Cr")
    return symbol_list

def fetch_stock_1m(symbol):
    """
    Downloads full-day 1-minute OHLCV data for a single symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Fetch 1-day 1-minute data
        df = ticker.history(period="1d", interval="1m", auto_adjust=False)
        
        if df.empty or len(df) < 5:
            return None

        # Clean columns
        cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols].copy()
        
        # Ensure standard column names
        clean_symbol = symbol.replace('.NS', '')
        df['Symbol'] = clean_symbol
        
        # Convert index to IST timestamp
        df.reset_index(inplace=True)
        # Handle datetime column name (Datetime or Date)
        date_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
        df.rename(columns={date_col: 'Timestamp'}, inplace=True)
        
        # Convert to Asia/Kolkata timezone
        if df['Timestamp'].dt.tz is not None:
            df['Timestamp'] = df['Timestamp'].dt.tz_convert('Asia/Kolkata').dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
        return df[['Timestamp', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception:
        return None

def run_collector(max_workers=12):
    """
    Runs multi-threaded collector across all stocks in universe.
    """
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    today_str = now_ist.strftime('%Y-%m-%d')
    start_time = time.time()

    print("=" * 65)
    print(f"  NSE 1-MINUTE CANDLE & VOLUME COLLECTOR")
    print(f"  Date: {today_str} | Current IST Time: {now_ist.strftime('%H:%M:%S')}")
    print("=" * 65)

    symbols = get_nse_universe()
    total_symbols = len(symbols)
    print(f"[+] Starting download for {total_symbols} stocks using {max_workers} worker threads...\n")

    successful_dfs = []
    failed_symbols = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sym = {executor.submit(fetch_stock_1m, sym): sym for sym in symbols}
        
        completed = 0
        for future in as_completed(future_to_sym):
            sym = future_to_sym[future]
            completed += 1
            res = future.result()
            
            clean_sym = sym.replace('.NS', '')
            if res is not None and not res.empty:
                successful_dfs.append(res)
                if completed % 50 == 0 or completed == total_symbols:
                    print(f"[{completed}/{total_symbols}] Progress: {len(successful_dfs)} fetched successfully...")
            else:
                failed_symbols.append(clean_sym)

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"  DOWNLOAD FINISHED in {elapsed:.1f} seconds")
    print(f"  Successful Stocks: {len(successful_dfs)} / {total_symbols}")
    print(f"  Failed / No Data: {len(failed_symbols)}")
    print("=" * 65)

    if successful_dfs:
        final_df = pd.concat(successful_dfs, ignore_index=True)
        # Sort by Symbol and Timestamp
        final_df.sort_values(by=['Symbol', 'Timestamp'], inplace=True)

        # Output paths
        parquet_file = os.path.join(DATA_DIR, f"nse_1min_{today_str}.parquet")
        csv_file = os.path.join(DATA_DIR, f"nse_1min_{today_str}.csv")

        # Save Parquet (compressed, fast, light)
        final_df.to_parquet(parquet_file, index=False, compression='snappy')
        parquet_size_mb = os.path.getsize(parquet_file) / (1024 * 1024)
        print(f"\n[✓] Saved PARQUET: {parquet_file} ({parquet_size_mb:.2f} MB)")

        # Save CSV
        final_df.to_csv(csv_file, index=False)
        csv_size_mb = os.path.getsize(csv_file) / (1024 * 1024)
        print(f"[✓] Saved CSV:     {csv_file} ({csv_size_mb:.2f} MB)")

        print(f"[✓] Total 1-minute candles saved: {len(final_df):,}")
        return parquet_file
    else:
        print("[!] No data was collected. (Check if market was open or internet connectivity)")
        return None

if __name__ == "__main__":
    run_collector()
