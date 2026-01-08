"""
Meta Ads Creative Intelligence Dashboard V2
===========================================
Application de pilotage des créatives publicitaires Meta Ads.
Avec support des données quotidiennes pour tendances et sparklines.

Installation:
    pip install streamlit pandas numpy plotly

Lancement:
    streamlit run meta_ads_dashboard.py

Auteur: BNB Solutions Digitales
Version: 2.0
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import json

# Configuration de la page
st.set_page_config(
    page_title="Creative Intelligence Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    .action-card {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
    }
    .scale-card { background: #ECFDF5; border-color: #10B981; }
    .test-card { background: #EFF6FF; border-color: #3B82F6; }
    .monitor-card { background: #FFFBEB; border-color: #F59E0B; }
    .pause-card { background: #FEF2F2; border-color: #EF4444; }
    .sparkline-up { color: #10B981; }
    .sparkline-down { color: #EF4444; }
    .sparkline-stable { color: #6B7280; }
    .trend-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .trend-up { background: #D1FAE5; color: #065F46; }
    .trend-down { background: #FEE2E2; color: #991B1B; }
    .trend-stable { background: #F3F4F6; color: #374151; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# FONCTIONS DE TRAITEMENT
# ============================================================================

def detect_columns(df):
    """Détecte et mappe les colonnes du CSV Meta Ads."""
    
    # Mapping des colonnes possibles vers noms standardisés
    column_mappings = {
        'nom': ['Nom de la publicité', 'Ad name', 'nom_publicite', 'nom'],
        'impressions': ['Impressions', 'impressions'],
        'reach': ['Couverture', 'Reach', 'reach', 'couverture'],
        'clics_lien': ['Clics sur un lien', 'Link clicks', 'clics_lien', 'Clics sur le lien'],
        'clics_tous': ['Clics (tous)', 'Clicks (all)', 'clics_tous'],
        'ctr_lien': ['CTR (taux de clics sur le lien)', 'CTR unique (taux de clics sur le lien)', 
                     'Link click-through rate', 'ctr_lien', 'CTR (lien)', 'ctr_unique_lien'],
        'cpc_lien': ['CPC (coût par clic sur un lien) (EUR)', 'Cost per link click', 'cpc_lien',
                     'CPC (coût par clic sur un lien)'],
        'cpm': ['CPM (Coût pour 1 000 impressions) (EUR)', 'CPM (cost per 1,000 impressions)', 
                'cpm', 'CPM'],
        'depense': ['Montant dépensé (EUR)', 'Amount spent', 'depense', 'montant_depense',
                    'Montant dépensé'],
        'achats': ['Achats', 'Purchases', 'achats'],
        'valeur_achats': ['Valeur de conversion des achats', 'Purchase conversion value', 
                         'valeur_achats', 'valeur_conversion'],
        'roas': ['ROAS (retour sur les dépenses publicitaires) des achats', 'Purchase ROAS', 
                'roas', 'ROAS'],
        'cpa': ['Coût par résultat', 'Cost per result', 'cpa', 'cout_par_resultat'],
        'frequency': ['Répétition', 'Frequency', 'frequency', 'frequence'],
        'ajouts_panier': ['Ajouts au panier', 'Adds to cart', 'ajouts_panier'],
        'date_debut': ['Début des rapports', 'Reporting starts', 'date_debut'],
        'date_fin': ['Fin des rapports', 'Reporting ends', 'date_fin'],
    }
    
    # Créer le mapping inverse
    rename_dict = {}
    for standard_name, possible_names in column_mappings.items():
        for col_name in possible_names:
            if col_name in df.columns:
                rename_dict[col_name] = standard_name
                break
    
    return rename_dict


@st.cache_data
def load_and_process_data(uploaded_file):
    """Charge et traite le fichier CSV exporté de Meta Ads."""
    
    # Lire le CSV
    df = pd.read_csv(uploaded_file)
    
    # Détecter et renommer les colonnes
    rename_dict = detect_columns(df)
    df = df.rename(columns=rename_dict)
    
    # Convertir les colonnes numériques
    numeric_cols = ['impressions', 'reach', 'clics_lien', 'clics_tous', 'ctr_lien', 
                    'cpc_lien', 'cpm', 'depense', 'achats', 'valeur_achats', 'roas', 
                    'cpa', 'frequency', 'ajouts_panier']
    
    for col in numeric_cols:
        if col in df.columns:
            # Gérer les formats avec virgules comme séparateur décimal
            if df[col].dtype == object:
                df[col] = df[col].str.replace(',', '.').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Ajouter colonnes manquantes avec valeurs par défaut
    default_cols = {
        'valeur_achats': 0,
        'achats': 0,
        'roas': 0,
        'ajouts_panier': 0,
        'cpa': 0
    }
    for col, default in default_cols.items():
        if col not in df.columns:
            df[col] = default
    
    # Calculer frequency si manquant
    if 'frequency' not in df.columns or df['frequency'].sum() == 0:
        df['frequency'] = np.where(df['reach'] > 0, df['impressions'] / df['reach'], 1)
    
    return df


@st.cache_data
def load_daily_data(uploaded_file):
    """Charge les données quotidiennes pour les tendances et sparklines."""
    
    df = pd.read_csv(uploaded_file)
    
    # Détecter et renommer les colonnes
    rename_dict = detect_columns(df)
    df = df.rename(columns=rename_dict)
    
    # Convertir les colonnes numériques
    numeric_cols = ['impressions', 'reach', 'clics_lien', 'ctr_lien', 'cpc_lien', 
                    'cpm', 'depense', 'achats']
    
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.replace(',', '.').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Convertir la date
    if 'date_debut' in df.columns:
        df['date'] = pd.to_datetime(df['date_debut'], dayfirst=True, errors='coerce')
    
    return df


def calculate_trends_from_daily(df_daily, lookback_days=14):
    """Calcule les tendances à partir des données quotidiennes."""
    
    if df_daily is None or len(df_daily) == 0 or 'date' not in df_daily.columns:
        return {}, {}
    
    # Nettoyer les dates
    df_daily = df_daily.dropna(subset=['date'])
    if len(df_daily) == 0:
        return {}, {}
    
    date_max = df_daily['date'].max()
    date_7j = date_max - timedelta(days=6)
    date_14j = date_max - timedelta(days=13)
    
    trends = {}
    sparklines = {}
    
    for nom in df_daily['nom'].unique():
        df_crea = df_daily[df_daily['nom'] == nom].sort_values('date')
        
        # Données pour sparkline (14 derniers jours)
        df_14j = df_crea[df_crea['date'] >= date_14j]
        
        # Générer les données sparkline
        sparkline_data = []
        dates = pd.date_range(start=date_14j, end=date_max, freq='D')
        
        for d in dates:
            row = df_14j[df_14j['date'].dt.date == d.date()]
            if len(row) > 0 and row.iloc[0]['impressions'] > 0:
                sparkline_data.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'impressions': float(row.iloc[0]['impressions']),
                    'ctr': float(row.iloc[0].get('ctr_lien', 0)),
                    'depense': float(row.iloc[0].get('depense', 0)),
                    'cpm': float(row.iloc[0].get('cpm', 0))
                })
            else:
                sparkline_data.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'impressions': 0,
                    'ctr': 0,
                    'depense': 0,
                    'cpm': 0
                })
        
        sparklines[nom] = sparkline_data
        
        # Calculer les tendances (7j récents vs 7j précédents)
        df_recent = df_crea[df_crea['date'] >= date_7j]
        df_precedent = df_crea[(df_crea['date'] >= date_14j) & (df_crea['date'] < date_7j)]
        
        def safe_mean(series):
            valid = series[series > 0]
            return valid.mean() if len(valid) > 0 else 0
        
        def calc_trend(recent_val, prec_val):
            if prec_val > 0:
                return ((recent_val - prec_val) / prec_val) * 100
            return 0
        
        ctr_recent = safe_mean(df_recent['ctr_lien']) if 'ctr_lien' in df_recent.columns else 0
        ctr_prec = safe_mean(df_precedent['ctr_lien']) if 'ctr_lien' in df_precedent.columns else 0
        
        cpc_recent = safe_mean(df_recent['cpc_lien']) if 'cpc_lien' in df_recent.columns else 0
        cpc_prec = safe_mean(df_precedent['cpc_lien']) if 'cpc_lien' in df_precedent.columns else 0
        
        cpm_recent = safe_mean(df_recent['cpm']) if 'cpm' in df_recent.columns else 0
        cpm_prec = safe_mean(df_precedent['cpm']) if 'cpm' in df_precedent.columns else 0
        
        impr_recent = df_recent['impressions'].sum() if 'impressions' in df_recent.columns else 0
        impr_prec = df_precedent['impressions'].sum() if 'impressions' in df_precedent.columns else 0
        
        trend_ctr = calc_trend(ctr_recent, ctr_prec)
        trend_cpc = calc_trend(cpc_recent, cpc_prec)
        trend_cpm = calc_trend(cpm_recent, cpm_prec)
        trend_impr = calc_trend(impr_recent, impr_prec)
        
        # Score de tendance global (pondéré)
        # CTR en hausse = bon, CPC en hausse = mauvais, CPM en hausse = mauvais
        trend_score = (
            0.40 * trend_ctr +
            0.25 * (-trend_cpc) +  # Inversé
            0.20 * (-trend_cpm) +  # Inversé
            0.15 * trend_impr
        )
        
        signal = 'up' if trend_score > 15 else 'down' if trend_score < -15 else 'stable'
        
        trends[nom] = {
            'ctr': round(trend_ctr, 1),
            'cpc': round(trend_cpc, 1),
            'cpm': round(trend_cpm, 1),
            'impressions': round(trend_impr, 1),
            'score': round(trend_score, 1),
            'signal': signal
        }
    
    return trends, sparklines


def parse_creative_name(nom):
    """Extrait les composants du nom de la créative."""
    import re
    
    usp = 'Autre'
    hook = 'Autre'
    format_type = 'IMG'
    
    # Extraire le format
    nom_upper = nom.upper()
    if nom_upper.startswith('IMG'):
        format_type = 'IMG'
    elif nom_upper.startswith('VID'):
        format_type = 'VID'
    elif nom_upper.startswith('GIF'):
        format_type = 'GIF'
    elif nom_upper.startswith('CAR'):
        format_type = 'CAR'
    
    # Extraire USP
    usp_match = re.search(r'USP\s*:\s*([^-]+)', nom, re.IGNORECASE)
    if usp_match:
        usp = usp_match.group(1).strip()
    elif 'Nouvelle collection' in nom:
        usp = 'Nouvelle collection'
    
    # Extraire Hook
    nom_lower = nom.lower()
    if 'probleme/solution' in nom_lower or 'problème/solution' in nom_lower:
        hook = 'Problème/Solution'
    elif 'probleme/frustation' in nom_lower or 'problème/frustration' in nom_lower:
        hook = 'Problème/Frustration'
    elif ' pv ' in nom_lower or nom_lower.startswith('pv ') or ' - pv -' in nom_lower:
        hook = 'Proposition de Valeur'
    elif 'produit neutre' in nom_lower:
        hook = 'Produit neutre'
    
    return {'usp': usp, 'hook': hook, 'format': format_type}


def calculate_confidence(row):
    """Calcule le coefficient de confiance basé sur le volume."""
    impressions = row.get('impressions', 0)
    achats = row.get('achats', 0)
    clics = row.get('clics_lien', 0)
    
    # Score impressions
    if impressions < 1000:
        score_impr = 0.3
    elif impressions < 5000:
        score_impr = 0.5
    elif impressions < 10000:
        score_impr = 0.7
    elif impressions < 50000:
        score_impr = 0.85
    else:
        score_impr = 1.0
    
    # Score conversions
    if achats < 5:
        score_conv = 0.4
    elif achats < 15:
        score_conv = 0.6
    elif achats < 30:
        score_conv = 0.8
    else:
        score_conv = 1.0
    
    # Score clics
    if clics < 50:
        score_clics = 0.5
    elif clics < 200:
        score_clics = 0.7
    elif clics < 500:
        score_clics = 0.85
    else:
        score_clics = 1.0
    
    return round(0.3 * score_impr + 0.4 * score_conv + 0.3 * score_clics, 2)


def calculate_scale_potential(row, score_global_ajuste, coef_conf, trend_score=0):
    """Calcule le potentiel de scale."""
    perf_score = min(100, max(0, score_global_ajuste))
    
    # Score tendance
    if trend_score > 50:
        trend_component = 90
    elif trend_score > 20:
        trend_component = 75
    elif trend_score > 0:
        trend_component = 60
    elif trend_score > -20:
        trend_component = 40
    else:
        trend_component = 20
    
    # Score frequency
    freq = row.get('frequency', 2)
    if freq < 1.5:
        freq_score = 100
    elif freq < 2.0:
        freq_score = 85
    elif freq < 2.5:
        freq_score = 70
    elif freq < 3.0:
        freq_score = 55
    elif freq < 4.0:
        freq_score = 35
    else:
        freq_score = 15
    
    conf_score = coef_conf * 100
    
    # Formule avec tendance
    potential = (
        0.25 * perf_score +
        0.25 * trend_component +
        0.20 * freq_score +
        0.15 * (100 - abs(row.get('trend_cpm', 0))) +  # CPM stable = bon
        0.15 * conf_score
    )
    
    return round(potential)


def calculate_scores(df, trends=None):
    """Calcule les scores pour chaque créative."""
    
    # Filtrer les créas avec assez de volume
    df = df[df['impressions'] >= 500].copy()
    
    if len(df) == 0:
        return df
    
    # Calculer les statistiques
    def calc_stats(values):
        valid = values[values > 0]
        if len(valid) == 0:
            return 0, 1
        return valid.mean(), valid.std() if valid.std() > 0 else 1
    
    # Z-scores
    def z_score(value, mean, std, inverse=False):
        if pd.isna(value) or value == 0:
            return 0
        z = (value - mean) / std
        return -z if inverse else z
    
    # Stats globales
    roas_mean, roas_std = calc_stats(df['roas'])
    ctr_mean, ctr_std = calc_stats(df['ctr_lien'])
    cpc_mean, cpc_std = calc_stats(df['cpc_lien'])
    cpm_mean, cpm_std = calc_stats(df['cpm'])
    reach_mean, reach_std = calc_stats(df['reach'])
    clics_mean, clics_std = calc_stats(df['clics_lien'])
    
    # Calculer CVR
    df['cvr'] = np.where(df['clics_lien'] > 0, 
                         (df['achats'] / df['clics_lien']) * 100, 0)
    cvr_mean, cvr_std = calc_stats(df['cvr'])
    
    # Calculer CPA pour ceux qui ont des achats
    df['cpa_calc'] = np.where(df['achats'] > 0, df['depense'] / df['achats'], 0)
    cpa_mean, cpa_std = calc_stats(df[df['cpa_calc'] > 0]['cpa_calc'])
    if cpa_mean == 0:
        cpa_mean = df['depense'].mean()
    
    # Calcul des Z-scores et scores
    scores_data = []
    for idx, row in df.iterrows():
        # Z-scores individuels
        z_roas = z_score(row['roas'], roas_mean, roas_std)
        z_cpa = z_score(row['cpa_calc'] if row['cpa_calc'] > 0 else cpa_mean * 2, cpa_mean, cpa_std, inverse=True)
        z_cvr = z_score(row['cvr'], cvr_mean, cvr_std)
        z_ctr = z_score(row['ctr_lien'], ctr_mean, ctr_std)
        z_cpc = z_score(row['cpc_lien'], cpc_mean, cpc_std, inverse=True)
        z_cpm = z_score(row['cpm'], cpm_mean, cpm_std, inverse=True)
        z_reach = z_score(row['reach'], reach_mean, reach_std)
        z_clics = z_score(row['clics_lien'], clics_mean, clics_std)
        
        # Scores composites (0-100)
        def z_to_100(z):
            return max(0, min(100, 50 + z * 10))
        
        score_profit = z_to_100(0.45 * z_roas + 0.35 * z_cpa + 0.20 * z_cvr)
        score_trafic = z_to_100(0.50 * z_ctr + 0.30 * z_cpc + 0.20 * z_clics)
        score_notoriete = z_to_100(0.40 * z_cpm + 0.60 * z_reach)
        score_global = (score_profit + score_trafic + score_notoriete) / 3
        
        # Coefficient de confiance
        coef_conf = calculate_confidence(row)
        
        # Score ajusté
        score_global_ajuste = score_global * coef_conf + 50 * (1 - coef_conf)
        
        # Récupérer les tendances si disponibles
        trend_data = trends.get(row['nom'], {}) if trends else {}
        trend_score = trend_data.get('score', 0)
        trend_signal = trend_data.get('signal', 'stable')
        trend_ctr = trend_data.get('ctr', 0)
        trend_cpm = trend_data.get('cpm', 0)
        
        # Créer un dict row enrichi pour le calcul du potentiel
        row_dict = row.to_dict()
        row_dict['trend_cpm'] = trend_cpm
        
        # Potentiel de scale (avec tendance si disponible)
        potential = calculate_scale_potential(row_dict, score_global_ajuste, coef_conf, trend_score)
        
        scores_data.append({
            'score_profitabilite': score_profit,
            'score_trafic': score_trafic,
            'score_notoriete': score_notoriete,
            'score_global': score_global,
            'coefficient_confiance': coef_conf,
            'score_global_ajuste': score_global_ajuste,
            'scale_potential': potential,
            'trend_score': trend_score,
            'trend_signal': trend_signal,
            'trend_ctr': trend_ctr,
            'trend_cpm': trend_cpm
        })
    
    # Ajouter les scores au dataframe
    scores_df = pd.DataFrame(scores_data)
    for col in scores_df.columns:
        df[col] = scores_df[col].values
    
    # Parser les noms
    parsed = df['nom'].apply(parse_creative_name)
    df['usp'] = parsed.apply(lambda x: x['usp'])
    df['hook'] = parsed.apply(lambda x: x['hook'])
    df['format'] = parsed.apply(lambda x: x['format'])
    
    # Déterminer l'action recommandée
    df['action'] = df.apply(lambda r: determine_action(r, trends), axis=1)
    df['recommendation'] = df.apply(lambda r: generate_recommendation(r, trends), axis=1)
    
    return df


def determine_action(row, trends=None):
    """Détermine l'action recommandée pour une créative."""
    potential = row['scale_potential']
    conf = row['coefficient_confiance']
    freq = row.get('frequency', 2)
    roas = row.get('roas', 0)
    trend_score = row.get('trend_score', 0)
    
    # Règles de décision
    if trend_score < -30 or (freq > 4 and conf > 0.6):
        return 'pause'
    elif potential >= 60 and conf >= 0.7:
        return 'scale'
    elif conf < 0.6 and (roas > 5 or potential > 50):
        return 'test'
    elif freq > 3 or trend_score < -10:
        return 'monitor'
    else:
        return 'monitor'


