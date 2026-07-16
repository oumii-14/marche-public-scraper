@echo off
cd /d "C:\Users\HP\Desktop\marche_public"
call venv\Scripts\activate
python scraper\scrape.py
pause
