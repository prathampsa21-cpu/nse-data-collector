"""
Query and inspect collected NSE 1-minute candle data.
Usage:
    python read_data.py                    # Shows available dates and summary
    python read_data.py RELIANCE           # Shows latest 1-min data for RELIANCE
    python read_data.py TCS 2026-11-03     # Shows 1-min data for TCS on a specific date
"""

import os
import sys
import glob
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def list_available_files():
    parquet_files = sorted(glob.glob(os.path.join(DATA_DIR, "nse_1min_*.parquet")))
    if not parquet_files:
        print("[!] No collected data files found in 'data/' directory yet.")
        return []
    print("\n--- Available Collected Dates ---")
    for f in parquet_files:
        basename = os.path.basename(f)
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f" • {basename} ({size_mb:.2f} MB)")
    return parquet_files

def view_stock_candles(symbol, date_str=None):
    files = sorted(glob.glob(os.path.join(DATA_DIR, "nse_1min_*.parquet")))
    if not files:
        print("[!] No data files found.")
        return

    if date_str:
        target_file = os.path.join(DATA_DIR, f"nse_1min_{date_str}.parquet")
    else:
        target_file = files[-1]  # Latest date

    if not os.path.exists(target_file):
        print(f"[!] File not found: {target_file}")
        return

    print(f"\n[+] Loading data from: {os.path.basename(target_file)}...")
    df = pd.read_parquet(target_file)
    stock_df = df[df['Symbol'] == symbol.upper().strip()]

    if stock_df.empty:
        print(f"[!] Stock '{symbol}' not found in {os.path.basename(target_file)}")
        print(f"Sample available symbols: {list(df['Symbol'].unique()[:10])}")
        return

    print(f"\n=== {symbol.upper()} 1-MINUTE CANDLES ({len(stock_df)} bars) ===")
    print(stock_df.head(5).to_string(index=False))
    print("...")
    print(stock_df.tail(5).to_string(index=False))
    
    # Calculate daily summary
    high = stock_df['High'].max()
    low = stock_df['Low'].min()
    day_open = stock_df['Open'].iloc[0]
    day_close = stock_df['Close'].iloc[-1]
    total_vol = stock_df['Volume'].sum()
    pct_chg = ((day_close - day_open) / day_open) * 100

    print("\n" + "="*45)
    print(f" Day Open:  Rs {day_open:.2f}")
    print(f" Day High:  Rs {high:.2f}")
    print(f" Day Low:   Rs {low:.2f}")
    print(f" Day Close: Rs {day_close:.2f} ({pct_chg:+.2f}%)")
    print(f" Total Vol: {total_vol:,} shares")
    print("="*45)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_available_files()
        print("\nTip: Run 'python read_data.py <SYMBOL>' to view a stock's 1-min data.")
    elif len(sys.argv) == 2:
        view_stock_candles(sys.argv[1])
    elif len(sys.argv) >= 3:
        view_stock_candles(sys.argv[1], sys.argv[2])
