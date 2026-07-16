@echo off
cd /d "C:\Users\HP\Desktop\marche_public"
.\venv\Scripts\python.exe "C:\Users\HP\Desktop\marche_public\scraper\scrape.py" >> "C:\Users\HP\Desktop\marche_public\logs\scraper.log" 2>&1
