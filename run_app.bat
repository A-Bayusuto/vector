@echo off
echo Creating virtual environment 'rag_venv'...

REM Check if Python is available
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not added to PATH.
    pause
    exit /b
)

REM Create the virtual environment
python -m venv rag_venv

IF EXIST rag_venv (
    echo Virtual environment 'rag_venv' created successfully.
) ELSE (
    echo Failed to create virtual environment.
    pause
    exit /b
)

REM Activate the virtual environment
echo Activating 'rag_venv'...
call rag_venv\Scripts\activate

REM Check if requirements.txt exists
IF EXIST requirements.txt (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
) ELSE (
    echo requirements.txt not found. Skipping package installation.
)

REM Run the Flask app (app.py)
echo Running Flask app...
python app.py

pause
