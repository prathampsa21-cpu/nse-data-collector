# NSE 1-Minute Candle & Volume Daily Collector (₹1,000 Cr+ Stocks)

Autonomous, set-and-forget pipeline that collects full-day 1-minute OHLCV (Open, High, Low, Close, Volume) data for all NSE stocks with Net Worth / Market Capitalization $\\ge$ ₹1,000 Crore.

---

## 🌟 How It Works When Laptop Is Closed ("Laptop Khule Ya Na Khule")

If your laptop is completely powered off or shut down, local scripts cannot run. To solve this, this repository includes **100% Free Cloud Automation via GitHub Actions**:

```
[ Every Mon-Fri at 4:00 PM IST ]
              │
              ▼
   GitHub Cloud Runner wakes up
   (Free Linux VM in the Cloud)
              │
              ▼
   Runs collector.py
   • Downloads ~750 stocks (>1,000 Cr M-Cap)
   • Pulls 1-min candles (9:15 AM - 3:30 PM) with Volume
              │
              ▼
   Saves to data/nse_1min_YYYY-MM-DD.parquet & .csv
              │
              ▼
   Automatically commits to your private/public GitHub Repo!
```

**Whenever you open your laptop (even days or weeks later), all data is already collected, timestamped, and waiting for you!**

---

## 🚀 Setup 1: 100% Free Cloud Setup (Laptop Bandh Ho Tab Bhi Chalega)

1. Create a new repository on [GitHub](https://github.com/new) (e.g. `nse-1min-data`). You can keep it **Private**.
2. Push this folder to your GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/nse-1min-data.git
   git push -u origin main
   ```
3. In your GitHub repository:
   - Go to **Settings** → **Actions** → **General**.
   - Under **Workflow permissions**, select **"Read and write permissions"** and click **Save**.
4. That's it! Every weekday at 4:00 PM IST, GitHub will automatically collect the data and commit it to the `data/` folder.
5. You can also trigger it manually anytime by going to **Actions** → **Daily NSE 1-Min Data Collector** → **Run workflow**.

---

## 💻 Setup 2: Local Windows Task Scheduler (Agar Laptop On/Sleep Rehta Hai)

If your laptop is usually on or in sleep mode at 4:00 PM:
1. Open PowerShell as Administrator.
2. Run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\\setup_windows_scheduler.ps1
   ```
3. A Windows Scheduled Task named `NSE_1Min_Daily_Collector` will be created to run `run_daily.bat` every weekday at 4:00 PM IST.

---

## 📊 How to Inspect / Query Collected Data

Run `read_data.py`:

```bash
# View list of all collected dates
python read_data.py

# View today's 1-minute candles for a specific stock
python read_data.py RELIANCE
python read_data.py TCS
python read_data.py HDFCBANK

# View a specific past date
python read_data.py INFY 2026-11-03
```

### Loading in Python / Pandas:

```python
import pandas as pd

# Load full market 1-min data for a day
df = pd.read_parquet("data/nse_1min_2026-11-03.parquet")

# Filter for a specific stock
tcs_df = df[df['Symbol'] == 'TCS']
print(tcs_df.head())
```

---

## 📁 File Structure

```
nse-data-collector/
├── .github/
│   └── workflows/
│       └── daily_nse_collector.yml    # Cloud Cron (Mon-Fri 4:00 PM IST)
├── data/                              # Output folder for .parquet & .csv
├── collector.py                       # Main multithreaded downloader
├── read_data.py                       # Quick query & inspection tool
├── run_daily.bat                      # Windows launcher
├── setup_windows_scheduler.ps1        # One-click Windows Task Scheduler
├── requirements.txt                   # Python dependencies
└── README.md                          # Documentation
```