def generate_recommendation(row, trends=None):
    """Génère une recommandation textuelle."""
    action = row['action']
    potential = row['scale_potential']
    freq = row.get('frequency', 2)
    roas = row.get('roas', 0)
    conf = row['coefficient_confiance']
    trend_score = row.get('trend_score', 0)
    
    if action == 'scale':
        pct = '+30%' if potential >= 70 else '+20%'
        trend_info = f" (tendance +{trend_score:.0f}%)" if trend_score > 10 else ""
        return f"Potentiel {potential}{trend_info} → Augmenter budget {pct}"
    elif action == 'pause':
        if trend_score < -30:
            return f"Tendance en chute ({trend_score:.0f}%) → Pauser"
        return f"Frequency trop élevée ({freq:.1f}) → Pauser"
    elif action == 'test':
        return f"ROAS {roas:.1f} prometteur, confiance {conf*100:.0f}% → Tester +50% budget"
    else:
        if freq > 3:
            return f"Frequency {freq:.1f} → Surveiller fatigue"
        if trend_score < -10:
            return f"Légère baisse ({trend_score:.0f}%) → À surveiller"
        return "Performances stables → Maintenir"


def create_sparkline_chart(sparkline_data, metric='ctr', height=60):
    """Crée un graphique sparkline avec Plotly."""
    if not sparkline_data:
        return None
    
    values = [d.get(metric, 0) for d in sparkline_data]
    dates = [d.get('date', '') for d in sparkline_data]
    
    # Calculer la tendance pour la couleur
    recent_avg = np.mean(values[-4:]) if len(values) >= 4 else np.mean(values)
    old_avg = np.mean(values[:4]) if len(values) >= 4 else np.mean(values)
    trend = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0
    
    color = '#10B981' if trend > 10 else '#EF4444' if trend < -10 else '#6B7280'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(values))),
        y=values,
        mode='lines+markers',
        line=dict(color=color, width=2),
        marker=dict(size=4, color=color),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False
    )
    
    return fig, trend


