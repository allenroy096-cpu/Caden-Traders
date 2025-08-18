# Windows Task Scheduler setup for trading bot automation
# Save this as schedule_trading_bot.bat in the project root

@echo off
set SCRIPT_PATH=%~dp0trading_bot\main.py
set PYTHON_EXE=python

REM Run the trading bot main script
%PYTHON_EXE% "%SCRIPT_PATH%"
