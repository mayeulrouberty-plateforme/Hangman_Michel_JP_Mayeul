@echo off
echo === Cosmic Query Agent ===
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Check if dependencies installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting application...
echo Open http://localhost:8501 in your browser
echo.

streamlit run app.py
