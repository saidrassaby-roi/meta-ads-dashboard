"""
Meta Ads Creative Intelligence Dashboard V3
============================================
Design moderne inspiré de Nexus Dashboard.

Auteur: BNB Solutions Digitales
Version: 3.0
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

# CSS moderne inspiré de Nexus
def get_modern_css(dark_mode=False):
    if dark_mode:
        bg_primary = "#0f0f1a"
        bg_secondary = "#1a1a2e"
        bg_card = "#252540"
        text_primary = "#ffffff"
        text_secondary = "#a0a0b0"
        border_color = "#3a3a5c"
        accent_color = "#6366f1"
        accent_light = "#818cf8"
    else:
        bg_primary = "#f8fafc"
        bg_secondary = "#ffffff"
        bg_card = "#ffffff"
        text_primary = "#1e293b"
        text_secondary = "#64748b"
        border_color = "#e2e8f0"
        accent_color = "#6366f1"
        accent_light = "#a5b4fc"
    
    return f"""
    <style>
        /* Global styles */
        .stApp {{
            background-color: {bg_primary};
        }}
        
        /* Hide default Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {bg_secondary};
            border-right: 1px solid {border_color};
        }}
        
        [data-testid="stSidebar"] .block-container {{
            padding-top: 1rem;
        }}
        
        /* Main container */
        .main .block-container {{
            padding: 1rem 2rem 2rem 2rem;
            max-width: 100%;
        }}
        
        /* Modern header */
        .dashboard-header {{
            background: linear-gradient(135deg, {accent_color} 0%, #8b5cf6 50%, #a855f7 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        }}
        
        .dashboard-header h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.025em;
        }}
        
        .dashboard-header p {{
            font-size: 0.9rem;
            opacity: 0.9;
            margin: 0.25rem 0 0 0;
        }}
        
        /* Metric cards */
        .metric-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }}
        
        .metric-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .metric-icon {{
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
        }}
        
        .metric-icon.purple {{ background: rgba(139, 92, 246, 0.15); }}
        .metric-icon.green {{ background: rgba(16, 185, 129, 0.15); }}
        .metric-icon.blue {{ background: rgba(59, 130, 246, 0.15); }}
        .metric-icon.orange {{ background: rgba(249, 115, 22, 0.15); }}
        .metric-icon.red {{ background: rgba(239, 68, 68, 0.15); }}
        
        .metric-label {{
            font-size: 0.8rem;
            color: {text_secondary};
            font-weight: 500;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .metric-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {text_primary};
            line-height: 1.2;
        }}
        
        .metric-change {{
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.25rem;
        }}
        
        .metric-change.positive {{ color: #10b981; }}
        .metric-change.negative {{ color: #ef4444; }}
        .metric-change.neutral {{ color: {text_secondary}; }}
        
        /* Section cards */
        .section-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .section-title {{
            font-size: 1rem;
            font-weight: 600;
            color: {text_primary};
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Action cards */
        .action-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid;
            transition: all 0.2s ease;
        }}
        
        .action-card:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .action-card.scale {{ border-left-color: #10b981; background: {'#0d2818' if dark_mode else '#ecfdf5'}; }}
        .action-card.test {{ border-left-color: #3b82f6; background: {'#0c1929' if dark_mode else '#eff6ff'}; }}
        .action-card.monitor {{ border-left-color: #f59e0b; background: {'#1c1608' if dark_mode else '#fffbeb'}; }}
        .action-card.pause {{ border-left-color: #ef4444; background: {'#1c0808' if dark_mode else '#fef2f2'}; }}
        
        .action-card-title {{
            font-weight: 600;
            font-size: 0.9rem;
            color: {text_primary};
            margin-bottom: 0.25rem;
        }}
        
        .action-card-subtitle {{
            font-size: 0.8rem;
            color: {text_secondary};
        }}
        
        .action-card-metrics {{
            font-size: 0.75rem;
            color: {text_secondary};
            margin-top: 0.5rem;
        }}
        
        /* Alert cards */
        .alert-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid #ef4444;
        }}
        
        .warning-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid #f59e0b;
        }}
        
        .info-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid #3b82f6;
        }}
        
        /* Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .badge-success {{ background: rgba(16, 185, 129, 0.15); color: #10b981; }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.15); color: #f59e0b; }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.15); color: #ef4444; }}
        .badge-info {{ background: rgba(59, 130, 246, 0.15); color: #3b82f6; }}
        .badge-purple {{ background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }}
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background-color: transparent;
            padding: 0.5rem;
            border-radius: 12px;
            background: {bg_secondary};
            border: 1px solid {border_color};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            color: {text_secondary};
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {accent_color} !important;
            color: white !important;
        }}
        
        /* Dataframe styling */
        .stDataFrame {{
            border-radius: 12px;
            overflow: hidden;
        }}
        
        /* Input styling */
        .stTextInput > div > div > input {{
            border-radius: 10px;
            border: 1px solid {border_color};
            background: {bg_card};
        }}
        
        .stSelectbox > div > div {{
            border-radius: 10px;
        }}
        
        /* Button styling */
        .stButton > button {{
            border-radius: 10px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background: {bg_card};
            border-radius: 10px;
            border: 1px solid {border_color};
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {bg_primary};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {border_color};
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {text_secondary};
        }}
        
        /* Progress bar styling */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {accent_color}, #8b5cf6);
            border-radius: 10px;
        }}
        
        /* Metric delta styling override */
        [data-testid="stMetricDelta"] {{
            font-size: 0.85rem;
        }}
        
        /* Sidebar sections */
        .sidebar-section {{
            padding: 0.75rem 0;
            border-bottom: 1px solid {border_color};
        }}
        
        .sidebar-section-title {{
            font-size: 0.7rem;
            font-weight: 600;
            color: {text_secondary};
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.75rem;
        }}
        
        /* Summary row */
        .summary-row {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        /* Plotly chart container */
        .js-plotly-plot {{
            border-radius: 12px;
        }}
    </style>
    """


def render_metric_card(icon, label, value, change=None, change_type="neutral", icon_color="purple"):
    """Render a modern metric card."""
    change_class = f"metric-change {change_type}"
    change_html = f'<div class="{change_class}">{change}</div>' if change else ''
    
    return f"""
    <div class="metric-card">
        <div class="metric-icon {icon_color}">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """


def render_action_card(format_type, name, recommendation, metrics, action_type, trend_badge=""):
    """Render a modern action card."""
    return f"""
    <div class="action-card {action_type}">
        <div class="action-card-title">
            <span style="opacity: 0.7;">{format_type}</span> · {name[:45]}{'...' if len(name) > 45 else ''} {trend_badge}
        </div>
        <div class="action-card-subtitle">{recommendation}</div>
        <div class="action-card-metrics">{metrics}</div>
    </div>
    """


# ============================================================================
# FONCTIONS DE TRAITEMENT (identiques à V2.3)
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
        
        sparkline_data = []
        dates = pd.date_range(start=date_30j, end=date_max, freq='D')
        
        for d in dates:
            row = df_30j[df_30j['date'].dt.date == d.date()]
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
    
    roas_mean, roas_std = calc_stats(df['roas'])
    ctr_mean, ctr_std = calc_stats(df['ctr_lien'])
    cpc_mean, cpc_std = calc_stats(df['cpc_lien'])
    cpm_mean, cpm_std = calc_stats(df['cpm'])
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
    
    for _, row in df.iterrows():
        nom = row['nom']
        
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
        
        if len(data) >= 2:
            yesterday = data[-2]
            today = data[-1]
            
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
        
        if nom in sparklines and len(sparklines[nom]) >= 7:
            data = sparklines[nom]
            impressions_recent = sum(d.get('impressions', 0) for d in data[-7:])
            impressions_old = sum(d.get('impressions', 0) for d in data[:7]) if len(data) >= 14 else impressions_recent
            
            if impressions_old > 0 and impressions_recent > 0:
                growth_rate = (impressions_recent / impressions_old - 1) / 7 * 0.1
            else:
                growth_rate = 0.05
        else:
            growth_rate = 0.05
        
        if growth_rate > 0 and current_freq < 4:
            days_to_fatigue = int((4 - current_freq) / (current_freq * growth_rate))
            days_to_fatigue = max(1, min(days_to_fatigue, 60))
        else:
            days_to_fatigue = 30
        
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
    
    predictions.sort(key=lambda x: x['days_to_fatigue'])
    return predictions


def calculate_diversification_score(df):
    """Calcule le score de diversification et détecte les concentrations de budget."""
    alerts = []
    
    total_budget = df['depense'].sum()
    
    if total_budget == 0:
        return {'score': 100, 'alerts': [], 'by_usp': {}, 'by_hook': {}, 'by_format': {}}
    
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
    
    max_usp_pct = max(usp_pct.values()) if usp_pct else 0
    max_hook_pct = max(hook_pct.values()) if hook_pct else 0
    max_format_pct = max(format_pct.values()) if format_pct else 0
    
    score = 100 - (max_usp_pct * 0.4 + max_hook_pct * 0.35 + max_format_pct * 0.25) * 0.7
    score = max(0, min(100, score))
    
    return {
        'score': round(score),
        'alerts': alerts,
        'by_usp': usp_pct,
        'by_hook': hook_pct,
        'by_format': format_pct
    }


# ============================================================================
# INTERFACE UTILISATEUR MODERNE
# ============================================================================

def main():
    # Appliquer le CSS moderne
    st.markdown(get_modern_css(st.session_state.dark_mode), unsafe_allow_html=True)
    
    # Header moderne
    st.markdown("""
    <div class="dashboard-header">
        <h1>🎯 Creative Intelligence Dashboard</h1>
        <p>Pilotage intelligent de vos créatives Meta Ads</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar moderne
    with st.sidebar:
        # Logo et toggle theme
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("### 🎯 Creative Intel")
        with col2:
            if st.button("🌙" if not st.session_state.dark_mode else "☀️", key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        st.markdown("---")
        
        # Section Import
        st.markdown('<div class="sidebar-section-title">📁 IMPORT</div>', unsafe_allow_html=True)
        
        import_mode = st.radio(
            "Mode",
            ["Agrégées seules", "Agrégées + Quotidiennes"],
            label_visibility="collapsed"
        )
        
        uploaded_main = st.file_uploader("📄 Données agrégées", type=['csv'], key="main_file", label_visibility="collapsed")
        if uploaded_main:
            st.success(f"✓ {uploaded_main.name[:20]}...")
        
        uploaded_daily = None
        if import_mode == "Agrégées + Quotidiennes":
            uploaded_daily = st.file_uploader("📈 Données quotidiennes", type=['csv'], key="daily_file", label_visibility="collapsed")
            if uploaded_daily:
                st.success(f"✓ {uploaded_daily.name[:20]}...")
        
        st.markdown("---")
        
        # Section Filtres
        st.markdown('<div class="sidebar-section-title">⚙️ FILTRES</div>', unsafe_allow_html=True)
        min_impressions = st.slider("Impressions min", 0, 10000, 500, 100)
        
        st.markdown("---")
        
        # Légende
        st.markdown('<div class="sidebar-section-title">📖 LÉGENDE</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.8rem;">
            🚀 <strong>Scale</strong> - Augmenter budget<br>
            ⚡ <strong>Test</strong> - Valider potentiel<br>
            👁️ <strong>Monitor</strong> - Surveiller<br>
            ⏸️ <strong>Pause</strong> - Arrêter
        </div>
        """, unsafe_allow_html=True)
    
    # Page principale
    if uploaded_main is None:
        # Welcome state
        st.markdown("""
        <div class="section-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h2 style="margin-bottom: 0.5rem;">Bienvenue !</h2>
            <p style="color: #64748b;">Importez vos données Meta Ads pour commencer l'analyse.</p>
        </div>
        """, unsafe_allow_html=True)
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
            except Exception as e:
                st.sidebar.warning(f"⚠️ Erreur: {str(e)}")
        
        df = calculate_scores(df, trends)
        
        if len(df) == 0:
            st.warning("⚠️ Aucune créative avec assez d'impressions.")
            return
            
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return
    
    # ===== MÉTRIQUES GLOBALES =====
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_spend = df['depense'].sum()
    total_revenue = df['valeur_achats'].sum()
    avg_roas = total_revenue / total_spend if total_spend > 0 else 0
    total_achats = df['achats'].sum()
    avg_ctr = df['ctr_lien'].mean()
    
    action_counts = df['action'].value_counts()
    scale_count = action_counts.get('scale', 0)
    
    with col1:
        st.markdown(render_metric_card(
            "💰", "Dépense totale", f"{total_spend:,.0f}€",
            None, "neutral", "purple"
        ), unsafe_allow_html=True)
    
    with col2:
        roas_change = "positive" if avg_roas >= 3 else "negative" if avg_roas < 1.5 else "neutral"
        st.markdown(render_metric_card(
            "📈", "ROAS moyen", f"{avg_roas:.2f}",
            f"{'✓ Rentable' if avg_roas >= 2 else '⚠ À améliorer'}", roas_change, "green"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_metric_card(
            "🛒", "Achats", f"{total_achats:,.0f}",
            None, "neutral", "blue"
        ), unsafe_allow_html=True)
    
    with col4:
        ctr_change = "positive" if avg_ctr >= 1.5 else "negative" if avg_ctr < 0.8 else "neutral"
        st.markdown(render_metric_card(
            "👆", "CTR moyen", f"{avg_ctr:.2f}%",
            None, ctr_change, "orange"
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(render_metric_card(
            "🚀", "À scaler", f"{scale_count}",
            f"sur {len(df)} créatives", "positive" if scale_count > 0 else "neutral", "green"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Actions du jour",
        "🚨 Alertes",
        "📊 Angles créatifs", 
        "📈 Tableau détaillé",
        "⚖️ Comparateur"
    ])
    
    # ========== TAB 1: Actions du jour ==========
    with tab1:
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚀 À scaler", action_counts.get('scale', 0))
        with col2:
            st.metric("⚡ À tester", action_counts.get('test', 0))
        with col3:
            st.metric("👁️ À surveiller", action_counts.get('monitor', 0))
        with col4:
            st.metric("⏸️ À pauser", action_counts.get('pause', 0))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Actions layout
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Scale section
            st.markdown('<div class="section-title">🚀 Créatives à scaler</div>', unsafe_allow_html=True)
            scale_df = df[df['action'] == 'scale'].sort_values('scale_potential', ascending=False)
            
            if len(scale_df) > 0:
                for _, row in scale_df.iterrows():
                    trend_badge = ""
                    if has_daily and row['trend_signal'] == 'up':
                        trend_badge = f'<span class="badge badge-success">↗ +{row["trend_score"]:.0f}%</span>'
                    
                    st.markdown(render_action_card(
                        row['format'],
                        row['nom'],
                        row['recommendation'],
                        f"ROAS: {row['roas']:.1f} · CTR: {row['ctr_lien']:.2f}% · Potentiel: {row['scale_potential']}",
                        'scale',
                        trend_badge
                    ), unsafe_allow_html=True)
            else:
                st.info("Aucune créative prête à scaler")
            
            # Monitor section
            st.markdown('<div class="section-title">👁️ À surveiller</div>', unsafe_allow_html=True)
            monitor_df = df[df['action'] == 'monitor'].sort_values('scale_potential', ascending=False).head(5)
            
            for _, row in monitor_df.iterrows():
                trend_badge = ""
                if has_daily:
                    if row['trend_signal'] == 'up':
                        trend_badge = f'<span class="badge badge-success">↗</span>'
                    elif row['trend_signal'] == 'down':
                        trend_badge = f'<span class="badge badge-danger">↘</span>'
                
                st.markdown(render_action_card(
                    row['format'],
                    row['nom'],
                    row['recommendation'],
                    f"Potentiel: {row['scale_potential']}",
                    'monitor',
                    trend_badge
                ), unsafe_allow_html=True)
        
        with col_right:
            # Test section
            st.markdown('<div class="section-title">⚡ À tester</div>', unsafe_allow_html=True)
            test_df = df[df['action'] == 'test'].sort_values('scale_potential', ascending=False)
            
            if len(test_df) > 0:
                for _, row in test_df.iterrows():
                    st.markdown(render_action_card(
                        row['format'],
                        row['nom'],
                        row['recommendation'],
                        f"ROAS: {row['roas']:.1f} · Confiance: {row['coefficient_confiance']*100:.0f}%",
                        'test'
                    ), unsafe_allow_html=True)
            else:
                st.info("Aucune créative à tester")
            
            # Pause section
            st.markdown('<div class="section-title">⏸️ À pauser</div>', unsafe_allow_html=True)
            pause_df = df[df['action'] == 'pause']
            
            if len(pause_df) > 0:
                for _, row in pause_df.iterrows():
                    trend_badge = ""
                    if has_daily and row['trend_score'] < -20:
                        trend_badge = f'<span class="badge badge-danger">↘ {row["trend_score"]:.0f}%</span>'
                    
                    st.markdown(render_action_card(
                        row['format'],
                        row['nom'],
                        row['recommendation'],
                        f"Frequency: {row['frequency']:.2f}",
                        'pause',
                        trend_badge
                    ), unsafe_allow_html=True)
            else:
                st.success("✅ Aucune créative à pauser")
    
    # ========== TAB 2: Alertes ==========
    with tab2:
        alerts = detect_alerts(df, trends)
        anomalies = detect_anomalies(df, sparklines) if has_daily else []
        fatigue_predictions = predict_fatigue(df, sparklines) if has_daily else []
        diversification = calculate_diversification_score(df)
        
        total_alerts = len(alerts) + len(anomalies) + len(diversification['alerts'])
        
        # Alert metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🚨 Alertes", total_alerts)
        with col2:
            st.metric("⚠️ Anomalies 24h", len(anomalies))
        with col3:
            fatigued_soon = len([p for p in fatigue_predictions if p['days_to_fatigue'] <= 7])
            st.metric("😴 Fatigue < 7j", fatigued_soon)
        with col4:
            st.metric("🎯 Diversification", f"{diversification['score']}/100")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        alert_tab1, alert_tab2, alert_tab3, alert_tab4 = st.tabs([
            f"🔔 Alertes ({len(alerts)})",
            f"⚠️ Anomalies ({len(anomalies)})",
            f"😴 Fatigue",
            "🎯 Diversification"
        ])
        
        with alert_tab1:
            if alerts:
                for alert in alerts:
                    card_class = "alert-card" if alert['type'] == 'danger' else "warning-card"
                    st.markdown(f"""
                    <div class="{card_class}">
                        <strong>{alert['icon']} {alert['title']}</strong><br>
                        <small style="opacity: 0.8;">📌 {alert['creative'][:50]}...</small><br>
                        <small>{alert['message']}</small><br>
                        <small style="opacity: 0.7;">💡 {alert['action']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Aucune alerte")
        
        with alert_tab2:
            if not has_daily:
                st.warning("Chargez les données quotidiennes")
            elif anomalies:
                for anomaly in anomalies:
                    st.markdown(f"""
                    <div class="alert-card">
                        <strong>{anomaly['icon']} {anomaly['title']}</strong><br>
                        <small>{anomaly['message']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Aucune anomalie")
        
        with alert_tab3:
            if fatigue_predictions:
                fatigue_df = pd.DataFrame(fatigue_predictions)
                fatigue_df['Statut'] = fatigue_df.apply(lambda r: f"{r['color']} {r['status']}", axis=1)
                fatigue_df['Jours'] = fatigue_df['days_to_fatigue'].apply(lambda x: "Fatiguée" if x == 0 else f"{x}j")
                fatigue_df['Freq.'] = fatigue_df['current_freq'].apply(lambda x: f"{x:.2f}")
                fatigue_df['Créative'] = fatigue_df['creative'].str[:40] + '...'
                
                st.dataframe(
                    fatigue_df[['format', 'Créative', 'Freq.', 'Jours', 'Statut']],
                    use_container_width=True,
                    hide_index=True
                )
        
        with alert_tab4:
            col1, col2 = st.columns([1, 2])
            with col1:
                score = diversification['score']
                st.metric("Score", f"{score}/100", 
                         delta="OK" if score >= 60 else "À améliorer",
                         delta_color="normal" if score >= 60 else "inverse")
            
            with col2:
                if diversification['by_usp']:
                    fig = px.pie(
                        values=list(diversification['by_usp'].values()),
                        names=list(diversification['by_usp'].keys()),
                        title="Répartition par USP",
                        hole=0.4
                    )
                    fig.update_layout(height=250, margin=dict(t=40, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 3: Angles créatifs ==========
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-title">📌 Par USP</div>', unsafe_allow_html=True)
            usp_stats = df.groupby('usp').agg({
                'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean'
            }).round(2)
            usp_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel']
            usp_stats = usp_stats.sort_values('Potentiel', ascending=False)
            st.dataframe(usp_stats, use_container_width=True)
            
            if len(usp_stats) > 0:
                fig = px.bar(usp_stats.reset_index(), x='usp', y='Potentiel',
                           color='Potentiel', color_continuous_scale='Purples')
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-title">🎣 Par Hook</div>', unsafe_allow_html=True)
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
    
    # ========== TAB 4: Tableau détaillé ==========
    with tab4:
        # Filtres
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_query = st.text_input("🔍 Rechercher", placeholder="Nom de créative...")
        with col2:
            format_filter = st.multiselect("Format", options=df['format'].unique(), default=list(df['format'].unique()))
        with col3:
            action_filter = st.multiselect("Action", options=df['action'].unique(), default=list(df['action'].unique()))
        with col4:
            sort_by = st.selectbox("Trier par", options=['scale_potential', 'score_global', 'roas', 'ctr_lien'])
        
        # Filtrer
        filtered_df = df[
            (df['format'].isin(format_filter)) &
            (df['action'].isin(action_filter))
        ]
        
        if search_query:
            filtered_df = filtered_df[filtered_df['nom'].str.lower().str.contains(search_query.lower())]
        
        filtered_df = filtered_df.sort_values(sort_by, ascending=False)
        
        # Préparer affichage
        display_df = filtered_df.copy()
        display_df['Nom'] = display_df['nom']
        display_df['ROAS'] = display_df['roas'].apply(lambda x: f"{x:.2f}")
        display_df['CTR'] = display_df['ctr_lien'].apply(lambda x: f"{x:.2f}%")
        display_df['Dépense'] = display_df['depense'].apply(lambda x: f"{x:.0f}€")
        display_df['Score'] = display_df['score_global'].apply(lambda x: f"{x} ({get_grade(x)})")
        
        action_icons = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
        display_df['Action'] = display_df['action'].map(action_icons)
        
        st.dataframe(
            display_df[['format', 'Nom', 'ROAS', 'CTR', 'Dépense', 'Score', 'scale_potential', 'Action']],
            use_container_width=True,
            height=500,
            column_config={
                "format": st.column_config.TextColumn("Format", width=70),
                "Nom": st.column_config.TextColumn("Nom", width=350),
                "scale_potential": st.column_config.ProgressColumn("Potentiel", format="%d", min_value=0, max_value=100),
            },
            hide_index=True
        )
        
        st.download_button(
            "📥 Exporter CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name=f"creative_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    
    # ========== TAB 5: Comparateur ==========
    with tab5:
        selected = st.multiselect(
            "Sélectionnez 2 à 4 créatives à comparer",
            options=df['nom'].tolist(),
            max_selections=4,
            format_func=lambda x: f"{df[df['nom']==x]['format'].values[0]} · {x[:40]}..."
        )
        
        if len(selected) >= 2:
            compare_df = df[df['nom'].isin(selected)]
            
            # Radar chart
            fig = go.Figure()
            for nom in selected:
                row = compare_df[compare_df['nom'] == nom].iloc[0]
                values = [row['score_profitabilite'], row['score_trafic'], row['score_notoriete'], row['scale_potential'], row['score_profitabilite']]
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=['Profit', 'Trafic', 'Notoriété', 'Potentiel', 'Profit'],
                    name=nom[:20] + '...',
                    fill='toself',
                    opacity=0.6
                ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100])),
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Comparison table
            score_data = []
            for nom in selected:
                row = compare_df[compare_df['nom'] == nom].iloc[0]
                score_data.append({
                    'Créative': nom[:30] + '...',
                    'Profit': f"{row['score_profitabilite']} ({get_grade(row['score_profitabilite'])})",
                    'Trafic': f"{row['score_trafic']} ({get_grade(row['score_trafic'])})",
                    'Notoriété': f"{row['score_notoriete']} ({get_grade(row['score_notoriete'])})",
                    'Potentiel': row['scale_potential'],
                    'Action': row['action']
                })
            st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True)
            
            winner = compare_df.sort_values('scale_potential', ascending=False).iloc[0]
            st.success(f"🏆 **Meilleur potentiel:** {winner['format']} · {winner['nom'][:40]}... (Score: {winner['scale_potential']})")
        else:
            st.info("👆 Sélectionnez au moins 2 créatives pour comparer")


if __name__ == "__main__":
    main()
