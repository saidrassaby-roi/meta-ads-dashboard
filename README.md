# 🎯 Meta Ads Creative Intelligence Dashboard V2

Application de pilotage intelligent des créatives publicitaires Meta Ads.
**Avec support des tendances et sparklines !**

## ✨ Nouveautés V2

- 📈 **Sparklines** : Visualisez l'évolution de chaque créative sur 14 jours
- 📊 **Tendances 7j** : Score de tendance intégré au potentiel de scale
- 🔄 **Import quotidien** : Chargez vos données jour par jour pour des analyses dynamiques
- 🎯 **Actions plus précises** : Recommandations basées sur la trajectoire, pas seulement les totaux

## 🚀 Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
streamlit run meta_ads_dashboard.py
```

**Windows** : Double-cliquez sur `run.bat`
**Mac/Linux** : Exécutez `./run.sh`

## 📁 Préparer vos exports Meta Ads

### Export 1 : Données agrégées (obligatoire)

C'est le fichier principal avec les totaux sur votre période d'analyse.

1. Allez dans **Meta Ads Manager**
2. Sélectionnez le niveau **Publicité**
3. Choisissez votre période (ex: 30 derniers jours)
4. **Ventilation** : Aucune (très important !)
5. Colonnes recommandées :
   - Impressions, Couverture
   - Clics sur un lien, CTR (lien)
   - CPC (lien), CPM
   - Montant dépensé
   - Achats, ROAS
   - Répétition
6. **Exporter** → CSV

### Export 2 : Données quotidiennes (recommandé)

Ce fichier permet d'avoir les tendances et sparklines.

1. **Même configuration** que l'export agrégé
2. **Ventilation** : Par jour ⭐
3. **Exporter** → CSV

Vous aurez ainsi :
- Export agrégé : 1 ligne par créative
- Export quotidien : 1 ligne par créative **par jour**

## 🎯 Utilisation quotidienne

```
Lundi matin (5 min) :
1. Lancer l'application
2. Charger l'export agrégé
3. Charger l'export quotidien (optionnel mais recommandé)
4. Onglet "Actions du jour"
5. Exécuter les recommandations
✅ Done !
```

## 📊 Comprendre les tendances

### Score de tendance

Calcul basé sur l'évolution 7j récents vs 7j précédents :
- **CTR** (40%) : Hausse = bon
- **CPC** (25%) : Hausse = mauvais (inversé)
- **CPM** (20%) : Hausse = mauvais (inversé)
- **Volume** (15%) : Hausse = bon

### Signaux visuels

| Signal | Signification |
|--------|---------------|
| ↗ +XX% (vert) | Tendance positive (>+15%) |
| ↘ -XX% (rouge) | Tendance négative (<-15%) |
| → stable (gris) | Stable (-15% à +15%) |

### Impact sur le potentiel

Le score de tendance représente **25%** du potentiel de scale :
- Tendance > +50% → Composante à 90/100
- Tendance +20 à +50% → Composante à 75/100
- Tendance 0 à +20% → Composante à 60/100
- Tendance -20% à 0% → Composante à 40/100
- Tendance < -20% → Composante à 20/100

## 📈 Sparklines

Les mini-graphiques montrent l'évolution du CTR sur 14 jours.

**Lecture rapide :**
- Courbe montante = performance en amélioration
- Courbe descendante = fatigue créative probable
- Courbe plate = stabilité

**Couleurs :**
- 🟢 Vert : +10% sur la période
- 🔴 Rouge : -10% sur la période
- ⚫ Gris : Stable

## 🎬 Règles d'action mises à jour

| Action | Critères V2 |
|--------|-------------|
| 🚀 **Scaler** | Potentiel ≥ 60 ET Confiance ≥ 70% |
| ⚡ **Tester** | ROAS > 5 OU Potentiel > 50, MAIS Confiance < 60% |
| 👁️ **Surveiller** | Frequency > 3 OU Tendance entre -10% et -30% |
| ⏸️ **Pauser** | Tendance < -30% OU (Frequency > 4 ET Confiance élevée) |

## 🔧 Dépannage

### "Tendances non disponibles"
→ Vérifiez que le fichier quotidien a bien une colonne date

### "Colonnes non reconnues"
→ L'app détecte automatiquement les colonnes Meta Ads françaises et anglaises
→ Si problème, vérifiez que les noms de colonnes correspondent à ceux de Meta

### Erreur de chargement
→ Vérifiez l'encodage du CSV (UTF-8 recommandé)
→ Vérifiez le séparateur (virgule par défaut)

## 📁 Structure du projet

```
meta-ads-app-v2/
├── meta_ads_dashboard.py   # Application principale
├── requirements.txt        # Dépendances Python
├── README.md              # Ce fichier
├── run.bat                # Script Windows
└── run.sh                 # Script Mac/Linux
```

## 🌐 Déploiement cloud (optionnel)

1. Créez un repo GitHub avec ces fichiers
2. Allez sur [Streamlit Cloud](https://streamlit.io/cloud)
3. Connectez votre repo
4. Déployez !

URL personnalisée : `https://votre-app.streamlit.app`

---

**BNB Solutions Digitales** • Saint-Denis, La Réunion
Version 2.0 - Janvier 2026
