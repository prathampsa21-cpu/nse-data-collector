@echo off
cd /d "%~dp0"
echo ========================================================
echo Running NSE 1-Minute Candle Collector...
echo ========================================================
python collector.py
echo ========================================================
echo Finished! Check the 'data/' folder.
echo ========================================================
