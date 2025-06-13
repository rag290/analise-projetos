@echo off
cd /d %~dp0
echo Iniciando o dashboard Streamlit...
streamlit run app.py
pause
