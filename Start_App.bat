@echo off
cd /d "%~dp0"
title Fraud Monitor
if not exist venv (
  echo Creating environment...
  python -m venv venv || (echo Python is not installed. Get it from python.org & pause & exit /b 1)
)
call venv\Scripts\activate
if not exist venv\.installed (
  echo Installing packages, first run only - please wait...
  pip install -r requirements.txt && echo ok> venv\.installed
)
python run_app.py
pause
