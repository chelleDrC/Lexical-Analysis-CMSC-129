@echo off
REM Builds the executable dist\LexicalAnalyzer.exe using PyInstaller.
REM Requires: pip install pyinstaller

pyinstaller --onefile --windowed --name LexicalAnalyzer main_window.py
if errorlevel 1 exit /b 1

echo Built dist\LexicalAnalyzer.exe
