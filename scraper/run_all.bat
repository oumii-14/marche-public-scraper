@echo off
cd /d "C:\Users\HP\Desktop\marche_public"
echo [%date% %time%] Debut du scraping...
.\venv\Scripts\python.exe "C:\Users\HP\Desktop\marche_public\scraper\scrape.py"
echo [%date% %time%] Scraping termine, envoi des alertes...
.\venv\Scripts\python.exe "C:\Users\HP\Desktop\marche_public\scraper\alertes.py"
echo [%date% %time%] Termine.
