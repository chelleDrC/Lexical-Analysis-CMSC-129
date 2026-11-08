@echo off
REM Builds the executable dist\PredictiveParser.exe using PyInstaller.
REM Requires: pip install pyinstaller

pyinstaller --onefile --windowed --name PredictiveParser main.py
if errorlevel 1 exit /b 1

echo Built dist\PredictiveParser.exe