def get_grade(score):
    """Retourne le grade basé sur le score."""
    if score >= 85:
        return 'A', '🟢'
    elif score >= 70:
        return 'B', '🟢'
    elif score >= 55:
        return 'C', '🟡'
    elif score >= 40:
        return 'D', '🟠'
    else:
        return 'F', '🔴'


# ============================================================================
# INTERFACE UTILISATEUR
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Creative Intelligence Dashboard</h1>
        <p>Pilotage intelligent de vos créatives Meta Ads</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour upload
    with st.sidebar:
        st.header("📁 Import des données")
        
        # Mode d'import
        import_mode = st.radio(
            "Mode d'import",
            ["Données agrégées uniquement", "Agrégées + Quotidiennes (recommandé)"],
            help="Le mode quotidien permet d'avoir les tendances et sparklines"
        )
        
        st.divider()
        
        # Upload fichier principal (agrégé)
        st.subheader("1️⃣ Données agrégées")
        st.caption("Export Meta Ads sur la période complète")
        uploaded_main = st.file_uploader(
            "Fichier principal (période complète)",
            type=['csv'],
            key="main_file",
            help="Export CSV depuis Meta Ads Manager (30 derniers jours par exemple)"
        )
        
        if uploaded_main:
            st.success(f"✅ {uploaded_main.name}")
        
        # Upload fichier quotidien (optionnel)
        uploaded_daily = None
        if import_mode == "Agrégées + Quotidiennes (recommandé)":
            st.divider()
            st.subheader("2️⃣ Données quotidiennes")
            st.caption("Export Meta Ads jour par jour")
            uploaded_daily = st.file_uploader(
                "Fichier quotidien (jour par jour)",
                type=['csv'],
                key="daily_file",
                help="Export CSV avec une ligne par jour et par créative"
            )
            
            if uploaded_daily:
                st.success(f"✅ {uploaded_daily.name}")
            else:
                st.info("💡 Sans ce fichier, les tendances et sparklines ne seront pas disponibles")
        
        st.divider()
        
        st.header("⚙️ Paramètres")
        
        min_impressions = st.slider(
            "Impressions minimum",
            min_value=0,
            max_value=10000,
            value=500,
            step=100,
            help="Filtrer les créatives avec moins d'impressions"
        )
        
        st.divider()
        
        # Guide export
        with st.expander("📖 Comment exporter depuis Meta Ads"):
            st.markdown("""
            **Export agrégé (période complète) :**
            1. Meta Ads Manager → Niveau Publicité
            2. Sélectionner la période (ex: 30 jours)
            3. Ventilation : **Aucune**
            4. Exporter CSV
            
            **Export quotidien (jour par jour) :**
            1. Meta Ads Manager → Niveau Publicité
            2. Même période
            3. Ventilation : **Par jour**
            4. Exporter CSV
            """)
        
        st.divider()
        
        st.markdown("""
        **Légende des actions:**
        - 🚀 **Scaler** : Augmenter le budget
        - ⚡ **Tester** : Valider le potentiel
        - 👁️ **Surveiller** : À monitorer
        - ⏸️ **Pauser** : Couper le budget
        """)
    
    # Contenu principal
    if uploaded_main is None:
        # État initial - pas de fichier
        st.info("👈 Chargez votre export Meta Ads dans la barre latérale pour commencer l'analyse.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Export agrégé")
            st.markdown("""
            Un fichier avec les **totaux** sur la période :
            - 1 ligne par créative
            - Métriques cumulées (impressions, clics, achats...)
            - Indispensable pour l'analyse
            """)
        
        with col2:
            st.subheader("📈 Export quotidien")
            st.markdown("""
            Un fichier avec les **données jour par jour** :
            - 1 ligne par créative **par jour**
            - Permet de calculer les **tendances**
            - Active les **sparklines** 📊
            """)
        
        st.divider()
        
        st.subheader("🎯 Fonctionnalités")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Actions du jour**\n\nRecommandations claires : scaler, tester, surveiller, pauser")
        with col2:
            st.markdown("**Angles créatifs**\n\nAnalyse par USP et Hook pour identifier vos meilleurs angles")
        with col3:
            st.markdown("**Tendances**\n\nÉvolution sur 7j vs 7j précédents pour anticiper")
        with col4:
            st.markdown("**Comparateur**\n\nComparez jusqu'à 4 créatives côte à côte")
        
        return
    
    # Charger les données
    try:
        df = load_and_process_data(uploaded_main)
        df = df[df['impressions'] >= min_impressions]
        
        if len(df) == 0:
            st.warning("⚠️ Aucune créative ne correspond aux critères de filtrage.")
            return
        
        # Charger les données quotidiennes si disponibles
        trends = {}
        sparklines = {}
        has_daily = False
        
        if uploaded_daily:
            try:
                df_daily = load_daily_data(uploaded_daily)
                trends, sparklines = calculate_trends_from_daily(df_daily)
                has_daily = len(trends) > 0
                if has_daily:
                    st.sidebar.success(f"📈 Tendances calculées pour {len(trends)} créatives")
            except Exception as e:
                st.sidebar.warning(f"⚠️ Erreur données quotidiennes: {str(e)}")
        
        # Calculer les scores
        df = calculate_scores(df, trends)
        
        if len(df) == 0:
            st.warning("⚠️ Impossible de calculer les scores. Vérifiez le format du fichier.")
            return
            
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {str(e)}")
        st.info("Vérifiez que votre fichier est bien un export CSV de Meta Ads Manager.")
        return
    
    # Indicateur de données quotidiennes
    if has_daily:
        st.success("✅ Données quotidiennes chargées - Tendances et sparklines activées")
    elif uploaded_daily is None and import_mode == "Agrégées + Quotidiennes (recommandé)":
        st.info("💡 Ajoutez le fichier quotidien pour activer les tendances et sparklines")
    
    # Tabs principaux
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Actions du jour",
        "📊 Angles créatifs", 
        "📈 Tableau détaillé",
        "⚖️ Comparateur"
    ])
    
    # ========== TAB 1: Actions du jour ==========
    with tab1:
        st.header("Actions du jour")
        st.markdown("*Vos décisions prioritaires pour aujourd'hui*")
        
        # Compteurs par action
        action_counts = df['action'].value_counts()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            count = action_counts.get('scale', 0)
            st.metric("🚀 À scaler", count, help="Créatives prêtes à recevoir plus de budget")
        with col2:
            count = action_counts.get('test', 0)
            st.metric("⚡ À tester", count, help="Potentiel à valider avec plus de volume")
        with col3:
            count = action_counts.get('monitor', 0)
            st.metric("👁️ À surveiller", count, help="Performances à monitorer")
        with col4:
            count = action_counts.get('pause', 0)
            st.metric("⏸️ À pauser", count, help="Créatives à couper")
        
        st.divider()
        
        # Sections par action
        col_left, col_right = st.columns(2)
        
        with col_left:
            # À scaler
            st.subheader("🚀 À scaler maintenant")
            scale_df = df[df['action'] == 'scale'].sort_values('scale_potential', ascending=False)
            
            if len(scale_df) > 0:
                for _, row in scale_df.iterrows():
                    trend_badge = ""
                    if has_daily and row['trend_signal'] == 'up':
                        trend_badge = f"<span class='trend-badge trend-up'>↗ +{row['trend_score']:.0f}%</span>"
                    elif has_daily and row['trend_signal'] == 'down':
                        trend_badge = f"<span class='trend-badge trend-down'>↘ {row['trend_score']:.0f}%</span>"
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="action-card scale-card">
                            <strong>{row['format']}</strong> | {row['nom'][:50]}... {trend_badge}
                            <br><small>{row['recommendation']}</small>
                            <br><small>ROAS: {row['roas']:.1f} | CTR: {row['ctr_lien']:.2f}% | Potentiel: {row['scale_potential']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Sparkline si disponible
                        if has_daily and row['nom'] in sparklines:
                            fig, trend = create_sparkline_chart(sparklines[row['nom']], metric='ctr', height=40)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True, key=f"spark_scale_{row['nom'][:20]}")
            else:
                st.info("Aucune créative prête à scaler")
            
            # À surveiller
            st.subheader("👁️ À surveiller")
            monitor_df = df[df['action'] == 'monitor'].sort_values('scale_potential', ascending=False).head(5)
            
            for _, row in monitor_df.iterrows():
                trend_badge = ""
                if has_daily:
                    if row['trend_signal'] == 'up':
                        trend_badge = f"<span class='trend-badge trend-up'>↗ +{row['trend_score']:.0f}%</span>"
                    elif row['trend_signal'] == 'down':
                        trend_badge = f"<span class='trend-badge trend-down'>↘ {row['trend_score']:.0f}%</span>"
                    else:
                        trend_badge = f"<span class='trend-badge trend-stable'>→ stable</span>"
                
                with st.container():
                    st.markdown(f"""
                    <div class="action-card monitor-card">
                        <strong>{row['format']}</strong> | {row['nom'][:50]}... {trend_badge}
                        <br><small>{row['recommendation']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_right:
            # À tester
            st.subheader("⚡ À tester (potentiel à valider)")
            test_df = df[df['action'] == 'test'].sort_values('roas', ascending=False)
            
            if len(test_df) > 0:
                for _, row in test_df.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="action-card test-card">
                            <strong>{row['format']}</strong> | {row['nom'][:50]}...
                            <br><small>{row['recommendation']}</small>
                            <br><small>ROAS: {row['roas']:.1f} | Confiance: {row['coefficient_confiance']*100:.0f}%</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Aucune créative à tester")
            
            # À pauser
            st.subheader("⏸️ À pauser")
            pause_df = df[df['action'] == 'pause']
            
            if len(pause_df) > 0:
                for _, row in pause_df.iterrows():
                    trend_badge = ""
                    if has_daily and row['trend_score'] < -20:
                        trend_badge = f"<span class='trend-badge trend-down'>↘ {row['trend_score']:.0f}%</span>"
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="action-card pause-card">
                            <strong>{row['format']}</strong> | {row['nom'][:50]}... {trend_badge}
                            <br><small>{row['recommendation']}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("✅ Aucune créative à pauser")
    
    # ========== TAB 2: Angles créatifs ==========
    with tab2:
        st.header("Analyse par angle créatif")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Performance par USP")
            
            usp_stats = df.groupby('usp').agg({
                'nom': 'count',
                'depense': 'sum',
                'achats': 'sum',
                'roas': 'mean',
                'ctr_lien': 'mean',
                'scale_potential': 'mean'
            }).round(2)
            usp_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS moy', 'CTR moy %', 'Potentiel']
            usp_stats = usp_stats.sort_values('Potentiel', ascending=False)
            
            st.dataframe(usp_stats, use_container_width=True)
            
            # Graphique
            fig = px.bar(
                usp_stats.reset_index(),
                x='usp',
                y='Potentiel',
                color='Potentiel',
                color_continuous_scale='Greens',
                title="Potentiel moyen par USP"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎣 Performance par Hook")
            
            hook_stats = df.groupby('hook').agg({
                'nom': 'count',
                'depense': 'sum',
                'achats': 'sum',
                'roas': 'mean',
                'ctr_lien': 'mean',
                'scale_potential': 'mean'
            }).round(2)
            hook_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS moy', 'CTR moy %', 'Potentiel']
            hook_stats = hook_stats.sort_values('Potentiel', ascending=False)
            
            st.dataframe(hook_stats, use_container_width=True)
            
            # Graphique
            fig = px.bar(
                hook_stats.reset_index(),
                x='hook',
                y='CTR moy %',
                color='ROAS moy',
                color_continuous_scale='Blues',
                title="CTR moyen par Hook"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Matrice USP x Hook
        st.divider()
        st.subheader("🎯 Matrice USP × Hook")
        
        matrix = df.pivot_table(
            values='scale_potential',
            index='usp',
            columns='hook',
            aggfunc='mean'
        ).round(0)
        
        fig = px.imshow(
            matrix,
            labels=dict(x="Hook", y="USP", color="Potentiel"),
            color_continuous_scale='RdYlGn',
            aspect='auto'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.divider()
        st.subheader("💡 Insights stratégiques")
        
        best_usp = usp_stats.index[0] if len(usp_stats) > 0 else "N/A"
        best_hook = hook_stats.index[0] if len(hook_stats) > 0 else "N/A"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**USP gagnante:** {best_usp}")
        with col2:
            st.info(f"**Hook efficace:** {best_hook}")
        with col3:
            st.success(f"**Recommandation:** Créer plus de variations {best_usp} + {best_hook}")
    
    # ========== TAB 3: Tableau détaillé ==========
    with tab3:
        st.header("Tableau détaillé")
        
        # Filtres
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            format_filter = st.multiselect(
                "Format",
                options=df['format'].unique(),
                default=list(df['format'].unique())
            )
        with col2:
            action_filter = st.multiselect(
                "Action",
                options=df['action'].unique(),
                default=list(df['action'].unique())
            )
        with col3:
            sort_by = st.selectbox(
                "Trier par",
                options=['scale_potential', 'score_global_ajuste', 'roas', 'ctr_lien', 'depense', 'trend_score'],
                format_func=lambda x: {
                    'scale_potential': 'Potentiel',
                    'score_global_ajuste': 'Score global',
                    'roas': 'ROAS',
                    'ctr_lien': 'CTR',
                    'depense': 'Dépense',
                    'trend_score': 'Tendance'
                }.get(x, x)
            )
        with col4:
            sort_order = st.radio("Ordre", ["Décroissant", "Croissant"], horizontal=True)
        
        # Filtrer
        filtered_df = df[
            (df['format'].isin(format_filter)) &
            (df['action'].isin(action_filter))
        ].sort_values(sort_by, ascending=(sort_order == "Croissant"))
        
        st.caption(f"{len(filtered_df)} créatives affichées")
        
        # Afficher avec sparklines si disponibles
        for idx, row in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{row['format']}**")
                
                with col2:
                    st.markdown(f"{row['nom'][:45]}...")
                    st.caption(f"{row['usp']} • {row['hook']}")
                
                with col3:
                    if has_daily and row['nom'] in sparklines:
                        fig, trend = create_sparkline_chart(sparklines[row['nom']], metric='ctr', height=50)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True, key=f"spark_table_{idx}")
                        trend_color = "green" if trend > 10 else "red" if trend < -10 else "gray"
                        st.markdown(f"<small style='color:{trend_color}'>{trend:+.0f}%</small>", unsafe_allow_html=True)
                    else:
                        st.caption("Pas de données")
                
                with col4:
                    st.metric("CTR", f"{row['ctr_lien']:.2f}%")
                
                with col5:
                    roas_val = f"{row['roas']:.1f}" if row['roas'] > 0 else "-"
                    st.metric("ROAS", roas_val)
                
                with col6:
                    action_icons = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
                    st.metric("Potentiel", f"{row['scale_potential']} {action_icons.get(row['action'], '')}")
                
                st.divider()
        
        # Export
        st.download_button(
            label="📥 Exporter les résultats (CSV)",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name=f"meta_ads_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime='text/csv'
        )
    
    # ========== TAB 4: Comparateur ==========
    with tab4:
        st.header("Comparateur de créatives")
        
        # Sélection des créatives à comparer
        options = df['nom'].tolist()
        selected = st.multiselect(
            "Sélectionnez 2 à 4 créatives à comparer",
            options=options,
            max_selections=4,
            format_func=lambda x: f"{df[df['nom']==x]['format'].values[0]} | {x[:50]}..."
        )
        
        if len(selected) >= 2:
            compare_df = df[df['nom'].isin(selected)]
            
            # Sparklines comparatives
            if has_daily:
                st.subheader("📈 Évolution CTR sur 14 jours")
                
                fig = go.Figure()
                for nom in selected:
                    if nom in sparklines:
                        values = [d.get('ctr', 0) for d in sparklines[nom]]
                        fig.add_trace(go.Scatter(
                            x=list(range(len(values))),
                            y=values,
                            mode='lines+markers',
                            name=nom[:30] + '...',
                            line=dict(width=2)
                        ))
                
                fig.update_layout(
                    height=300,
                    xaxis_title="Jour",
                    yaxis_title="CTR %",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Métriques à comparer
            st.subheader("📊 Comparaison des métriques")
            
            metrics = [
                ('impressions', 'Impressions', True),
                ('clics_lien', 'Clics', True),
                ('ctr_lien', 'CTR %', True),
                ('cpc_lien', 'CPC €', False),
                ('cpm', 'CPM €', False),
                ('achats', 'Achats', True),
                ('roas', 'ROAS', True),
                ('frequency', 'Frequency', False),
                ('coefficient_confiance', 'Confiance', True),
                ('scale_potential', 'Potentiel', True),
            ]
            
            if has_daily:
                metrics.append(('trend_score', 'Tendance 7j', True))
            
            # Créer le tableau de comparaison
            comparison_data = []
            for metric, label, higher_better in metrics:
                row = {'Métrique': label}
                values = []
                for nom in selected:
                    val = compare_df[compare_df['nom'] == nom][metric].values[0]
                    values.append(val)
                    short_name = nom[:25] + '...'
                    row[short_name] = round(val, 2) if isinstance(val, float) else val
                
                comparison_data.append(row)
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            # Graphique radar
            st.subheader("🎯 Visualisation comparative")
            
            radar_metrics = ['ctr_lien', 'scale_potential', 'coefficient_confiance']
            if has_daily:
                radar_metrics.append('trend_score')
            if df['roas'].max() > 0:
                radar_metrics.insert(1, 'roas')
            
            radar_labels = {
                'ctr_lien': 'CTR',
                'roas': 'ROAS',
                'scale_potential': 'Potentiel',
                'coefficient_confiance': 'Confiance',
                'trend_score': 'Tendance'
            }
            
            fig = go.Figure()
            
            for nom in selected:
                row = compare_df[compare_df['nom'] == nom].iloc[0]
                values = []
                for m in radar_metrics:
                    max_val = df[m].max() if df[m].max() > 0 else 1
                    if m == 'trend_score':
                        # Normaliser tendance entre 0 et 100
                        val = (row[m] + 100) / 2  # -100 à +100 devient 0 à 100
                    elif m == 'coefficient_confiance':
                        val = row[m] * 100
                    else:
                        val = (row[m] / max_val) * 100
                    values.append(val)
                values.append(values[0])  # Fermer le polygone
                
                labels = [radar_labels.get(m, m) for m in radar_metrics] + [radar_labels.get(radar_metrics[0], radar_metrics[0])]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    name=nom[:30] + '...',
                    fill='toself',
                    opacity=0.6
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Verdict
            st.subheader("🏆 Verdict")
            winner = compare_df.sort_values('scale_potential', ascending=False).iloc[0]
            st.success(f"**Meilleur potentiel de scale :** {winner['format']} | {winner['nom'][:50]}... (Potentiel: {winner['scale_potential']})")
        
        else:
            st.info("👆 Sélectionnez au moins 2 créatives pour les comparer")


if __name__ == "__main__":
    main()
