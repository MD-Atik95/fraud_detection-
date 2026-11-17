#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
[ -f venv/.installed ] || { pip install -r requirements.txt && touch venv/.installed; }
python run_app.py
