@echo off
REM Launch the Admit Card Generator app.
REM First run: install Streamlit with  pip install -r requirements.txt
cd /d "%~dp0"
python -m streamlit run app.py
pause
