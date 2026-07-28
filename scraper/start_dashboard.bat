@echo off
cd /d "C:\Users\HP\Desktop\marche_public"
start "" .\venv\Scripts\streamlit.exe run dashboard_app.py --server.port 8501 --server.address 0.0.0.0
