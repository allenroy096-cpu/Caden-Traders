@echo off
REM Batch file to run NIFTY options live data recorder using the correct Python environment
cd /d "%~dp0"
"C:\Users\user\OneDrive\Desktop\Nifty new\.venv310\Scripts\python.exe" "C:\Users\user\OneDrive\Desktop\Nifty new\record_nifty_options_live.py"
pause
