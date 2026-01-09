"""
Meta Ads Creative Intelligence Dashboard V2.2
=============================================
Application de pilotage des créatives publicitaires Meta Ads.
Avec tableau amélioré : scores détaillés, grades, tendances, sparklines.

Installation:
    pip install streamlit pandas numpy plotly

Lancement:
    streamlit run meta_ads_dashboard.py

Auteur: BNB Solutions Digitales
Version: 2.2
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import json
import re

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
    
    /* Custom table styles */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin-top: 1rem;
    }
    .custom-table th {
        background: #F8FAFC;
        padding: 12px 8px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #E5E7EB;
        white-space: nowrap;
        position: sticky;
        top: 0;
    }
    .custom-table td {
        padding: 10px 8px;
        border-bottom: 1px solid #F3F4F6;
        vertical-align: middle;
    }
    .custom-table tr:hover {
        background: #F8FAFC !important;
    }
    .custom-table .action-badge {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-scale { background: #D1FAE5; color: #065F46; }
    .badge-test { background: #DBEAFE; color: #1E40AF; }
    .badge-monitor { background: #FEF3C7; color: #92400E; }
    .badge-pause { background: #FEE2E2; color: #991B1B; }
    
    .format-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .format-img { background: #DBEAFE; color: #1E40AF; }
    .format-vid { background: #E0E7FF; color: #3730A3; }
    .format-gif { background: #D1FAE5; color: #065F46; }
    .format-car { background: #FEF3C7; color: #92400E; }
    
    .score-cell {
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
    }
    .score-bar {
        width: 50px;
        height: 8px;
        background: #E5E7EB;
        border-radius: 4px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
    }
    .grade-badge {
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
        color: white;
    }
    .var-positive { color: #065F46; font-size: 11px; }
    .var-negative { color: #991B1B; font-size: 11px; }
    .var-neutral { color: #6B7280; font-size: 11px; }
    
    .table-container {
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# FONCTIONS DE TRAITEMENT
# ============================================================================

def find_column(df, possible_names):
    """Trouve une colonne parmi plusieurs noms possibles."""
    for name in possible_names:
        if name in df.columns:
            return name
        for col in df.columns:
            if col.lower() == name.lower():
                return col
            if name.lower() in col.lower():
                return col
    return None


def standardize_columns(df):
    """Standardise les noms de colonnes du CSV Meta Ads."""
    
    column_mappings = {
        'nom': ['Nom de la publicité', 'Ad name', 'nom_publicite', 'nom', 'Nom de la pub'],
        'impressions': ['Impressions', 'impressions'],
        'reach': ['Couverture', 'Reach', 'reach', 'couverture'],
        'clics_lien': ['Clics sur un lien', 'Link clicks', 'clics_lien', 'Clics sur le lien'],
        'clics_tous': ['Clics (tous)', 'Clicks (all)', 'clics_tous'],
        'ctr_lien': ['CTR unique (taux de clics sur le lien)', 'CTR (taux de clics sur le lien)', 
                     'Link click-through rate', 'ctr_lien', 'CTR (lien)', 'ctr_unique_lien'],
        'ctr_tous': ['CTR (tous)', 'CTR (all)', 'ctr_tous'],
        'cpc_lien': ['CPC (coût par clic sur un lien) (EUR)', 'CPC (coût par clic sur un lien)',
                     'Cost per link click', 'cpc_lien'],
        'cpc_tous': ['CPC (Tous) (EUR)', 'CPC (tous)', 'CPC (All)', 'cpc_tous'],
        'cpm': ['CPM (Coût pour 1 000 impressions) (EUR)', 'CPM (Coût pour 1 000 impressions)',
                'CPM (cost per 1,000 impressions)', 'cpm', 'CPM'],
        'depense': ['Montant dépensé (EUR)', 'Montant dépensé', 'Amount spent', 'depense', 
                    'montant_depense'],
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
    
    rename_dict = {}
    for standard_name, possible_names in column_mappings.items():
        found_col = find_column(df, possible_names)
        if found_col and found_col != standard_name:
            rename_dict[found_col] = standard_name
    
    df = df.rename(columns=rename_dict)
    return df


def clean_numeric(value):
    """Nettoie une valeur numérique."""
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip().replace(' ', '').replace(',', '.')
        value = re.sub(r'[^\d.\-]', '', value)
        try:
            return float(value) if value else 0
        except:
            return 0
    return 0


@st.cache_data
def load_and_process_data(uploaded_file):
    """Charge et traite le fichier CSV exporté de Meta Ads."""
    
    df = pd.read_csv(uploaded_file)
    df = standardize_columns(df)
    
    numeric_cols = ['impressions', 'reach', 'clics_lien', 'clics_tous', 'ctr_lien', 'ctr_tous',
                    'cpc_lien', 'cpc_tous', 'cpm', 'depense', 'achats', 'valeur_achats', 'roas', 
                    'cpa', 'frequency', 'ajouts_panier']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)
    
    default_cols = {
        'valeur_achats': 0, 'achats': 0, 'roas': 0, 'ajouts_panier': 0, 'cpa': 0,
        'cpm': 0, 'cpc_lien': 0, 'ctr_lien': 0, 'clics_lien': 0, 'frequency': 1
    }
    
    for col, default in default_cols.items():
        if col not in df.columns:
            df[col] = default
    
    if df['clics_lien'].sum() == 0 and 'clics_tous' in df.columns:
        df['clics_lien'] = df['clics_tous']
    
    if df['ctr_lien'].sum() == 0 and 'ctr_tous' in df.columns:
        df['ctr_lien'] = df['ctr_tous']
    
    if df['cpc_lien'].sum() == 0 and 'cpc_tous' in df.columns:
        df['cpc_lien'] = df['cpc_tous']
    
    if df['frequency'].sum() == 0:
        df['frequency'] = np.where(df['reach'] > 0, df['impressions'] / df['reach'], 1)
    
    if 'nom' in df.columns:
        df = df[df['nom'].notna() & (df['nom'] != '')]
    
    return df


@st.cache_data
def load_daily_data(uploaded_file):
    """Charge les données quotidiennes pour les tendances et sparklines."""
    
    df = pd.read_csv(uploaded_file)
    df = standardize_columns(df)
    
    numeric_cols = ['impressions', 'reach', 'clics_lien', 'ctr_lien', 'cpc_lien', 
                    'cpm', 'depense', 'achats']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)
    
    if 'date_debut' in df.columns:
        df['date'] = pd.to_datetime(df['date_debut'], dayfirst=True, errors='coerce')
    
    return df


def calculate_trends_from_daily(df_daily, lookback_days=14):
    """Calcule les tendances à partir des données quotidiennes."""
    
    if df_daily is None or len(df_daily) == 0 or 'date' not in df_daily.columns:
        return {}, {}
    
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
        df_14j = df_crea[df_crea['date'] >= date_14j]
        
        sparkline_data = []
        dates = pd.date_range(start=date_14j, end=date_max, freq='D')
        
        for d in dates:
            row = df_14j[df_14j['date'].dt.date == d.date()]
            if len(row) > 0 and row.iloc[0].get('impressions', 0) > 0:
                sparkline_data.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'impressions': float(row.iloc[0].get('impressions', 0)),
                    'ctr': float(row.iloc[0].get('ctr_lien', 0)),
                    'depense': float(row.iloc[0].get('depense', 0)),
                    'cpm': float(row.iloc[0].get('cpm', 0))
                })
            else:
                sparkline_data.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'impressions': 0, 'ctr': 0, 'depense': 0, 'cpm': 0
                })
        
        sparklines[nom] = sparkline_data
        
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
        
        trend_score = (
            0.40 * trend_ctr +
            0.25 * (-trend_cpc) +
            0.20 * (-trend_cpm) +
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
    
    if not isinstance(nom, str):
        return {'usp': 'Autre', 'hook': 'Autre', 'format': 'IMG'}
    
    usp = 'Autre'
    hook = 'Autre'
    format_type = 'IMG'
    
    nom_upper = nom.upper()
    if nom_upper.startswith('IMG'):
        format_type = 'IMG'
    elif nom_upper.startswith('VID'):
        format_type = 'VID'
    elif nom_upper.startswith('GIF'):
        format_type = 'GIF'
    elif nom_upper.startswith('CAR'):
        format_type = 'CAR'
    
    usp_match = re.search(r'USP\s*:\s*([^-]+)', nom, re.IGNORECASE)
    if usp_match:
        usp = usp_match.group(1).strip()
    elif 'Nouvelle collection' in nom:
        usp = 'Nouvelle collection'
    
    nom_lower = nom.lower()
    if 'probleme/solution' in nom_lower or 'problème/solution' in nom_lower:
        hook = 'Problème/Solution'
    elif 'probleme/frustation' in nom_lower or 'problème/frustration' in nom_lower:
        hook = 'Problème/Frustration'
    elif ' pv ' in nom_lower or nom_lower.startswith('pv ') or ' - pv -' in nom_lower or '--pv--' in nom_lower:
        hook = 'Proposition de Valeur'
    elif 'produit neutre' in nom_lower:
        hook = 'Produit neutre'
    
    return {'usp': usp, 'hook': hook, 'format': format_type}


def calculate_confidence(row):
    """Calcule le coefficient de confiance basé sur le volume."""
    impressions = row.get('impressions', 0)
    achats = row.get('achats', 0)
    clics = row.get('clics_lien', 0)
    
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
    
    if achats < 5:
        score_conv = 0.4
    elif achats < 15:
        score_conv = 0.6
    elif achats < 30:
        score_conv = 0.8
    else:
        score_conv = 1.0
    
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
    
    potential = (
        0.25 * perf_score +
        0.25 * trend_component +
        0.20 * freq_score +
        0.15 * (100 - min(abs(row.get('trend_cpm', 0)), 100)) +
        0.15 * conf_score
    )
    
    return round(potential)


def get_grade(score):
    """Retourne le grade et la couleur basés sur le score."""
    if score >= 70:
        return 'A', '#10B981'  # Vert
    elif score >= 60:
        return 'B', '#34D399'  # Vert clair
    elif score >= 50:
        return 'C', '#FBBF24'  # Jaune/Orange
    elif score >= 40:
        return 'D', '#F97316'  # Orange
    else:
        return 'F', '#EF4444'  # Rouge


def get_bar_color(score):
    """Retourne la couleur de la barre basée sur le score."""
    if score >= 70:
        return '#10B981'  # Vert
    elif score >= 60:
        return '#34D399'  # Vert clair
    elif score >= 50:
        return '#FBBF24'  # Jaune
    elif score >= 40:
        return '#F97316'  # Orange
    else:
        return '#EF4444'  # Rouge


def calculate_scores(df, trends=None):
    """Calcule les scores pour chaque créative."""
    
    df = df[df['impressions'] >= 500].copy()
    
    if len(df) == 0:
        return df
    
    def calc_stats(values):
        valid = values[values > 0]
        if len(valid) == 0:
            return 0, 1
        return valid.mean(), valid.std() if valid.std() > 0 else 1
    
    def z_score(value, mean, std, inverse=False):
        if pd.isna(value) or value == 0:
            return 0
        z = (value - mean) / std
        return -z if inverse else z
    
    roas_mean, roas_std = calc_stats(df['roas'])
    ctr_mean, ctr_std = calc_stats(df['ctr_lien'])
    cpc_mean, cpc_std = calc_stats(df['cpc_lien'])
    cpm_mean, cpm_std = calc_stats(df['cpm'])
    reach_mean, reach_std = calc_stats(df['reach'])
    clics_mean, clics_std = calc_stats(df['clics_lien'])
    
    df['cvr'] = np.where(df['clics_lien'] > 0, 
                         (df['achats'] / df['clics_lien']) * 100, 0)
    cvr_mean, cvr_std = calc_stats(df['cvr'])
    
    df['cpa_calc'] = np.where(df['achats'] > 0, df['depense'] / df['achats'], 0)
    valid_cpa = df[df['cpa_calc'] > 0]['cpa_calc']
    cpa_mean = valid_cpa.mean() if len(valid_cpa) > 0 else df['depense'].mean()
    cpa_std = valid_cpa.std() if len(valid_cpa) > 0 and valid_cpa.std() > 0 else 1
    
    scores_data = []
    for idx, row in df.iterrows():
        z_roas = z_score(row['roas'], roas_mean, roas_std)
        z_cpa = z_score(row['cpa_calc'] if row['cpa_calc'] > 0 else cpa_mean * 2, cpa_mean, cpa_std, inverse=True)
        z_cvr = z_score(row['cvr'], cvr_mean, cvr_std)
        z_ctr = z_score(row['ctr_lien'], ctr_mean, ctr_std)
        z_cpc = z_score(row['cpc_lien'], cpc_mean, cpc_std, inverse=True)
        z_cpm = z_score(row['cpm'], cpm_mean, cpm_std, inverse=True)
        z_reach = z_score(row['reach'], reach_mean, reach_std)
        z_clics = z_score(row['clics_lien'], clics_mean, clics_std)
        
        def z_to_100(z):
            return max(0, min(100, 50 + z * 10))
        
        score_profit = round(z_to_100(0.45 * z_roas + 0.35 * z_cpa + 0.20 * z_cvr))
        score_trafic = round(z_to_100(0.50 * z_ctr + 0.30 * z_cpc + 0.20 * z_clics))
        score_notoriete = round(z_to_100(0.40 * z_cpm + 0.60 * z_reach))
        score_global = round((score_profit + score_trafic + score_notoriete) / 3)
        
        coef_conf = calculate_confidence(row)
        score_global_ajuste = round(score_global * coef_conf + 50 * (1 - coef_conf))
        
        trend_data = trends.get(row['nom'], {}) if trends else {}
        trend_score = trend_data.get('score', 0)
        trend_signal = trend_data.get('signal', 'stable')
        trend_ctr = trend_data.get('ctr', 0)
        trend_cpm = trend_data.get('cpm', 0)
        
        row_dict = row.to_dict()
        row_dict['trend_cpm'] = trend_cpm
        
        potential = calculate_scale_potential(row_dict, score_global_ajuste, coef_conf, trend_score)
        
        # Calcul des variations basées sur les tendances
        var_profit = round(trend_score * 0.15) if trend_score != 0 else 0
        var_trafic = round(trend_ctr * 0.3) if trend_ctr != 0 else 0
        var_notoriete = round(-trend_cpm * 0.2) if trend_cpm != 0 else 0
        var_global = round((var_profit + var_trafic + var_notoriete) / 3)
        
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
            'trend_cpm': trend_cpm,
            'var_profit': var_profit,
            'var_trafic': var_trafic,
            'var_notoriete': var_notoriete,
            'var_global': var_global,
        })
    
    scores_df = pd.DataFrame(scores_data)
    for col in scores_df.columns:
        df[col] = scores_df[col].values
    
    parsed = df['nom'].apply(parse_creative_name)
    df['usp'] = parsed.apply(lambda x: x['usp'])
    df['hook'] = parsed.apply(lambda x: x['hook'])
    df['format'] = parsed.apply(lambda x: x['format'])
    
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


def render_score_cell_html(score, variation=0):
    """Génère le HTML pour une cellule de score avec barre, grade et variation."""
    grade, grade_color = get_grade(score)
    bar_color = get_bar_color(score)
    
    # Variation HTML
    if variation > 0:
        var_html = f'<span class="var-positive">(+{variation})</span>'
    elif variation < 0:
        var_html = f'<span class="var-negative">({variation})</span>'
    else:
        var_html = ''
    
    html = f'''
    <div class="score-cell">
        <div class="score-bar">
            <div class="score-bar-fill" style="width: {score}%; background: {bar_color};"></div>
        </div>
        <span style="font-weight: 600; min-width: 20px;">{score}</span>
        <span class="grade-badge" style="background: {grade_color};">{grade}</span>
        {var_html}
    </div>
    '''
    return html


def render_sparkline_svg(sparkline_data, width=70, height=20):
    """Génère un SVG pour sparkline."""
    if not sparkline_data:
        return '<span style="color: #9CA3AF; font-size: 11px;">-</span>'
    
    values = [d.get('ctr', 0) for d in sparkline_data]
    if max(values) == 0:
        return '<span style="color: #9CA3AF; font-size: 11px;">-</span>'
    
    max_val = max(values) if max(values) > 0 else 1
    min_val = min([v for v in values if v > 0]) if any(v > 0 for v in values) else 0
    range_val = max_val - min_val if max_val > min_val else 1
    
    # Calculer tendance
    recent_avg = np.mean(values[-4:]) if len(values) >= 4 else np.mean(values)
    old_avg = np.mean(values[:4]) if len(values) >= 4 else np.mean(values)
    trend = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0
    
    color = '#10B981' if trend > 10 else '#EF4444' if trend < -10 else '#6B7280'
    
    # Générer les points
    points = []
    for i, v in enumerate(values):
        x = (i / (len(values) - 1)) * width if len(values) > 1 else width / 2
        y = height - ((v - min_val) / range_val * (height - 4)) - 2 if range_val > 0 else height / 2
        points.append(f"{x:.1f},{y:.1f}")
    
    points_str = ' '.join(points)
    
    trend_text = f"+{trend:.0f}%" if trend > 0 else f"{trend:.0f}%"
    trend_color = '#10B981' if trend > 10 else '#EF4444' if trend < -10 else '#6B7280'
    
    svg = f'''
    <div style="display: flex; align-items: center; gap: 6px;">
        <svg width="{width}" height="{height}" style="overflow: visible;">
            <polyline points="{points_str}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span style="color: {trend_color}; font-size: 11px; font-weight: 600;">{trend_text}</span>
    </div>
    '''
    return svg


def create_sparkline_chart(sparkline_data, metric='ctr', height=60):
    """Crée un graphique sparkline avec Plotly."""
    if not sparkline_data:
        return None, 0
    
    values = [d.get(metric, 0) for d in sparkline_data]
    
    non_zero = [v for v in values if v > 0]
    if len(non_zero) >= 2:
        recent_avg = np.mean(values[-4:]) if len(values) >= 4 else np.mean(values)
        old_avg = np.mean(values[:4]) if len(values) >= 4 else np.mean(values)
        trend = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0
    else:
        trend = 0
    
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
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Import des données")
        
        import_mode = st.radio(
            "Mode d'import",
            ["Données agrégées uniquement", "Agrégées + Quotidiennes (recommandé)"],
            help="Le mode quotidien permet d'avoir les tendances et sparklines"
        )
        
        st.divider()
        
        st.subheader("1️⃣ Données agrégées")
        st.caption("Export Meta Ads sur la période complète")
        uploaded_main = st.file_uploader(
            "Fichier principal (période complète)",
            type=['csv'],
            key="main_file"
        )
        
        if uploaded_main:
            st.success(f"✅ {uploaded_main.name}")
        
        uploaded_daily = None
        if import_mode == "Agrégées + Quotidiennes (recommandé)":
            st.divider()
            st.subheader("2️⃣ Données quotidiennes")
            st.caption("Export Meta Ads jour par jour")
            uploaded_daily = st.file_uploader(
                "Fichier quotidien (jour par jour)",
                type=['csv'],
                key="daily_file"
            )
            
            if uploaded_daily:
                st.success(f"✅ {uploaded_daily.name}")
            else:
                st.info("💡 Sans ce fichier, pas de tendances")
        
        st.divider()
        st.header("⚙️ Paramètres")
        
        min_impressions = st.slider(
            "Impressions minimum",
            min_value=0,
            max_value=10000,
            value=500,
            step=100
        )
        
        st.divider()
        
        with st.expander("📖 Guide export Meta Ads"):
            st.markdown("""
            **Export agrégé :**
            1. Meta Ads Manager → Publicité
            2. Période : 30 jours
            3. Ventilation : **Aucune**
            4. Exporter CSV
            
            **Export quotidien :**
            - Même chose mais Ventilation : **Par jour**
            """)
        
        st.divider()
        st.markdown("""
        **Légende:**
        - 🚀 Scaler
        - ⚡ Tester
        - 👁️ Surveiller
        - ⏸️ Pauser
        """)
    
    # Page principale
    if uploaded_main is None:
        st.info("👈 Chargez votre export Meta Ads pour commencer.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Export agrégé")
            st.markdown("Fichier avec les **totaux** (1 ligne/créative)")
        with col2:
            st.subheader("📈 Export quotidien")
            st.markdown("Fichier **jour par jour** pour les tendances")
        return
    
    # Charger les données
    try:
        df = load_and_process_data(uploaded_main)
        df = df[df['impressions'] >= min_impressions]
        
        if len(df) == 0:
            st.warning("⚠️ Aucune créative ne correspond aux filtres.")
            return
        
        trends = {}
        sparklines = {}
        has_daily = False
        
        if uploaded_daily:
            try:
                df_daily = load_daily_data(uploaded_daily)
                trends, sparklines = calculate_trends_from_daily(df_daily)
                has_daily = len(trends) > 0
                if has_daily:
                    st.sidebar.success(f"📈 {len(trends)} tendances calculées")
            except Exception as e:
                st.sidebar.warning(f"⚠️ Erreur: {str(e)}")
        
        df = calculate_scores(df, trends)
        
        if len(df) == 0:
            st.warning("⚠️ Aucune créative avec assez d'impressions.")
            return
            
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    if has_daily:
        st.success("✅ Données quotidiennes chargées - Tendances et sparklines activées")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Actions du jour",
        "📊 Angles créatifs", 
        "📈 Tableau détaillé",
        "⚖️ Comparateur"
    ])
    
    # ========== TAB 1: Actions du jour ==========
    with tab1:
        st.header("Actions du jour")
        
        action_counts = df['action'].value_counts()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚀 À scaler", action_counts.get('scale', 0))
        with col2:
            st.metric("⚡ À tester", action_counts.get('test', 0))
        with col3:
            st.metric("👁️ À surveiller", action_counts.get('monitor', 0))
        with col4:
            st.metric("⏸️ À pauser", action_counts.get('pause', 0))
        
        st.divider()
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🚀 À scaler")
            scale_df = df[df['action'] == 'scale'].sort_values('scale_potential', ascending=False)
            
            if len(scale_df) > 0:
                for _, row in scale_df.iterrows():
                    trend_badge = ""
                    if has_daily:
                        if row['trend_signal'] == 'up':
                            trend_badge = f"<span class='trend-badge trend-up'>↗ +{row['trend_score']:.0f}%</span>"
                        elif row['trend_signal'] == 'down':
                            trend_badge = f"<span class='trend-badge trend-down'>↘ {row['trend_score']:.0f}%</span>"
                    
                    st.markdown(f"""
                    <div class="action-card scale-card">
                        <strong>{row['format']}</strong> | {row['nom'][:45]}... {trend_badge}
                        <br><small>{row['recommendation']}</small>
                        <br><small>ROAS: {row['roas']:.1f} | CTR: {row['ctr_lien']:.2f}% | Potentiel: {row['scale_potential']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucune créative prête à scaler")
            
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
                        trend_badge = f"<span class='trend-badge trend-stable'>→</span>"
                
                st.markdown(f"""
                <div class="action-card monitor-card">
                    <strong>{row['format']}</strong> | {row['nom'][:45]}... {trend_badge}
                    <br><small>{row['recommendation']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col_right:
            st.subheader("⚡ À tester")
            test_df = df[df['action'] == 'test'].sort_values('roas', ascending=False)
            
            if len(test_df) > 0:
                for _, row in test_df.iterrows():
                    st.markdown(f"""
                    <div class="action-card test-card">
                        <strong>{row['format']}</strong> | {row['nom'][:45]}...
                        <br><small>{row['recommendation']}</small>
                        <br><small>ROAS: {row['roas']:.1f} | Confiance: {row['coefficient_confiance']*100:.0f}%</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucune créative à tester")
            
            st.subheader("⏸️ À pauser")
            pause_df = df[df['action'] == 'pause']
            
            if len(pause_df) > 0:
                for _, row in pause_df.iterrows():
                    trend_badge = ""
                    if has_daily and row['trend_score'] < -20:
                        trend_badge = f"<span class='trend-badge trend-down'>↘ {row['trend_score']:.0f}%</span>"
                    
                    st.markdown(f"""
                    <div class="action-card pause-card">
                        <strong>{row['format']}</strong> | {row['nom'][:45]}... {trend_badge}
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
            st.subheader("📌 Par USP")
            usp_stats = df.groupby('usp').agg({
                'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean'
            }).round(2)
            usp_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel']
            usp_stats = usp_stats.sort_values('Potentiel', ascending=False)
            st.dataframe(usp_stats, use_container_width=True)
            
            if len(usp_stats) > 0:
                fig = px.bar(usp_stats.reset_index(), x='usp', y='Potentiel',
                           color='Potentiel', color_continuous_scale='Greens')
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎣 Par Hook")
            hook_stats = df.groupby('hook').agg({
                'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean'
            }).round(2)
            hook_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel']
            hook_stats = hook_stats.sort_values('Potentiel', ascending=False)
            st.dataframe(hook_stats, use_container_width=True)
            
            if len(hook_stats) > 0:
                fig = px.bar(hook_stats.reset_index(), x='hook', y='CTR %',
                           color='ROAS', color_continuous_scale='Blues')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        best_usp = usp_stats.index[0] if len(usp_stats) > 0 else "N/A"
        best_hook = hook_stats.index[0] if len(hook_stats) > 0 else "N/A"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**USP gagnante:** {best_usp}")
        with col2:
            st.info(f"**Hook efficace:** {best_hook}")
        with col3:
            st.success(f"**Combo:** {best_usp} + {best_hook}")
    
    # ========== TAB 3: Tableau détaillé ==========
    with tab3:
        st.header("Tableau détaillé")
        
        # Filtres
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            format_filter = st.multiselect("Format", options=df['format'].unique(), default=list(df['format'].unique()))
        with col2:
            action_filter = st.multiselect("Action", options=df['action'].unique(), default=list(df['action'].unique()))
        with col3:
            sort_by = st.selectbox("Trier par", options=['score_global', 'scale_potential', 'score_profitabilite', 'score_trafic', 'score_notoriete'],
                format_func=lambda x: {'score_global': '⭐ Global', 'scale_potential': 'Potentiel', 'score_profitabilite': '💰 Profit', 'score_trafic': '🚀 Trafic', 'score_notoriete': '👁️ Notoriété'}.get(x, x))
        with col4:
            sort_order = st.radio("Ordre", ["Décroissant", "Croissant"], horizontal=True)
        
        # Filtrer
        filtered_df = df[
            (df['format'].isin(format_filter)) &
            (df['action'].isin(action_filter))
        ].sort_values(sort_by, ascending=(sort_order == "Croissant"))
        
        st.caption(f"{len(filtered_df)} créatives affichées")
        
        # Générer le tableau HTML
        table_html = '''
        <div class="table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="width: 40px;">#</th>
                    <th style="width: 55px;">Format</th>
                    <th style="width: 200px;">Nom</th>
                    <th style="width: 100px;">Évolution</th>
                    <th style="width: 140px;">💰 Profit</th>
                    <th style="width: 140px;">🚀 Trafic</th>
                    <th style="width: 140px;">👁️ Notoriété</th>
                    <th style="width: 140px;">⭐ Global</th>
                    <th style="width: 70px;">Potentiel</th>
                    <th style="width: 70px;">Action</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for idx, (_, row) in enumerate(filtered_df.iterrows(), 1):
            # Format badge
            format_class = f"format-{row['format'].lower()}"
            
            # Action badge
            action_class = f"badge-{row['action']}"
            action_icons = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
            action_icon = action_icons.get(row['action'], '')
            
            # Sparkline
            sparkline_html = "-"
            if has_daily and row['nom'] in sparklines:
                sparkline_html = render_sparkline_svg(sparklines[row['nom']])
            
            # Scores avec grades et variations
            profit_html = render_score_cell_html(row['score_profitabilite'], row.get('var_profit', 0))
            trafic_html = render_score_cell_html(row['score_trafic'], row.get('var_trafic', 0))
            notoriete_html = render_score_cell_html(row['score_notoriete'], row.get('var_notoriete', 0))
            global_html = render_score_cell_html(row['score_global'], row.get('var_global', 0))
            
            # Potentiel avec barre
            pot_color = get_bar_color(row['scale_potential'])
            
            # Couleur de ligne selon action
            row_bg = {
                'scale': '#F0FDF4',
                'test': '#EFF6FF',
                'monitor': '#FFFBEB',
                'pause': '#FEF2F2'
            }.get(row['action'], '#FFFFFF')
            
            table_html += f'''
                <tr style="background-color: {row_bg};">
                    <td>{idx}</td>
                    <td><span class="format-badge {format_class}">{row['format']}</span></td>
                    <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{row['nom']}">{row['nom'][:35]}...</td>
                    <td>{sparkline_html}</td>
                    <td>{profit_html}</td>
                    <td>{trafic_html}</td>
                    <td>{notoriete_html}</td>
                    <td>{global_html}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <div style="width: 35px; height: 6px; background: #E5E7EB; border-radius: 3px; overflow: hidden;">
                                <div style="width: {row['scale_potential']}%; height: 100%; background: {pot_color};"></div>
                            </div>
                            <span style="font-weight: 600; font-size: 12px;">{row['scale_potential']}</span>
                        </div>
                    </td>
                    <td><span class="action-badge {action_class}">{action_icon}</span></td>
                </tr>
            '''
        
        table_html += '''
            </tbody>
        </table>
        </div>
        '''
        
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.divider()
        
        # Export
        st.download_button(
            "📥 Exporter CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name=f"meta_ads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime='text/csv'
        )
    
    # ========== TAB 4: Comparateur ==========
    with tab4:
        st.header("Comparateur")
        
        options = df['nom'].tolist()
        selected = st.multiselect(
            "Sélectionnez 2 à 4 créatives",
            options=options,
            max_selections=4,
            format_func=lambda x: f"{df[df['nom']==x]['format'].values[0]} | {x[:45]}..."
        )
        
        if len(selected) >= 2:
            compare_df = df[df['nom'].isin(selected)]
            
            if has_daily:
                st.subheader("📈 Évolution CTR")
                fig = go.Figure()
                for nom in selected:
                    if nom in sparklines:
                        values = [d.get('ctr', 0) for d in sparklines[nom]]
                        fig.add_trace(go.Scatter(
                            x=list(range(len(values))), y=values,
                            mode='lines+markers', name=nom[:25] + '...', line=dict(width=2)
                        ))
                fig.update_layout(height=250, xaxis_title="Jour", yaxis_title="CTR %")
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📊 Comparaison scores")
            
            score_data = []
            for nom in selected:
                row = compare_df[compare_df['nom'] == nom].iloc[0]
                score_data.append({
                    'Créative': nom[:30] + '...',
                    'Profit': f"{row['score_profitabilite']} ({get_grade(row['score_profitabilite'])[0]})",
                    'Trafic': f"{row['score_trafic']} ({get_grade(row['score_trafic'])[0]})",
                    'Notoriété': f"{row['score_notoriete']} ({get_grade(row['score_notoriete'])[0]})",
                    'Global': f"{row['score_global']} ({get_grade(row['score_global'])[0]})",
                    'Potentiel': row['scale_potential'],
                    'Action': row['action']
                })
            st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True)
            
            st.subheader("🎯 Radar")
            fig = go.Figure()
            for nom in selected:
                row = compare_df[compare_df['nom'] == nom].iloc[0]
                values = [row['score_profitabilite'], row['score_trafic'], row['score_notoriete'], row['scale_potential'], row['score_profitabilite']]
                fig.add_trace(go.Scatterpolar(
                    r=values, theta=['Profit', 'Trafic', 'Notoriété', 'Potentiel', 'Profit'],
                    name=nom[:25] + '...', fill='toself', opacity=0.6
                ))
            fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            winner = compare_df.sort_values('scale_potential', ascending=False).iloc[0]
            st.success(f"🏆 **Meilleur potentiel:** {winner['format']} | {winner['nom'][:40]}... (Potentiel: {winner['scale_potential']})")
        else:
            st.info("👆 Sélectionnez au moins 2 créatives")


if __name__ == "__main__":
    main()
