@echo off
echo ========================================
echo Creating scheduled tasks...
echo ========================================

:: Tâche 1 : Scraper à 8h tous les jours
schtasks /create /tn "MarchePublic_Scraper" /tr "C:\Users\HP\Desktop\marche_public\scraper\run_scraper.bat" /sc daily /st 08:00 /f

:: Tâche 2 : Alertes à 9h tous les jours
schtasks /create /tn "MarchePublic_Alertes" /tr "C:\Users\HP\Desktop\marche_public\scraper\run_alertes.bat" /sc daily /st 09:00 /f

echo ========================================
echo Done! Tasks created successfully.
echo - Scraper: daily at 08:00
echo - Alertes: daily at 09:00
echo ========================================
pause
