#!/bin/bash

echo ""
echo "========================================"
echo " Meta Ads Creative Intelligence Dashboard V2"
echo " Avec Tendances et Sparklines"
echo "========================================"
echo ""

# Vérifier si les dépendances sont installées
if ! pip show streamlit > /dev/null 2>&1; then
    echo "Installation des dépendances..."
    pip install -r requirements.txt
    echo ""
fi

echo "Lancement de l'application..."
echo "L'application va s'ouvrir dans votre navigateur."
echo ""
echo "Pour arrêter: Ctrl+C"
echo ""

streamlit run meta_ads_dashboard.py --server.maxUploadSize=50
