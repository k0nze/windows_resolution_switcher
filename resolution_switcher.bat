@echo off
set SCRIPT_DIR=%~dp0
cd "%SCRIPT_DIR%"

:: Define the path to the virtual environment's python executable
set PYTHON_EXE="%SCRIPT_DIR%\.venv\Scripts\pythonw.exe"

:: Check if the python executable exists
if not exist %PYTHON_EXE% (
    echo Error: Python executable not found at %PYTHON_EXE%
    echo Please ensure the virtual environment is set up correctly.
    pause
    exit /b 1
)

:: Execute the Python script using the full path to the venv's pythonw
%PYTHON_EXE% resolution_switcher.py