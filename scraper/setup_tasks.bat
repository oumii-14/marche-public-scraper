@echo off
echo ========================================
echo Creation de la tache planifiee...
echo ========================================

:: Tache unique : Scraper + Alertes a 8h tous les jours
schtasks /create /tn "MarchePublic_Scraper" /tr "C:\Users\HP\Desktop\marche_public\scraper\run_all.bat" /sc daily /st 10:00 /f

echo ========================================
echo Termine ! Tache creee avec succes.
echo - Scraper + Alertes: tous les jours a 10:00
echo ========================================
pause
