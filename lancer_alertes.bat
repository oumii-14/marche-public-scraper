@echo off
cd /d "C:\Users\HP\Desktop\marche_public"
call venv\Scripts\activate
python scraper\alertes.py
pause
