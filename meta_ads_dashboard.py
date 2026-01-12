"""
Meta Ads Creative Intelligence Dashboard V2.3
=============================================
Application de pilotage des créatives publicitaires Meta Ads.
Tableau avec composants natifs Streamlit pour un affichage fiable.

Auteur: Saïd Rassay
Version: 2.3
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import re

# Configuration de la page
st.set_page_config(
    page_title="Creative Intelligence Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser le mode sombre dans session_state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# CSS personnalisé avec mode sombre
def get_css(dark_mode=False):
    if dark_mode:
        return """
        <style>
            .stApp {
                background-color: #1a1a2e;
                color: #eaeaea;
            }
            .main-header {
                background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
                padding: 1.5rem 2rem;
                border-radius: 12px;
                color: white;
                margin-bottom: 2rem;
            }
            .action-card {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid;
            }
            .scale-card { background: #1e3a2f; border-color: #10B981; }
            .test-card { background: #1e2a3a; border-color: #3B82F6; }
            .monitor-card { background: #3a3520; border-color: #F59E0B; }
            .pause-card { background: #3a1e1e; border-color: #EF4444; }
            .alert-card {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid;
                background: #2a1e1e;
                border-color: #EF4444;
            }
            .warning-card {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid;
                background: #3a3520;
                border-color: #F59E0B;
            }
            .info-card {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid;
                background: #1e2a3a;
                border-color: #3B82F6;
            }
            .trend-badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            .trend-up { background: #064e3b; color: #6ee7b7; }
            .trend-down { background: #7f1d1d; color: #fca5a5; }
            .trend-stable { background: #374151; color: #d1d5db; }
            .stTabs [data-baseweb="tab-list"] { gap: 8px; }
            .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px; }
            .metric-box {
                background: #2d2d44;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
            }
        </style>
        """
    else:
        return """
        <style>
            .main-header {
                background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
                padding: 1.5rem 2rem;
                border-radius: 12px;
                color: white;
                margin-bottom: 2rem;
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
            .alert-card {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid;
                background: #FEF2F2;
                border-color: #EF4444;
            }
            .warning-card {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid;
                background: #FFFBEB;
                border-color: #F59E0B;
            }
            .info-card {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid;
                background: #EFF6FF;
                border-color: #3B82F6;
            }
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
            .stTabs [data-baseweb="tab-list"] { gap: 8px; }
            .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px; }
            .metric-box {
                background: #F8FAFC;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
            }
        </style>
        """


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


def calculate_trends_from_daily(df_daily, lookback_days=30):
    """Calcule les tendances à partir des données quotidiennes."""
    
    if df_daily is None or len(df_daily) == 0 or 'date' not in df_daily.columns:
        return {}, {}
    
    df_daily = df_daily.dropna(subset=['date'])
    if len(df_daily) == 0:
        return {}, {}
    
    date_max = df_daily['date'].max()
    date_7j = date_max - timedelta(days=6)
    date_14j = date_max - timedelta(days=13)
    date_30j = date_max - timedelta(days=29)
    
    trends = {}
    sparklines = {}
    
    for nom in df_daily['nom'].unique():
        df_crea = df_daily[df_daily['nom'] == nom].sort_values('date')
        df_30j = df_crea[df_crea['date'] >= date_30j]
        
        # Stocker les 30 derniers jours de données
        sparkline_data = []
        dates = pd.date_range(start=date_30j, end=date_max, freq='D')
        
        for d in dates:
            row = df_30j[df_30j['date'].dt.date == d.date()]
            if len(row) > 0 and row.iloc[0].get('impressions', 0) > 0:
                impressions = float(row.iloc[0].get('impressions', 0))
                reach = float(row.iloc[0].get('reach', 0))
                depense = float(row.iloc[0].get('depense', 0))
                # Calculer CPMu : (dépense / reach) * 1000
                cpmu = (depense / reach * 1000) if reach > 0 else 0
                
                sparkline_data.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'impressions': impressions,
                    'ctr': float(row.iloc[0].get('ctr_lien', 0)),
                    'depense': depense,
                    'cpm': float(row.iloc[0].get('cpm', 0)),
                    'reach': reach,
                    'cpmu': cpmu
                })
            else:
                sparkline_data.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'impressions': 0, 'ctr': 0, 'depense': 0, 'cpm': 0, 'reach': 0, 'cpmu': 0
                })
        
        sparklines[nom] = sparkline_data
        
        # Calcul des tendances sur 7j vs 7j précédents
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
        
        trend_score = 0.40 * trend_ctr + 0.25 * (-trend_cpc) + 0.20 * (-trend_cpm) + 0.15 * trend_impr
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
    elif ' pv ' in nom_lower or nom_lower.startswith('pv ') or '--pv--' in nom_lower:
        hook = 'Proposition de Valeur'
    elif 'produit neutre' in nom_lower:
        hook = 'Produit neutre'
    
    return {'usp': usp, 'hook': hook, 'format': format_type}


def calculate_confidence(row):
    """Calcule le coefficient de confiance basé sur le volume."""
    impressions = row.get('impressions', 0)
    achats = row.get('achats', 0)
    clics = row.get('clics_lien', 0)
    
    if impressions < 1000: score_impr = 0.3
    elif impressions < 5000: score_impr = 0.5
    elif impressions < 10000: score_impr = 0.7
    elif impressions < 50000: score_impr = 0.85
    else: score_impr = 1.0
    
    if achats < 5: score_conv = 0.4
    elif achats < 15: score_conv = 0.6
    elif achats < 30: score_conv = 0.8
    else: score_conv = 1.0
    
    if clics < 50: score_clics = 0.5
    elif clics < 200: score_clics = 0.7
    elif clics < 500: score_clics = 0.85
    else: score_clics = 1.0
    
    return round(0.3 * score_impr + 0.4 * score_conv + 0.3 * score_clics, 2)


def calculate_scale_potential(row, score_global_ajuste, coef_conf, trend_score=0):
    """Calcule le potentiel de scale."""
    perf_score = min(100, max(0, score_global_ajuste))
    
    if trend_score > 50: trend_component = 90
    elif trend_score > 20: trend_component = 75
    elif trend_score > 0: trend_component = 60
    elif trend_score > -20: trend_component = 40
    else: trend_component = 20
    
    freq = row.get('frequency', 2)
    if freq < 1.5: freq_score = 100
    elif freq < 2.0: freq_score = 85
    elif freq < 2.5: freq_score = 70
    elif freq < 3.0: freq_score = 55
    elif freq < 4.0: freq_score = 35
    else: freq_score = 15
    
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
    """Retourne le grade basé sur le score."""
    if score >= 70: return 'A'
    elif score >= 60: return 'B'
    elif score >= 50: return 'C'
    elif score >= 40: return 'D'
    else: return 'F'


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
    
    # Calculer le CPMu (Cost Per Mille Unique)
    df['cpmu'] = np.where(df['reach'] > 0, (df['depense'] / df['reach']) * 1000, 0)
    
    roas_mean, roas_std = calc_stats(df['roas'])
    ctr_mean, ctr_std = calc_stats(df['ctr_lien'])
    cpc_mean, cpc_std = calc_stats(df['cpc_lien'])
    cpm_mean, cpm_std = calc_stats(df['cpm'])
    cpmu_mean, cpmu_std = calc_stats(df['cpmu'])
    reach_mean, reach_std = calc_stats(df['reach'])
    clics_mean, clics_std = calc_stats(df['clics_lien'])
    
    df['cvr'] = np.where(df['clics_lien'] > 0, (df['achats'] / df['clics_lien']) * 100, 0)
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
        z_cpmu = z_score(row['cpmu'], cpmu_mean, cpmu_std, inverse=True)
        z_reach = z_score(row['reach'], reach_mean, reach_std)
        z_clics = z_score(row['clics_lien'], clics_mean, clics_std)
        
        def z_to_100(z):
            return max(0, min(100, 50 + z * 10))
        
        score_profit = round(z_to_100(0.45 * z_roas + 0.35 * z_cpa + 0.20 * z_cvr))
        score_trafic = round(z_to_100(0.50 * z_ctr + 0.30 * z_cpc + 0.20 * z_clics))
        # Nouveau calcul: CPMu inversé (50%) + Couverture (50%)
        score_notoriete = round(z_to_100(0.50 * z_cpmu + 0.50 * z_reach))
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
    """Détermine l'action recommandée."""
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
        return f"Potentiel {potential} → Budget {pct}"
    elif action == 'pause':
        if trend_score < -30:
            return f"Tendance {trend_score:.0f}% → Pauser"
        return f"Frequency {freq:.1f} → Pauser"
    elif action == 'test':
        return f"Confiance {conf*100:.0f}% → Tester +50%"
    else:
        if freq > 3:
            return f"Frequency {freq:.1f} → Surveiller"
        return "Stable → Maintenir"


def detect_alerts(df, trends=None):
    """Détecte les alertes automatiques basées sur les seuils."""
    alerts = []
    
    # Calculer les seuils pour CPMu
    cpmu_mean = df['cpmu'].mean() if 'cpmu' in df.columns else 0
    cpmu_q75 = df['cpmu'].quantile(0.75) if 'cpmu' in df.columns else 0
    
    for _, row in df.iterrows():
        nom = row['nom']
        
        # Alerte Frequency > 3
        if row.get('frequency', 0) > 3:
            alerts.append({
                'type': 'danger',
                'icon': '🔴',
                'title': 'Frequency critique',
                'creative': nom,
                'message': f"Frequency à {row['frequency']:.2f} (seuil: 3.0)",
                'action': 'Pauser ou réduire le budget immédiatement',
                'priority': 1
            })
        elif row.get('frequency', 0) > 2.5:
            alerts.append({
                'type': 'warning',
                'icon': '🟠',
                'title': 'Frequency élevée',
                'creative': nom,
                'message': f"Frequency à {row['frequency']:.2f} (seuil warning: 2.5)",
                'action': 'Surveiller de près, envisager de réduire',
                'priority': 2
            })
        
        # Alerte CPMu explosif (> 2x la moyenne ou > 150% du Q75)
        cpmu = row.get('cpmu', 0)
        if cpmu_mean > 0 and cpmu > 0:
            if cpmu > cpmu_mean * 2.5:
                alerts.append({
                    'type': 'danger',
                    'icon': '🔴',
                    'title': 'CPMu explosif',
                    'creative': nom,
                    'message': f"CPMu à {cpmu:.2f}€ (moyenne: {cpmu_mean:.2f}€, +{((cpmu/cpmu_mean)-1)*100:.0f}%)",
                    'action': 'Audience saturée - Pauser ou changer de ciblage',
                    'priority': 1
                })
            elif cpmu > cpmu_mean * 1.8:
                alerts.append({
                    'type': 'warning',
                    'icon': '🟠',
                    'title': 'CPMu élevé',
                    'creative': nom,
                    'message': f"CPMu à {cpmu:.2f}€ (moyenne: {cpmu_mean:.2f}€, +{((cpmu/cpmu_mean)-1)*100:.0f}%)",
                    'action': 'Surveiller - Risque de saturation audience',
                    'priority': 2
                })
        
        # Alerte tendance < -20%
        trend_score = row.get('trend_score', 0)
        if trend_score < -30:
            alerts.append({
                'type': 'danger',
                'icon': '🔴',
                'title': 'Chute de performance',
                'creative': nom,
                'message': f"Tendance à {trend_score:.0f}% sur 7 jours",
                'action': 'Pauser cette créative',
                'priority': 1
            })
        elif trend_score < -20:
            alerts.append({
                'type': 'warning',
                'icon': '🟠',
                'title': 'Tendance négative',
                'creative': nom,
                'message': f"Tendance à {trend_score:.0f}% sur 7 jours",
                'action': 'Surveiller et préparer une alternative',
                'priority': 2
            })
    
    # Trier par priorité
    alerts.sort(key=lambda x: x['priority'])
    return alerts


def detect_anomalies(df, sparklines):
    """Détecte les anomalies (variations brutales > 50% en 24h)."""
    anomalies = []
    
    if not sparklines:
        return anomalies
    
    for _, row in df.iterrows():
        nom = row['nom']
        
        if nom not in sparklines or len(sparklines[nom]) < 2:
            continue
        
        data = sparklines[nom]
        
        # Vérifier les 2 derniers jours
        if len(data) >= 2:
            yesterday = data[-2]
            today = data[-1]
            
            # Anomalie CTR (chute > 50%)
            if yesterday.get('ctr', 0) > 0 and today.get('ctr', 0) > 0:
                ctr_change = ((today['ctr'] - yesterday['ctr']) / yesterday['ctr']) * 100
                if ctr_change < -50:
                    anomalies.append({
                        'type': 'danger',
                        'icon': '⚠️',
                        'title': 'Chute CTR brutale',
                        'creative': nom,
                        'message': f"CTR: {yesterday['ctr']:.2f}% → {today['ctr']:.2f}% ({ctr_change:.0f}% en 24h)",
                        'action': 'Vérifier si problème technique ou fatigue soudaine',
                        'priority': 1
                    })
            
            # Anomalie CPM (hausse > 50%)
            if yesterday.get('cpm', 0) > 0 and today.get('cpm', 0) > 0:
                cpm_change = ((today['cpm'] - yesterday['cpm']) / yesterday['cpm']) * 100
                if cpm_change > 50:
                    anomalies.append({
                        'type': 'danger',
                        'icon': '⚠️',
                        'title': 'Explosion CPM',
                        'creative': nom,
                        'message': f"CPM: {yesterday['cpm']:.2f}€ → {today['cpm']:.2f}€ (+{cpm_change:.0f}% en 24h)",
                        'action': 'Vérifier la concurrence ou problème de ciblage',
                        'priority': 1
                    })
    
    return anomalies


def predict_fatigue(df, sparklines):
    """Prédit dans combien de jours une créative sera fatiguée."""
    predictions = []
    
    for _, row in df.iterrows():
        nom = row['nom']
        current_freq = row.get('frequency', 1)
        
        # Si déjà fatiguée
        if current_freq >= 4:
            predictions.append({
                'creative': nom,
                'format': row['format'],
                'current_freq': current_freq,
                'days_to_fatigue': 0,
                'status': 'fatiguée',
                'color': '🔴'
            })
            continue
        
        # Calculer le taux d'augmentation de frequency
        if nom in sparklines and len(sparklines[nom]) >= 7:
            data = sparklines[nom]
            
            # Estimer frequency par jour (impressions / reach approximatif)
            impressions_recent = sum(d.get('impressions', 0) for d in data[-7:])
            impressions_old = sum(d.get('impressions', 0) for d in data[:7]) if len(data) >= 14 else impressions_recent
            
            # Taux de croissance estimé de la frequency par jour
            if impressions_old > 0 and impressions_recent > 0:
                growth_rate = (impressions_recent / impressions_old - 1) / 7 * 0.1  # Approximation
            else:
                growth_rate = 0.05  # Valeur par défaut
        else:
            growth_rate = 0.05  # Valeur par défaut (5% par jour)
        
        # Calculer jours restants avant frequency = 4
        if growth_rate > 0 and current_freq < 4:
            days_to_fatigue = int((4 - current_freq) / (current_freq * growth_rate))
            days_to_fatigue = max(1, min(days_to_fatigue, 60))  # Entre 1 et 60 jours
        else:
            days_to_fatigue = 30  # Par défaut
        
        if days_to_fatigue <= 3:
            status = 'critique'
            color = '🔴'
        elif days_to_fatigue <= 7:
            status = 'attention'
            color = '🟠'
        elif days_to_fatigue <= 14:
            status = 'à surveiller'
            color = '🟡'
        else:
            status = 'OK'
            color = '🟢'
        
        predictions.append({
            'creative': nom,
            'format': row['format'],
            'current_freq': current_freq,
            'days_to_fatigue': days_to_fatigue,
            'status': status,
            'color': color
        })
    
    # Trier par jours restants
    predictions.sort(key=lambda x: x['days_to_fatigue'])
    return predictions


def calculate_diversification_score(df):
    """Calcule le score de diversification et détecte les concentrations de budget."""
    alerts = []
    
    total_budget = df['depense'].sum()
    
    if total_budget == 0:
        return {'score': 100, 'alerts': [], 'by_usp': {}, 'by_hook': {}, 'by_format': {}}
    
    # Analyse par USP
    usp_budget = df.groupby('usp')['depense'].sum()
    usp_pct = (usp_budget / total_budget * 100).to_dict()
    
    for usp, pct in usp_pct.items():
        if pct > 50:
            alerts.append({
                'type': 'danger',
                'icon': '🎯',
                'title': f'Concentration USP: {usp}',
                'message': f'{pct:.0f}% du budget sur cette USP',
                'action': 'Diversifier vers d\'autres USP pour réduire le risque',
                'priority': 1
            })
        elif pct > 35:
            alerts.append({
                'type': 'warning',
                'icon': '🎯',
                'title': f'USP dominante: {usp}',
                'message': f'{pct:.0f}% du budget sur cette USP',
                'action': 'Envisager de tester d\'autres angles',
                'priority': 2
            })
    
    # Analyse par Hook
    hook_budget = df.groupby('hook')['depense'].sum()
    hook_pct = (hook_budget / total_budget * 100).to_dict()
    
    for hook, pct in hook_pct.items():
        if pct > 50:
            alerts.append({
                'type': 'danger',
                'icon': '🎣',
                'title': f'Concentration Hook: {hook}',
                'message': f'{pct:.0f}% du budget sur ce hook',
                'action': 'Tester d\'autres types d\'accroches',
                'priority': 1
            })
    
    # Analyse par Format
    format_budget = df.groupby('format')['depense'].sum()
    format_pct = (format_budget / total_budget * 100).to_dict()
    
    for fmt, pct in format_pct.items():
        if pct > 70:
            alerts.append({
                'type': 'warning',
                'icon': '📐',
                'title': f'Concentration Format: {fmt}',
                'message': f'{pct:.0f}% du budget sur ce format',
                'action': 'Tester d\'autres formats (vidéo, carousel, etc.)',
                'priority': 2
            })
    
    # Calculer score de diversification (100 = parfaitement diversifié)
    # Plus il y a de concentration, plus le score est bas
    max_usp_pct = max(usp_pct.values()) if usp_pct else 0
    max_hook_pct = max(hook_pct.values()) if hook_pct else 0
    max_format_pct = max(format_pct.values()) if format_pct else 0
    
    # Score: 100 si tout est à 25%, 0 si tout est à 100%
    score = 100 - (max_usp_pct * 0.4 + max_hook_pct * 0.35 + max_format_pct * 0.25) * 0.7
    score = max(0, min(100, score))
    
    return {
        'score': round(score),
        'alerts': alerts,
        'by_usp': usp_pct,
        'by_hook': hook_pct,
        'by_format': format_pct
    }


def format_score_with_grade(score, variation=0):
    """Formate un score avec grade et variation pour affichage."""
    grade = get_grade(score)
    if variation > 0:
        var_str = f" (+{variation})"
    elif variation < 0:
        var_str = f" ({variation})"
    else:
        var_str = ""
    return f"{score} {grade}{var_str}"


def create_sparkline_plotly(sparkline_data, width=120, height=40):
    """Crée un mini graphique sparkline avec Plotly."""
    if not sparkline_data:
        return None
    
    values = [d.get('ctr', 0) for d in sparkline_data]
    if max(values) == 0:
        return None
    
    recent_avg = np.mean(values[-4:]) if len(values) >= 4 else np.mean(values)
    old_avg = np.mean(values[:4]) if len(values) >= 4 else np.mean(values)
    trend = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0
    
    color = '#10B981' if trend > 10 else '#EF4444' if trend < -10 else '#6B7280'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(values))),
        y=values,
        mode='lines',
        line=dict(color=color, width=2),
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        width=width,
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
    # Appliquer le CSS selon le mode
    st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Creative Intelligence Dashboard</h1>
        <p>Pilotage intelligent de vos créatives Meta Ads</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Mode sombre en haut
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("📁 Import des données")
        with col2:
            if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="Changer le thème"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        import_mode = st.radio(
            "Mode d'import",
            ["Données agrégées uniquement", "Agrégées + Quotidiennes (recommandé)"]
        )
        
        st.divider()
        
        st.subheader("1️⃣ Données agrégées")
        uploaded_main = st.file_uploader("Fichier principal", type=['csv'], key="main_file")
        
        if uploaded_main:
            st.success(f"✅ {uploaded_main.name}")
        
        uploaded_daily = None
        if import_mode == "Agrégées + Quotidiennes (recommandé)":
            st.divider()
            st.subheader("2️⃣ Données quotidiennes")
            uploaded_daily = st.file_uploader("Fichier quotidien", type=['csv'], key="daily_file")
            
            if uploaded_daily:
                st.success(f"✅ {uploaded_daily.name}")
        
        st.divider()
        st.header("⚙️ Paramètres")
        min_impressions = st.slider("Impressions minimum", 0, 10000, 500, 100)
        
        st.divider()
        st.markdown("""
        **Légende:** 🚀 Scaler · ⚡ Tester · 👁️ Surveiller · ⏸️ Pauser
        """)
    
    # Page principale
    if uploaded_main is None:
        st.info("👈 Chargez votre export Meta Ads pour commencer.")
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
        return
    
    if has_daily:
        st.success("✅ Données quotidiennes chargées - Tendances et sparklines activées")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Actions du jour",
        "🚨 Alertes & Prédictions",
        "📊 Angles créatifs", 
        "📈 Tableau détaillé",
        "⚖️ Comparateur"
    ])
    
    # ========== TAB 1: Actions du jour ==========
    with tab1:
        # Calculer les KPIs globaux
        total_spend = df['depense'].sum()
        total_revenue = df['valeur_achats'].sum()
        avg_roas = total_revenue / total_spend if total_spend > 0 else 0
        total_achats = df['achats'].sum()
        avg_ctr = df['ctr_lien'].mean()
        avg_cpm = df['cpm'].mean()
        
        action_counts = df['action'].value_counts()
        scale_count = action_counts.get('scale', 0)
        test_count = action_counts.get('test', 0)
        monitor_count = action_counts.get('monitor', 0)
        pause_count = action_counts.get('pause', 0)
        
        # Calculer le score de santé global
        pct_scale = (scale_count / len(df) * 100) if len(df) > 0 else 0
        pct_pause = (pause_count / len(df) * 100) if len(df) > 0 else 0
        diversification = calculate_diversification_score(df)
        alerts_count = len(detect_alerts(df, trends))
        
        health_score = round(
            (pct_scale * 2) +  # Bonus pour créatives à scaler
            (100 - pct_pause * 3) * 0.3 +  # Pénalité pour créatives à pauser
            (diversification['score'] * 0.3) +  # Score diversification
            (max(0, 30 - alerts_count * 5))  # Pénalité alertes
        )
        health_score = max(0, min(100, health_score))
        
        health_status = "🟢 Excellent" if health_score >= 75 else "🟡 Bon" if health_score >= 50 else "🟠 Moyen" if health_score >= 30 else "🔴 Critique"
        
        # Budget par action
        budget_scale = df[df['action'] == 'scale']['depense'].sum()
        budget_test = df[df['action'] == 'test']['depense'].sum()
        budget_monitor = df[df['action'] == 'monitor']['depense'].sum()
        budget_pause = df[df['action'] == 'pause']['depense'].sum()
        
        pct_budget_scale = (budget_scale / total_spend * 100) if total_spend > 0 else 0
        pct_budget_test = (budget_test / total_spend * 100) if total_spend > 0 else 0
        pct_budget_monitor = (budget_monitor / total_spend * 100) if total_spend > 0 else 0
        pct_budget_pause = (budget_pause / total_spend * 100) if total_spend > 0 else 0
        
        # Potentiel moyen par action
        pot_scale = df[df['action'] == 'scale']['scale_potential'].mean() if scale_count > 0 else 0
        pot_test = df[df['action'] == 'test']['scale_potential'].mean() if test_count > 0 else 0
        
        # ===== LIGNE 1: KPIs GLOBAUX =====
        st.markdown("##### 📊 Performance globale")
        kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
        
        with kpi1:
            spend_delta = None
            if has_daily:
                # Calculer variation vs 7j précédents
                spend_delta = f"Budget total"
            st.metric("💰 Dépense", f"{total_spend:,.0f}€", delta=spend_delta)
        
        with kpi2:
            roas_status = "↗ Rentable" if avg_roas >= 2 else "↘ À améliorer" if avg_roas < 1 else None
            st.metric("📈 ROAS", f"{avg_roas:.2f}", delta=roas_status, delta_color="normal" if avg_roas >= 2 else "inverse")
        
        with kpi3:
            st.metric("🛒 Achats", f"{total_achats:,.0f}")
        
        with kpi4:
            ctr_status = "Bon" if avg_ctr >= 1.5 else None
            st.metric("👆 CTR", f"{avg_ctr:.2f}%", delta=ctr_status)
        
        with kpi5:
            st.metric("💵 CPM", f"{avg_cpm:.2f}€")
        
        with kpi6:
            st.metric("🎯 Santé", f"{health_score}/100", delta=health_status, delta_color="normal" if health_score >= 50 else "inverse")
        
        # ===== LIGNE 2: RÉSUMÉ EXÉCUTIF =====
        summary_parts = []
        if scale_count > 0:
            summary_parts.append(f"**{scale_count}** créa{'s' if scale_count > 1 else ''} à scaler ({pct_budget_scale:.0f}% budget)")
        if pause_count > 0:
            summary_parts.append(f"**{pause_count}** à pauser")
        if alerts_count > 0:
            summary_parts.append(f"**{alerts_count}** alerte{'s' if alerts_count > 1 else ''}")
        summary_parts.append(f"Diversification: **{diversification['score']}/100**")
        
        st.info(f"🎯 {' · '.join(summary_parts)}")
        
        # ===== LIGNE 3: CARDS ACTIONS + GRAPHIQUE =====
        col_cards, col_chart = st.columns([3, 1])
        
        with col_cards:
            # 4 cards métriques enrichies sur une ligne
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown(f"""
                <div class="action-card scale-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700;">{scale_count}</div>
                    <div style="font-weight:600;">🚀 À scaler</div>
                    <div style="font-size:0.75rem; opacity:0.8;">{pct_budget_scale:.0f}% budget · Pot. {pot_scale:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""
                <div class="action-card test-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700;">{test_count}</div>
                    <div style="font-weight:600;">⚡ À tester</div>
                    <div style="font-size:0.75rem; opacity:0.8;">{pct_budget_test:.0f}% budget · Pot. {pot_test:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c3:
                st.markdown(f"""
                <div class="action-card monitor-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700;">{monitor_count}</div>
                    <div style="font-weight:600;">👁️ Surveiller</div>
                    <div style="font-size:0.75rem; opacity:0.8;">{pct_budget_monitor:.0f}% budget</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c4:
                st.markdown(f"""
                <div class="action-card pause-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700;">{pause_count}</div>
                    <div style="font-weight:600;">⏸️ À pauser</div>
                    <div style="font-size:0.75rem; opacity:0.8;">{pct_budget_pause:.0f}% budget</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_chart:
            # Mini pie chart répartition budget
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Scale', 'Test', 'Monitor', 'Pause'],
                values=[budget_scale, budget_test, budget_monitor, budget_pause],
                hole=0.6,
                marker_colors=['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
                textinfo='none',
                hovertemplate='%{label}: %{percent}<extra></extra>'
            )])
            fig_pie.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=120,
                annotations=[dict(text='Budget', x=0.5, y=0.5, font_size=11, showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # ===== LIGNE 4: LISTES D'ACTIONS (COMPACT) =====
        col_left, col_right = st.columns(2)
        
        with col_left:
            # À scaler (compact)
            st.markdown("##### 🚀 À scaler")
            scale_df = df[df['action'] == 'scale'].sort_values('scale_potential', ascending=False)
            
            if len(scale_df) > 0:
                for _, row in scale_df.head(4).iterrows():
                    trend_badge = ""
                    if has_daily and row['trend_signal'] == 'up':
                        trend_badge = f"<span class='trend-badge trend-up'>+{row['trend_score']:.0f}%</span>"
                    elif has_daily and row['trend_signal'] == 'down':
                        trend_badge = f"<span class='trend-badge trend-down'>{row['trend_score']:.0f}%</span>"
                    
                    st.markdown(f"""
                    <div class="action-card scale-card" style="padding:0.6rem 0.8rem; margin-bottom:0.4rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <strong>{row['format']}</strong> · {row['nom'][:35]}{'...' if len(row['nom']) > 35 else ''} {trend_badge}
                                <div style="font-size:0.75rem; opacity:0.8;">ROAS {row['roas']:.1f} · CTR {row['ctr_lien']:.2f}% · Pot. {row['scale_potential']}</div>
                            </div>
                            <div style="font-size:0.7rem; background:#10B981; color:white; padding:2px 8px; border-radius:4px;">+20%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                if len(scale_df) > 4:
                    st.caption(f"... et {len(scale_df) - 4} autre(s)")
            else:
                st.caption("Aucune créative prête à scaler")
            
            # À surveiller (très compact)
            st.markdown("##### 👁️ À surveiller")
            monitor_df = df[df['action'] == 'monitor'].sort_values('scale_potential', ascending=False).head(3)
            
            if len(monitor_df) > 0:
                for _, row in monitor_df.iterrows():
                    trend_icon = "→"
                    if has_daily:
                        trend_icon = "↗" if row['trend_signal'] == 'up' else "↘" if row['trend_signal'] == 'down' else "→"
                    
                    st.markdown(f"""
                    <div class="action-card monitor-card" style="padding:0.5rem 0.8rem; margin-bottom:0.3rem;">
                        <strong>{row['format']}</strong> · {row['nom'][:30]}... <span style="opacity:0.6;">{trend_icon}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_right:
            # À tester (compact)
            st.markdown("##### ⚡ À tester")
            test_df = df[df['action'] == 'test'].sort_values('scale_potential', ascending=False)
            
            if len(test_df) > 0:
                for _, row in test_df.head(4).iterrows():
                    st.markdown(f"""
                    <div class="action-card test-card" style="padding:0.6rem 0.8rem; margin-bottom:0.4rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <strong>{row['format']}</strong> · {row['nom'][:35]}{'...' if len(row['nom']) > 35 else ''}
                                <div style="font-size:0.75rem; opacity:0.8;">ROAS {row['roas']:.1f} · Confiance {row['coefficient_confiance']*100:.0f}%</div>
                            </div>
                            <div style="font-size:0.7rem; background:#3B82F6; color:white; padding:2px 8px; border-radius:4px;">+50%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                if len(test_df) > 4:
                    st.caption(f"... et {len(test_df) - 4} autre(s)")
            else:
                st.caption("Aucune créative à tester")
            
            # À pauser (compact)
            st.markdown("##### ⏸️ À pauser")
            pause_df = df[df['action'] == 'pause']
            
            if len(pause_df) > 0:
                for _, row in pause_df.head(3).iterrows():
                    trend_badge = ""
                    if has_daily and row['trend_score'] < -20:
                        trend_badge = f"<span class='trend-badge trend-down'>{row['trend_score']:.0f}%</span>"
                    
                    st.markdown(f"""
                    <div class="action-card pause-card" style="padding:0.5rem 0.8rem; margin-bottom:0.3rem;">
                        <strong>{row['format']}</strong> · {row['nom'][:30]}... {trend_badge}
                        <div style="font-size:0.7rem; opacity:0.8;">Freq. {row['frequency']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                if len(pause_df) > 3:
                    st.caption(f"... et {len(pause_df) - 3} autre(s)")
            else:
                st.success("✅ Aucune créative à pauser")
    
    # ========== TAB 2: Alertes & Prédictions ==========
    with tab2:
        # Générer toutes les alertes
        alerts = detect_alerts(df, trends)
        anomalies = detect_anomalies(df, sparklines) if has_daily else []
        fatigue_predictions = predict_fatigue(df, sparklines) if has_daily else []
        diversification_data = calculate_diversification_score(df)
        
        # Compteurs
        critical_alerts = len([a for a in alerts if a['type'] == 'danger'])
        warning_alerts = len([a for a in alerts if a['type'] == 'warning'])
        fatigued_soon = len([p for p in fatigue_predictions if p['days_to_fatigue'] <= 7 and p['days_to_fatigue'] > 0])
        fatigued_critical = len([p for p in fatigue_predictions if p['days_to_fatigue'] <= 3 and p['days_to_fatigue'] > 0])
        
        # ===== RÉSUMÉ D'URGENCE =====
        if critical_alerts > 0:
            st.error(f"🔴 **{critical_alerts} alerte(s) critique(s)** nécessitent une action immédiate")
        elif warning_alerts > 0:
            st.warning(f"🟠 **{warning_alerts} alerte(s)** à surveiller")
        else:
            st.success("✅ **Aucune alerte critique** - Tout est sous contrôle")
        
        # ===== LAYOUT EN 4 COLONNES =====
        col1, col2, col3, col4 = st.columns(4)
        
        # --- Colonne 1: Alertes ---
        with col1:
            st.markdown(f"##### 🔔 Alertes ({len(alerts)})")
            
            if alerts:
                for alert in alerts[:5]:  # Max 5
                    icon = "🔴" if alert['type'] == 'danger' else "🟠"
                    st.markdown(f"""
                    <div style="padding:0.4rem 0.6rem; margin-bottom:0.3rem; border-left:3px solid {'#EF4444' if alert['type'] == 'danger' else '#F59E0B'}; background:{'#FEF2F2' if alert['type'] == 'danger' else '#FFFBEB'}; border-radius:4px; font-size:0.8rem;">
                        {icon} <strong>{alert['title'][:20]}</strong><br>
                        <span style="opacity:0.7;">{alert['creative'][:25]}...</span><br>
                        <span style="font-size:0.7rem;">{alert['message'][:35]}...</span>
                    </div>
                    """, unsafe_allow_html=True)
                if len(alerts) > 5:
                    st.caption(f"... +{len(alerts) - 5} autre(s)")
            else:
                st.markdown("""
                <div style="padding:1rem; text-align:center; opacity:0.6;">
                    ✅ Aucune alerte
                </div>
                """, unsafe_allow_html=True)
        
        # --- Colonne 2: Anomalies ---
        with col2:
            st.markdown(f"##### ⚠️ Anomalies 24h ({len(anomalies)})")
            
            if not has_daily:
                st.caption("Chargez données quotidiennes")
            elif anomalies:
                for anomaly in anomalies[:4]:  # Max 4
                    st.markdown(f"""
                    <div style="padding:0.4rem 0.6rem; margin-bottom:0.3rem; border-left:3px solid #EF4444; background:#FEF2F2; border-radius:4px; font-size:0.8rem;">
                        ⚠️ <strong>{anomaly['title'][:18]}</strong><br>
                        <span style="opacity:0.7;">{anomaly['creative'][:22]}...</span><br>
                        <span style="font-size:0.7rem;">{anomaly['message'][:40]}</span>
                    </div>
                    """, unsafe_allow_html=True)
                if len(anomalies) > 4:
                    st.caption(f"... +{len(anomalies) - 4} autre(s)")
            else:
                st.markdown("""
                <div style="padding:1rem; text-align:center; opacity:0.6;">
                    ✅ Aucune anomalie
                </div>
                """, unsafe_allow_html=True)
        
        # --- Colonne 3: Fatigue ---
        with col3:
            st.markdown(f"##### 😴 Fatigue ({fatigued_soon} < 7j)")
            
            if not has_daily:
                st.caption("Chargez données quotidiennes")
            elif fatigue_predictions:
                # Afficher seulement les critiques et attention
                urgent_fatigue = [p for p in fatigue_predictions if p['days_to_fatigue'] <= 14][:5]
                
                for p in urgent_fatigue:
                    if p['days_to_fatigue'] == 0:
                        bg_color = "#FEF2F2"
                        border_color = "#EF4444"
                        days_text = "Fatiguée"
                    elif p['days_to_fatigue'] <= 3:
                        bg_color = "#FEF2F2"
                        border_color = "#EF4444"
                        days_text = f"{p['days_to_fatigue']}j"
                    elif p['days_to_fatigue'] <= 7:
                        bg_color = "#FFFBEB"
                        border_color = "#F59E0B"
                        days_text = f"{p['days_to_fatigue']}j"
                    else:
                        bg_color = "#F0FDF4"
                        border_color = "#10B981"
                        days_text = f"{p['days_to_fatigue']}j"
                    
                    st.markdown(f"""
                    <div style="padding:0.4rem 0.6rem; margin-bottom:0.3rem; border-left:3px solid {border_color}; background:{bg_color}; border-radius:4px; font-size:0.8rem; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>{p['format']}</strong> · {p['creative'][:18]}...<br>
                            <span style="opacity:0.7; font-size:0.7rem;">Freq: {p['current_freq']:.2f}</span>
                        </div>
                        <div style="font-weight:700; color:{border_color};">{days_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                ok_count = len([p for p in fatigue_predictions if p['days_to_fatigue'] > 14])
                if ok_count > 0:
                    st.caption(f"✅ {ok_count} créa(s) OK (> 14j)")
            else:
                st.caption("Aucune prédiction")
        
        # --- Colonne 4: Diversification ---
        with col4:
            score = diversification_data['score']
            score_color = "#10B981" if score >= 70 else "#F59E0B" if score >= 50 else "#EF4444"
            score_bg = "#F0FDF4" if score >= 70 else "#FFFBEB" if score >= 50 else "#FEF2F2"
            
            st.markdown(f"##### 🎯 Diversification")
            
            # Score avec jauge visuelle
            st.markdown(f"""
            <div style="padding:0.6rem; background:{score_bg}; border-radius:8px; text-align:center; margin-bottom:0.5rem;">
                <div style="font-size:1.8rem; font-weight:700; color:{score_color};">{score}</div>
                <div style="font-size:0.75rem; opacity:0.8;">/100</div>
                <div style="background:#E5E7EB; border-radius:4px; height:8px; margin-top:0.5rem;">
                    <div style="background:{score_color}; width:{score}%; height:100%; border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Top concentrations
            st.markdown("<div style='font-size:0.75rem;'><strong>Répartition budget:</strong></div>", unsafe_allow_html=True)
            
            for usp, pct in sorted(diversification_data['by_usp'].items(), key=lambda x: -x[1])[:3]:
                bar_color = "#10B981" if pct < 35 else "#F59E0B" if pct < 50 else "#EF4444"
                st.markdown(f"""
                <div style="font-size:0.7rem; margin-bottom:0.2rem;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>{usp[:15]}{'...' if len(usp) > 15 else ''}</span>
                        <span style="font-weight:600;">{pct:.0f}%</span>
                    </div>
                    <div style="background:#E5E7EB; border-radius:2px; height:4px;">
                        <div style="background:{bar_color}; width:{min(pct, 100)}%; height:100%; border-radius:2px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Alertes concentration
            if diversification_data['alerts']:
                st.markdown(f"""
                <div style="margin-top:0.5rem; padding:0.3rem 0.5rem; background:#FFFBEB; border-radius:4px; font-size:0.7rem;">
                    ⚠️ {len(diversification_data['alerts'])} alerte(s) concentration
                </div>
                """, unsafe_allow_html=True)
    
    # ========== TAB 3: Angles créatifs ==========
    with tab3:
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
        
        with col2:
            st.subheader("🎣 Par Hook")
            hook_stats = df.groupby('hook').agg({
                'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean'
            }).round(2)
            hook_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel']
            hook_stats = hook_stats.sort_values('Potentiel', ascending=False)
            st.dataframe(hook_stats, use_container_width=True)
        
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
    
    # ========== TAB 4: Tableau détaillé ==========
    with tab4:
        st.header("Tableau détaillé")
        
        # Barre de recherche
        search_query = st.text_input("🔍 Rechercher une créative", placeholder="Tapez le nom de la créative...")
        
        # Filtres sur une ligne
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            format_filter = st.multiselect("Format", options=df['format'].unique(), default=list(df['format'].unique()))
        with col2:
            action_filter = st.multiselect("Action", options=df['action'].unique(), default=list(df['action'].unique()))
        with col3:
            sort_by = st.selectbox("Trier par", 
                options=['scale_potential', 'score_global', 'score_profitabilite', 'score_trafic', 'score_notoriete', 'trend_score', 'roas', 'ctr_lien', 'depense'],
                format_func=lambda x: {
                    'score_global': '⭐ Global', 'scale_potential': 'Potentiel', 
                    'score_profitabilite': '💰 Profit', 'score_trafic': '🚀 Trafic', 
                    'score_notoriete': '👁️ Notoriété', 'trend_score': '📈 Tendance',
                    'roas': 'ROAS', 'ctr_lien': 'CTR', 'depense': 'Dépense'
                }.get(x, x))
        with col4:
            sort_order = st.radio("Ordre", ["Décroissant", "Croissant"], horizontal=True)
        
        # Filtres avancés (expandable)
        with st.expander("🎛️ Filtres avancés"):
            col1, col2, col3 = st.columns(3)
            with col1:
                min_roas = st.number_input("ROAS minimum", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
            with col2:
                min_potential = st.slider("Potentiel minimum", 0, 100, 0)
            with col3:
                max_frequency = st.number_input("Frequency maximum", min_value=1.0, max_value=10.0, value=10.0, step=0.5)
        
        # Sélection des colonnes à afficher
        with st.expander("📊 Colonnes à afficher"):
            col1, col2, col3 = st.columns(3)
            with col1:
                show_scores = st.checkbox("Scores (Profit, Trafic, Notoriété, Global)", value=True)
            with col2:
                show_metrics = st.checkbox("Métriques (ROAS, CTR, CPMu, Dépense, Frequency)", value=True)
            with col3:
                show_confiance = st.checkbox("Confiance", value=False)
        
        # Appliquer les filtres
        filtered_df = df[
            (df['format'].isin(format_filter)) &
            (df['action'].isin(action_filter)) &
            (df['roas'] >= min_roas) &
            (df['scale_potential'] >= min_potential) &
            (df['frequency'] <= max_frequency)
        ]
        
        # Appliquer la recherche
        if search_query:
            filtered_df = filtered_df[filtered_df['nom'].str.lower().str.contains(search_query.lower())]
        
        # Trier
        filtered_df = filtered_df.sort_values(sort_by, ascending=(sort_order == "Croissant"))
        
        st.caption(f"{len(filtered_df)} créatives affichées")
        
        # Fonction pour colorer les grades
        def format_grade(score, variation=0):
            grade = get_grade(score)
            grade_colors = {'A': '🟢', 'B': '🟢', 'C': '🟡', 'D': '🟠', 'F': '🔴'}
            icon = grade_colors.get(grade, '')
            var_str = f" (+{variation})" if variation > 0 else f" ({variation})" if variation < 0 else ""
            return f"{score} {icon}{grade}{var_str}"
        
        # Fonction pour colorer les tendances
        def format_trend(value):
            if value > 10:
                return f"🟢 +{value:.0f}%"
            elif value < -10:
                return f"🔴 {value:.0f}%"
            elif value != 0:
                return f"⚪ {value:+.0f}%"
            else:
                return "⚪ 0%"
        
        # Préparer le dataframe pour l'affichage
        display_df = filtered_df.copy()
        
        # Colonnes de base (toujours visibles)
        display_df['Nom'] = display_df['nom']
        
        # Tendance formatée
        if has_daily:
            display_df['📈 Tendance'] = display_df['trend_score'].apply(format_trend)
        else:
            display_df['📈 Tendance'] = "-"
        
        # Scores formatés avec grades colorés
        display_df['💰 Profit'] = display_df.apply(
            lambda r: format_grade(r['score_profitabilite'], r.get('var_profit', 0)), axis=1
        )
        display_df['🚀 Trafic'] = display_df.apply(
            lambda r: format_grade(r['score_trafic'], r.get('var_trafic', 0)), axis=1
        )
        display_df['👁️ Notoriété'] = display_df.apply(
            lambda r: format_grade(r['score_notoriete'], r.get('var_notoriete', 0)), axis=1
        )
        display_df['⭐ Global'] = display_df.apply(
            lambda r: format_grade(r['score_global'], r.get('var_global', 0)), axis=1
        )
        
        # Métriques formatées
        display_df['ROAS'] = display_df['roas'].apply(lambda x: f"{x:.2f}" if x > 0 else "-")
        display_df['CTR %'] = display_df['ctr_lien'].apply(lambda x: f"{x:.2f}%")
        display_df['Dépense €'] = display_df['depense'].apply(lambda x: f"{x:.2f}€")
        display_df['Frequency'] = display_df['frequency'].apply(
            lambda x: f"{'🔴' if x > 3 else '🟡' if x > 2 else '🟢'} {x:.2f}"
        )
        # CPMu avec couleur (plus bas = meilleur)
        cpmu_mean = filtered_df['cpmu'].mean() if 'cpmu' in filtered_df.columns else 0
        display_df['CPMu €'] = display_df['cpmu'].apply(
            lambda x: f"{'🟢' if x < cpmu_mean * 0.8 else '🟡' if x < cpmu_mean * 1.5 else '🔴'} {x:.2f}€" if x > 0 else "-"
        )
        display_df['Confiance'] = display_df['coefficient_confiance'].apply(
            lambda x: f"{'🟢' if x >= 0.7 else '🟡' if x >= 0.5 else '🔴'} {x*100:.0f}%"
        )
        
        # Action formatée avec couleur
        action_format = {
            'scale': '🚀 Scale', 
            'test': '⚡ Test', 
            'monitor': '👁️ Monitor', 
            'pause': '⏸️ Pause'
        }
        display_df['Action'] = display_df['action'].map(action_format)
        
        # Construire la liste des colonnes à afficher
        columns_to_show = ['format', 'Nom', '📈 Tendance']
        
        if show_scores:
            columns_to_show.extend(['💰 Profit', '🚀 Trafic', '👁️ Notoriété', '⭐ Global'])
        
        if show_metrics:
            columns_to_show.extend(['ROAS', 'CTR %', 'CPMu €', 'Dépense €', 'Frequency'])
        
        if show_confiance:
            columns_to_show.append('Confiance')
        
        columns_to_show.extend(['scale_potential', 'Action'])
        
        final_df = display_df[columns_to_show].copy()
        
        # Renommer les colonnes
        rename_cols = {'format': 'Format', 'scale_potential': 'Potentiel'}
        final_df = final_df.rename(columns=rename_cols)
        
        # Configuration des colonnes pour st.dataframe
        column_config = {
            "Format": st.column_config.TextColumn("Format", width=70),
            "Nom": st.column_config.TextColumn("Nom", width=300),
            "📈 Tendance": st.column_config.TextColumn("Tendance", width=85),
            "💰 Profit": st.column_config.TextColumn("Profit", width=100),
            "🚀 Trafic": st.column_config.TextColumn("Trafic", width=100),
            "👁️ Notoriété": st.column_config.TextColumn("Notoriété", width=100),
            "⭐ Global": st.column_config.TextColumn("Global", width=100),
            "ROAS": st.column_config.TextColumn("ROAS", width=65),
            "CTR %": st.column_config.TextColumn("CTR", width=65),
            "CPMu €": st.column_config.TextColumn("CPMu", width=80),
            "Dépense €": st.column_config.TextColumn("Dépense", width=75),
            "Frequency": st.column_config.TextColumn("Freq.", width=75),
            "Confiance": st.column_config.TextColumn("Conf.", width=75),
            "Potentiel": st.column_config.ProgressColumn(
                "Potentiel",
                format="%d",
                min_value=0,
                max_value=100,
                width=90
            ),
            "Action": st.column_config.TextColumn("Action", width=90),
        }
        
        # Fonction pour colorer les lignes selon l'action
        def highlight_rows(row):
            action = filtered_df.iloc[row.name]['action'] if row.name < len(filtered_df) else 'monitor'
            colors = {
                'scale': 'background-color: #ECFDF5',  # Vert clair
                'test': 'background-color: #EFF6FF',   # Bleu clair
                'monitor': 'background-color: #FFFBEB', # Jaune clair
                'pause': 'background-color: #FEF2F2'   # Rouge clair
            }
            return [colors.get(action, '')] * len(row)
        
        # Afficher le tableau
        st.dataframe(
            final_df,
            use_container_width=True,
            height=600,
            column_config=column_config,
            hide_index=True
        )
        
        # Légende des couleurs
        st.markdown("""
        <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 12px;">
            <span>🟢 A/B = Excellent</span>
            <span>🟡 C = Moyen</span>
            <span>🟠 D = Faible</span>
            <span>🔴 F = Critique</span>
            <span style="margin-left: 20px;">|</span>
            <span>🚀 Scale</span>
            <span>⚡ Test</span>
            <span>👁️ Monitor</span>
            <span>⏸️ Pause</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # ===== TABLEAUX DÉTAILLÉS PAR SCORE =====
        st.subheader("📊 Détail des scores par dimension")
        
        # Fonctions de formatage avec couleurs
        def format_metric_color(value, thresholds, inverse=False, suffix="", decimals=2):
            """Formate une métrique avec couleur selon seuils. inverse=True si une valeur basse est meilleure."""
            if pd.isna(value) or value == 0:
                return "⚪ -"
            
            low, mid, high = thresholds
            
            if inverse:
                if value <= low:
                    color = "🟢"
                elif value <= mid:
                    color = "🟡"
                elif value <= high:
                    color = "🟠"
                else:
                    color = "🔴"
            else:
                if value >= high:
                    color = "🟢"
                elif value >= mid:
                    color = "🟡"
                elif value >= low:
                    color = "🟠"
                else:
                    color = "🔴"
            
            if decimals == 0:
                return f"{color} {value:,.0f}{suffix}"
            else:
                return f"{color} {value:.{decimals}f}{suffix}"
        
        def format_score_color(score):
            """Formate un score avec couleur et grade."""
            grade = get_grade(score)
            if score >= 70:
                return f"🟢 {score} ({grade})"
            elif score >= 60:
                return f"🟢 {score} ({grade})"
            elif score >= 50:
                return f"🟡 {score} ({grade})"
            elif score >= 40:
                return f"🟠 {score} ({grade})"
            else:
                return f"🔴 {score} ({grade})"
        
        # Calculer les statistiques pour les seuils dynamiques
        roas_q25, roas_q50, roas_q75 = filtered_df['roas'].quantile([0.25, 0.5, 0.75])
        cpa_q25, cpa_q50, cpa_q75 = filtered_df[filtered_df['cpa_calc'] > 0]['cpa_calc'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpa_calc'] > 0]) > 0 else (10, 20, 40)
        cvr_q25, cvr_q50, cvr_q75 = filtered_df[filtered_df['cvr'] > 0]['cvr'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cvr'] > 0]) > 0 else (1, 2, 5)
        
        ctr_q25, ctr_q50, ctr_q75 = filtered_df['ctr_lien'].quantile([0.25, 0.5, 0.75])
        cpc_q25, cpc_q50, cpc_q75 = filtered_df[filtered_df['cpc_lien'] > 0]['cpc_lien'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpc_lien'] > 0]) > 0 else (0.2, 0.5, 1)
        clics_q25, clics_q50, clics_q75 = filtered_df['clics_lien'].quantile([0.25, 0.5, 0.75])
        
        cpm_q25, cpm_q50, cpm_q75 = filtered_df[filtered_df['cpm'] > 0]['cpm'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpm'] > 0]) > 0 else (2, 5, 10)
        reach_q25, reach_q50, reach_q75 = filtered_df['reach'].quantile([0.25, 0.5, 0.75])
        
        # Onglets pour les 3 tableaux
        tab_profit, tab_trafic, tab_notoriete, tab_tendance = st.tabs(["💰 Score Profit", "🚀 Score Trafic", "👁️ Score Notoriété", "📈 Score Tendance"])
        
        # ===== TABLEAU PROFIT =====
        with tab_profit:
            st.markdown("""
            **Composition du score Profit :** ROAS (45%) + CPA inversé (35%) + CVR (20%)
            
            *Plus le ROAS et le CVR sont élevés, meilleur est le score. Plus le CPA est bas, meilleur est le score.*
            """)
            
            profit_df = filtered_df[['nom', 'format', 'roas', 'cpa_calc', 'cvr', 'achats', 'depense', 'score_profitabilite', 'action']].copy()
            
            # Formater les colonnes
            profit_df['Nom'] = profit_df['nom']
            profit_df['ROAS'] = profit_df['roas'].apply(
                lambda x: format_metric_color(x, (roas_q25, roas_q50, roas_q75), inverse=False, decimals=2)
            )
            profit_df['CPA €'] = profit_df['cpa_calc'].apply(
                lambda x: format_metric_color(x, (cpa_q25, cpa_q50, cpa_q75), inverse=True, suffix="€", decimals=2)
            )
            profit_df['CVR %'] = profit_df['cvr'].apply(
                lambda x: format_metric_color(x, (cvr_q25, cvr_q50, cvr_q75), inverse=False, suffix="%", decimals=2)
            )
            profit_df['Achats'] = profit_df['achats'].apply(lambda x: f"{x:,.0f}")
            profit_df['Dépense €'] = profit_df['depense'].apply(lambda x: f"{x:.2f}€")
            profit_df['Score'] = profit_df['score_profitabilite'].apply(format_score_color)
            
            action_format = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
            profit_df['Act.'] = profit_df['action'].map(action_format)
            
            # Calculer la hauteur dynamique (35px par ligne + 40px header)
            table_height = min(2000, 40 + len(profit_df) * 35)
            
            # Afficher
            st.dataframe(
                profit_df[['format', 'Nom', 'ROAS', 'CPA €', 'CVR %', 'Achats', 'Dépense €', 'Score', 'Act.']],
                use_container_width=True,
                height=table_height,
                column_config={
                    "format": st.column_config.TextColumn("Format", width=60),
                    "Nom": st.column_config.TextColumn("Nom", width=350),
                    "ROAS": st.column_config.TextColumn("ROAS", width=80),
                    "CPA €": st.column_config.TextColumn("CPA", width=90),
                    "CVR %": st.column_config.TextColumn("CVR", width=90),
                    "Achats": st.column_config.TextColumn("Achats", width=70),
                    "Dépense €": st.column_config.TextColumn("Dépense", width=80),
                    "Score": st.column_config.TextColumn("Score", width=100),
                    "Act.": st.column_config.TextColumn("", width=40),
                },
                hide_index=True
            )
            
            # Légende
            st.caption("🟢 Excellent (top 25%) | 🟡 Bon (médiane) | 🟠 Moyen (bottom 25%) | 🔴 Faible | *CPA : plus bas = meilleur*")
        
        # ===== TABLEAU TRAFIC =====
        with tab_trafic:
            st.markdown("""
            **Composition du score Trafic :** CTR (50%) + CPC inversé (30%) + Clics (20%)
            
            *Plus le CTR et les clics sont élevés, meilleur est le score. Plus le CPC est bas, meilleur est le score.*
            """)
            
            trafic_df = filtered_df[['nom', 'format', 'ctr_lien', 'cpc_lien', 'clics_lien', 'impressions', 'score_trafic', 'action']].copy()
            
            # Formater les colonnes
            trafic_df['Nom'] = trafic_df['nom']
            trafic_df['CTR %'] = trafic_df['ctr_lien'].apply(
                lambda x: format_metric_color(x, (ctr_q25, ctr_q50, ctr_q75), inverse=False, suffix="%", decimals=2)
            )
            trafic_df['CPC €'] = trafic_df['cpc_lien'].apply(
                lambda x: format_metric_color(x, (cpc_q25, cpc_q50, cpc_q75), inverse=True, suffix="€", decimals=2)
            )
            trafic_df['Clics'] = trafic_df['clics_lien'].apply(
                lambda x: format_metric_color(x, (clics_q25, clics_q50, clics_q75), inverse=False, decimals=0)
            )
            trafic_df['Impressions'] = trafic_df['impressions'].apply(lambda x: f"{x:,.0f}")
            trafic_df['Score'] = trafic_df['score_trafic'].apply(format_score_color)
            
            action_format = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
            trafic_df['Act.'] = trafic_df['action'].map(action_format)
            
            # Calculer la hauteur dynamique (35px par ligne + 40px header)
            table_height = min(2000, 40 + len(trafic_df) * 35)
            
            # Afficher
            st.dataframe(
                trafic_df[['format', 'Nom', 'CTR %', 'CPC €', 'Clics', 'Impressions', 'Score', 'Act.']],
                use_container_width=True,
                height=table_height,
                column_config={
                    "format": st.column_config.TextColumn("Format", width=60),
                    "Nom": st.column_config.TextColumn("Nom", width=350),
                    "CTR %": st.column_config.TextColumn("CTR", width=90),
                    "CPC €": st.column_config.TextColumn("CPC", width=90),
                    "Clics": st.column_config.TextColumn("Clics", width=90),
                    "Impressions": st.column_config.TextColumn("Impr.", width=90),
                    "Score": st.column_config.TextColumn("Score", width=100),
                    "Act.": st.column_config.TextColumn("", width=40),
                },
                hide_index=True
            )
            
            # Légende
            st.caption("🟢 Excellent (top 25%) | 🟡 Bon (médiane) | 🟠 Moyen (bottom 25%) | 🔴 Faible | *CPC : plus bas = meilleur*")
        
        # ===== TABLEAU NOTORIÉTÉ =====
        with tab_notoriete:
            st.markdown("""
            **Composition du score Notoriété :** CPMu inversé (50%) + Couverture (50%)
            
            *CPMu = Coût pour 1000 personnes uniques. Plus la couverture est élevée et le CPMu bas, meilleur est le score.*
            """)
            
            # Calculer les quartiles pour CPMu
            cpmu_q25, cpmu_q50, cpmu_q75 = filtered_df[filtered_df['cpmu'] > 0]['cpmu'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpmu'] > 0]) > 0 else (2, 5, 10)
            
            notoriete_df = filtered_df[['nom', 'format', 'cpmu', 'cpm', 'reach', 'impressions', 'frequency', 'score_notoriete', 'action']].copy()
            
            # Formater les colonnes
            notoriete_df['Nom'] = notoriete_df['nom']
            notoriete_df['CPMu €'] = notoriete_df['cpmu'].apply(
                lambda x: format_metric_color(x, (cpmu_q25, cpmu_q50, cpmu_q75), inverse=True, suffix="€", decimals=2)
            )
            notoriete_df['CPM €'] = notoriete_df['cpm'].apply(
                lambda x: format_metric_color(x, (cpm_q25, cpm_q50, cpm_q75), inverse=True, suffix="€", decimals=2)
            )
            notoriete_df['Couverture'] = notoriete_df['reach'].apply(
                lambda x: format_metric_color(x, (reach_q25, reach_q50, reach_q75), inverse=False, decimals=0)
            )
            notoriete_df['Impressions'] = notoriete_df['impressions'].apply(lambda x: f"{x:,.0f}")
            notoriete_df['Frequency'] = notoriete_df['frequency'].apply(
                lambda x: f"{'🟢' if x < 2 else '🟡' if x < 3 else '🔴'} {x:.2f}"
            )
            notoriete_df['Score'] = notoriete_df['score_notoriete'].apply(format_score_color)
            
            action_format = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
            notoriete_df['Act.'] = notoriete_df['action'].map(action_format)
            
            # Calculer la hauteur dynamique (35px par ligne + 40px header)
            table_height = min(2000, 40 + len(notoriete_df) * 35)
            
            # Afficher
            st.dataframe(
                notoriete_df[['format', 'Nom', 'CPMu €', 'CPM €', 'Couverture', 'Impressions', 'Frequency', 'Score', 'Act.']],
                use_container_width=True,
                height=table_height,
                column_config={
                    "format": st.column_config.TextColumn("Format", width=60),
                    "Nom": st.column_config.TextColumn("Nom", width=300),
                    "CPMu €": st.column_config.TextColumn("CPMu (50%)", width=100),
                    "CPM €": st.column_config.TextColumn("CPM", width=85),
                    "Couverture": st.column_config.TextColumn("Couverture (50%)", width=120),
                    "Impressions": st.column_config.TextColumn("Impr.", width=80),
                    "Frequency": st.column_config.TextColumn("Freq.", width=75),
                    "Score": st.column_config.TextColumn("Score", width=100),
                    "Act.": st.column_config.TextColumn("", width=40),
                },
                hide_index=True
            )
            
            # Légende
            st.caption("🟢 Excellent (top 25%) | 🟡 Bon (médiane) | 🟠 Moyen (bottom 25%) | 🔴 Faible | *CPMu/CPM : plus bas = meilleur* | *Frequency : <2 🟢, 2-3 🟡, >3 🔴*")
        
        # ===== TABLEAU TENDANCE =====
        with tab_tendance:
            st.markdown("""
            **Composition du score Tendance :** Δ CTR (40%) + Δ CPC inversé (25%) + Δ CPM inversé (20%) + Δ Impressions (15%)
            
            *Comparaison 7 derniers jours vs 7 jours précédents. Une hausse du CTR/Impressions est positive, une hausse du CPC/CPM est négative.*
            """)
            
            if not has_daily:
                st.warning("⚠️ Chargez les données quotidiennes pour voir les tendances.")
            else:
                tendance_df = filtered_df[['nom', 'format', 'trend_ctr', 'trend_cpm', 'trend_score', 'action']].copy()
                
                # Ajouter les autres métriques de tendance depuis le dict trends
                tendance_df['trend_cpc'] = tendance_df['nom'].apply(lambda x: trends.get(x, {}).get('cpc', 0))
                tendance_df['trend_impr'] = tendance_df['nom'].apply(lambda x: trends.get(x, {}).get('impressions', 0))
                
                # Fonction pour formater les variations avec couleur
                def format_trend_metric(value, inverse=False):
                    """Formate une variation avec couleur. inverse=True si une hausse est négative."""
                    if pd.isna(value) or value == 0:
                        return "⚪ 0%"
                    
                    if inverse:
                        # Pour CPC et CPM : baisse = bon (vert), hausse = mauvais (rouge)
                        if value <= -20:
                            color = "🟢"
                        elif value <= -5:
                            color = "🟢"
                        elif value <= 5:
                            color = "⚪"
                        elif value <= 20:
                            color = "🟠"
                        else:
                            color = "🔴"
                    else:
                        # Pour CTR et Impressions : hausse = bon (vert), baisse = mauvais (rouge)
                        if value >= 20:
                            color = "🟢"
                        elif value >= 5:
                            color = "🟢"
                        elif value >= -5:
                            color = "⚪"
                        elif value >= -20:
                            color = "🟠"
                        else:
                            color = "🔴"
                    
                    sign = "+" if value > 0 else ""
                    return f"{color} {sign}{value:.0f}%"
                
                def format_trend_score(score):
                    """Formate le score de tendance avec couleur."""
                    if score >= 20:
                        return f"🟢 +{score:.0f} (Excellent)"
                    elif score >= 5:
                        return f"🟢 +{score:.0f} (Bon)"
                    elif score >= -5:
                        return f"⚪ {score:+.0f} (Stable)"
                    elif score >= -20:
                        return f"🟠 {score:.0f} (Baisse)"
                    else:
                        return f"🔴 {score:.0f} (Chute)"
                
                # Formater les colonnes
                tendance_df['Nom'] = tendance_df['nom']
                tendance_df['Δ CTR'] = tendance_df['trend_ctr'].apply(lambda x: format_trend_metric(x, inverse=False))
                tendance_df['Δ CPC'] = tendance_df['trend_cpc'].apply(lambda x: format_trend_metric(x, inverse=True))
                tendance_df['Δ CPM'] = tendance_df['trend_cpm'].apply(lambda x: format_trend_metric(x, inverse=True))
                tendance_df['Δ Impr.'] = tendance_df['trend_impr'].apply(lambda x: format_trend_metric(x, inverse=False))
                tendance_df['Score'] = tendance_df['trend_score'].apply(format_trend_score)
                
                action_format = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
                tendance_df['Act.'] = tendance_df['action'].map(action_format)
                
                # Trier par score de tendance
                tendance_df = tendance_df.sort_values('trend_score', ascending=False)
                
                # Calculer la hauteur dynamique
                table_height = min(2000, 40 + len(tendance_df) * 35)
                
                # Afficher
                st.dataframe(
                    tendance_df[['format', 'Nom', 'Δ CTR', 'Δ CPC', 'Δ CPM', 'Δ Impr.', 'Score', 'Act.']],
                    use_container_width=True,
                    height=table_height,
                    column_config={
                        "format": st.column_config.TextColumn("Format", width=60),
                        "Nom": st.column_config.TextColumn("Nom", width=350),
                        "Δ CTR": st.column_config.TextColumn("Δ CTR (40%)", width=100),
                        "Δ CPC": st.column_config.TextColumn("Δ CPC (25%)", width=100),
                        "Δ CPM": st.column_config.TextColumn("Δ CPM (20%)", width=100),
                        "Δ Impr.": st.column_config.TextColumn("Δ Impr. (15%)", width=100),
                        "Score": st.column_config.TextColumn("Score Tendance", width=130),
                        "Act.": st.column_config.TextColumn("", width=40),
                    },
                    hide_index=True
                )
                
                # Légende
                st.caption("🟢 Amélioration | ⚪ Stable (-5% à +5%) | 🟠 Légère baisse | 🔴 Forte baisse | *CPC/CPM : baisse = 🟢, hausse = 🔴*")
        
        st.divider()
        
        # Détail d'une créative sélectionnée
        st.subheader("🔍 Détail créative")
        selected_creative = st.selectbox(
            "Sélectionner une créative pour voir le détail",
            options=filtered_df['nom'].tolist(),
            format_func=lambda x: f"{filtered_df[filtered_df['nom']==x]['format'].values[0]} | {x}"
        )
        
        if selected_creative:
            row = filtered_df[filtered_df['nom'] == selected_creative].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📊 Métriques**")
                st.write(f"Impressions: {row['impressions']:,.0f}")
                st.write(f"Clics: {row['clics_lien']:,.0f}")
                st.write(f"CTR: {row['ctr_lien']:.2f}%")
                st.write(f"CPC: {row['cpc_lien']:.2f}€")
                st.write(f"CPM: {row['cpm']:.2f}€")
            
            with col2:
                st.markdown("**💰 Conversions**")
                st.write(f"Achats: {row['achats']:,.0f}")
                st.write(f"ROAS: {row['roas']:.2f}")
                st.write(f"Dépense: {row['depense']:.2f}€")
                st.write(f"Frequency: {row['frequency']:.2f}")
                st.write(f"Confiance: {row['coefficient_confiance']*100:.0f}%")
            
            with col3:
                st.markdown("**🎯 Scores**")
                st.write(f"Profit: {row['score_profitabilite']} ({get_grade(row['score_profitabilite'])})")
                st.write(f"Trafic: {row['score_trafic']} ({get_grade(row['score_trafic'])})")
                st.write(f"Notoriété: {row['score_notoriete']} ({get_grade(row['score_notoriete'])})")
                st.write(f"Global: {row['score_global']} ({get_grade(row['score_global'])})")
                st.write(f"**Potentiel: {row['scale_potential']}**")
            
            # Graphique d'évolution multi-métriques
            if has_daily and selected_creative in sparklines:
                st.markdown("---")
                st.markdown("**📈 Évolution des métriques**")
                
                # Sélection de la plage de dates
                col_date1, col_date2 = st.columns([1, 2])
                
                with col_date1:
                    date_range_option = st.selectbox(
                        "Plage de dates",
                        options=["7 derniers jours", "14 derniers jours", "30 derniers jours", "Personnalisé"],
                        index=1
                    )
                
                # Récupérer toutes les données disponibles
                sparkline_data_full = sparklines[selected_creative]
                all_dates = [d.get('date', '') for d in sparkline_data_full]
                
                if all_dates:
                    min_date = datetime.strptime(min(all_dates), '%Y-%m-%d').date()
                    max_date = datetime.strptime(max(all_dates), '%Y-%m-%d').date()
                    
                    # Déterminer les dates de début et fin selon l'option choisie
                    if date_range_option == "7 derniers jours":
                        start_date = max_date - timedelta(days=6)
                        end_date = max_date
                    elif date_range_option == "14 derniers jours":
                        start_date = max_date - timedelta(days=13)
                        end_date = max_date
                    elif date_range_option == "30 derniers jours":
                        start_date = max_date - timedelta(days=29)
                        end_date = max_date
                    else:  # Personnalisé
                        with col_date2:
                            date_col1, date_col2 = st.columns(2)
                            with date_col1:
                                start_date = st.date_input(
                                    "Date de début",
                                    value=max_date - timedelta(days=13),
                                    min_value=min_date,
                                    max_value=max_date
                                )
                            with date_col2:
                                end_date = st.date_input(
                                    "Date de fin",
                                    value=max_date,
                                    min_value=min_date,
                                    max_value=max_date
                                )
                    
                    # Filtrer les données selon la plage sélectionnée
                    sparkline_data = [
                        d for d in sparkline_data_full 
                        if start_date <= datetime.strptime(d.get('date', '2000-01-01'), '%Y-%m-%d').date() <= end_date
                    ]
                    
                    # Afficher la plage sélectionnée
                    st.caption(f"📅 Du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')} ({len(sparkline_data)} jours)")
                
                # Sélection des métriques à afficher
                available_metrics = {
                    'CTR (%)': 'ctr',
                    'CPM (€)': 'cpm',
                    'CPMu (€)': 'cpmu',
                    'Impressions': 'impressions',
                    'Dépense (€)': 'depense'
                }
                
                selected_metrics = st.multiselect(
                    "Sélectionner les métriques à afficher",
                    options=list(available_metrics.keys()),
                    default=['CTR (%)'],
                    help="CPMu = Coût pour 1000 personnes uniques (Dépense/Reach × 1000)"
                )
                
                if selected_metrics and sparkline_data:
                    
                    # Créer le graphique
                    fig = go.Figure()
                    
                    # Couleurs pour chaque métrique
                    colors = {
                        'CTR (%)': '#10B981',
                        'CPM (€)': '#F59E0B', 
                        'CPMu (€)': '#EF4444',
                        'Impressions': '#3B82F6',
                        'Dépense (€)': '#8B5CF6'
                    }
                    
                    # Vérifier si on a besoin d'un axe secondaire (échelles très différentes)
                    use_secondary = len(selected_metrics) > 1 and 'Impressions' in selected_metrics
                    
                    for metric_label in selected_metrics:
                        metric_key = available_metrics[metric_label]
                        values = [d.get(metric_key, 0) for d in sparkline_data]
                        dates = [d.get('date', '') for d in sparkline_data]
                        
                        # Utiliser axe secondaire pour Impressions si autres métriques sélectionnées
                        use_y2 = use_secondary and metric_label == 'Impressions'
                        
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=values,
                            mode='lines+markers',
                            name=metric_label,
                            line=dict(color=colors.get(metric_label, '#6B7280'), width=2),
                            marker=dict(size=6),
                            yaxis='y2' if use_y2 else 'y'
                        ))
                    
                    # Configuration du layout
                    layout_config = dict(
                        height=400,
                        xaxis=dict(
                            title="Date",
                            tickangle=45,
                            showgrid=True,
                            gridcolor='rgba(0,0,0,0.1)'
                        ),
                        yaxis=dict(
                            title=selected_metrics[0] if len(selected_metrics) == 1 else "Valeur",
                            showgrid=True,
                            gridcolor='rgba(0,0,0,0.1)'
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="left",
                            x=0
                        ),
                        hovermode='x unified',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Ajouter axe Y secondaire si nécessaire
                    if use_secondary:
                        layout_config['yaxis2'] = dict(
                            title="Impressions",
                            overlaying='y',
                            side='right',
                            showgrid=False
                        )
                    
                    fig.update_layout(**layout_config)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Afficher les variations sur la période sélectionnée
                    st.markdown("**📊 Variations sur la période**")
                    var_cols = st.columns(len(selected_metrics))
                    
                    for i, metric_label in enumerate(selected_metrics):
                        metric_key = available_metrics[metric_label]
                        values = [d.get(metric_key, 0) for d in sparkline_data]
                        
                        if len(values) >= 2:
                            # Calculer la moyenne de la première moitié vs deuxième moitié
                            mid = len(values) // 2
                            first_half = [v for v in values[:mid] if v > 0]
                            second_half = [v for v in values[mid:] if v > 0]
                            
                            recent = np.mean(second_half) if second_half else 0
                            previous = np.mean(first_half) if first_half else 0
                            
                            if previous > 0:
                                variation = ((recent - previous) / previous) * 100
                                with var_cols[i]:
                                    # CTR et Impressions : hausse = vert, baisse = rouge
                                    # CPM et Dépense : hausse = rouge, baisse = vert
                                    delta_color = "normal" if metric_label in ['CTR (%)', 'Impressions'] else "inverse"
                                    st.metric(
                                        metric_label,
                                        f"{recent:.2f}" if metric_key != 'impressions' else f"{recent:,.0f}",
                                        f"{variation:+.1f}%",
                                        delta_color=delta_color
                                    )
                            else:
                                with var_cols[i]:
                                    current_val = np.mean([v for v in values if v > 0]) if any(v > 0 for v in values) else 0
                                    st.metric(
                                        metric_label,
                                        f"{current_val:.2f}" if metric_key != 'impressions' else f"{current_val:,.0f}",
                                        "N/A"
                                    )
                else:
                    st.info("👆 Sélectionnez au moins une métrique pour voir le graphique")
            
            st.info(f"**Recommandation:** {row['recommendation']}")
        
        st.divider()
        
        # Export
        st.download_button(
            "📥 Exporter CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name=f"meta_ads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime='text/csv'
        )
    
    # ========== TAB 5: Comparateur ==========
    with tab5:
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
                    '💰 Profit': f"{row['score_profitabilite']} ({get_grade(row['score_profitabilite'])})",
                    '🚀 Trafic': f"{row['score_trafic']} ({get_grade(row['score_trafic'])})",
                    '👁️ Notoriété': f"{row['score_notoriete']} ({get_grade(row['score_notoriete'])})",
                    '⭐ Global': f"{row['score_global']} ({get_grade(row['score_global'])})",
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
