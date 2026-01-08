@echo off
echo.
echo ========================================
echo  Meta Ads Creative Intelligence Dashboard V2
echo  Avec Tendances et Sparklines
echo ========================================
echo.

REM Vérifier si les dépendances sont installées
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
    echo.
)

echo Lancement de l'application...
echo L'application va s'ouvrir dans votre navigateur.
echo.
echo Pour arreter: Ctrl+C dans cette fenetre
echo.

streamlit run meta_ads_dashboard.py --server.maxUploadSize=50

pause
