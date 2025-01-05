@echo off

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if they exist
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Run the Streamlit app
echo Starting Streamlit app...
streamlit run app.py
