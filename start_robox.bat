@echo off
title Robox - Assistant Emotionnel
color 1F
echo.
echo  ╔══════════════════════════════════════╗
echo  ║     ROBOX - Assistant Emotionnel     ║
echo  ║         Demarrage en cours...        ║
echo  ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/3] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe!
    pause
    exit
)

echo [2/3] Installation des dependances...
pip install -q -r requirements.txt

echo [3/3] Lancement de Robox...
echo.
echo  Robox sera accessible sur: http://localhost:5000
echo  Appuie sur CTRL+C pour arreter le serveur
echo.

start "" "http://localhost:5000"
python app.py

pause
