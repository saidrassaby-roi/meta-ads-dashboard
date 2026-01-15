"""
Meta Ads Creative Intelligence Dashboard V2.5
=============================================
Application de pilotage des créatives publicitaires Meta Ads.
Tableau avec composants natifs Streamlit pour un affichage fiable.

Auteur: Le ROI Digital
Version: 2.5 - Nomenclature personnalisée

Changelog V2.5:
- Score Profitabilité V2 avec Panier moyen (20%)
- Paramètre Marge moyenne configurable
- Calcul du Profit estimé
- Alerte ROAS trompeur (ROAS > 1 mais perte)
- Affichage du ROAS seuil de rentabilité

Nomenclature créatives:
- Structure: [FORMAT]_CCPT-[Concept]_USP-[Argument]_PERSONA-[Cible]_[Version]_[Date]
- Exemple:   VID_CCPT-Transformation_USP-Garantie-30-Jours_PERSONA-Prospect_V1_2026-01-15
- Formats:   IMG, VID, CAR, GIF, UGC, STO
- CCPT:      Concept créatif (angle de communication)
- USP:       Unique Selling Proposition (argument de vente)
- Date:      Format YYYY-MM-DD ou YYYYMMDD
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

# Initialiser le mode sombre dans session_state (toujours activé maintenant)
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# ============================================================================
# THÈME VISUEL GA4 STYLE
# ============================================================================

# Couleurs du thème
COLORS = {
    'bg_primary': '#0d1117',      # Fond principal
    'bg_secondary': '#161b22',    # Fond cards
    'bg_tertiary': '#21262d',     # Fond hover/accent
    'border': '#30363d',          # Bordures
    'text_primary': '#f0f6fc',    # Texte principal
    'text_secondary': '#8b949e',  # Texte secondaire
    'text_muted': '#6e7681',      # Texte grisé
    'accent_gold': '#f0b429',     # Accent doré (graphiques)
    'accent_orange': '#f97316',   # Orange
    'accent_red': '#ef4444',      # Rouge
    'accent_green': '#22c55e',    # Vert
    'accent_blue': '#3b82f6',     # Bleu
    'accent_purple': '#8b5cf6',   # Violet
    'gradient_start': '#4F46E5',  # Gradient header
    'gradient_end': '#EC4899',    # Gradient header
}

# CSS personnalisé style GA4
def get_css(dark_mode=True):
    return f"""
    <style>
        /* ===== GLOBAL DARK THEME ===== */
        .stApp {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {COLORS['bg_secondary']};
            border-right: 1px solid {COLORS['border']};
        }}
        
        [data-testid="stSidebar"] .stMarkdown {{
            color: {COLORS['text_primary']};
        }}
        
        /* ===== HEADER ===== */
        .main-header {{
            background: linear-gradient(135deg, {COLORS['gradient_start']} 0%, {COLORS['accent_purple']} 50%, {COLORS['gradient_end']} 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(79, 70, 229, 0.3);
        }}
        
        .main-header h1 {{
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
        }}
        
        .main-header p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }}
        
        /* ===== METRIC CARDS GA4 STYLE ===== */
        .metric-card {{
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }}
        
        .metric-card:hover {{
            background: {COLORS['bg_tertiary']};
            border-color: {COLORS['accent_gold']};
        }}
        
        .metric-label {{
            color: {COLORS['text_secondary']};
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{
            color: {COLORS['text_primary']};
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
        }}
        
        .metric-value-small {{
            font-size: 1.5rem;
        }}
        
        /* ===== VARIATION BADGES ===== */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 8px;
        }}
        
        .badge-up {{
            background: rgba(34, 197, 94, 0.15);
            color: {COLORS['accent_green']};
        }}
        
        .badge-down {{
            background: rgba(239, 68, 68, 0.15);
            color: {COLORS['accent_red']};
        }}
        
        .badge-neutral {{
            background: rgba(139, 148, 158, 0.15);
            color: {COLORS['text_secondary']};
        }}
        
        /* ===== ACTION CARDS ===== */
        .action-card {{
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid;
            transition: all 0.2s ease;
        }}
        
        .action-card:hover {{
            transform: translateX(4px);
        }}
        
        .scale-card {{ 
            border-left-color: {COLORS['accent_green']}; 
            background: linear-gradient(90deg, rgba(34, 197, 94, 0.1) 0%, {COLORS['bg_secondary']} 100%);
        }}
        .test-card {{ 
            border-left-color: {COLORS['accent_blue']}; 
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, {COLORS['bg_secondary']} 100%);
        }}
        .monitor-card {{ 
            border-left-color: {COLORS['accent_gold']}; 
            background: linear-gradient(90deg, rgba(240, 180, 41, 0.1) 0%, {COLORS['bg_secondary']} 100%);
        }}
        .pause-card {{ 
            border-left-color: {COLORS['accent_red']}; 
            background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, {COLORS['bg_secondary']} 100%);
        }}
        
        /* ===== ALERT CARDS ===== */
        .alert-card {{
            background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, {COLORS['bg_secondary']} 100%);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-left: 4px solid {COLORS['accent_red']};
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}
        
        .warning-card {{
            background: linear-gradient(90deg, rgba(240, 180, 41, 0.1) 0%, {COLORS['bg_secondary']} 100%);
            border: 1px solid rgba(240, 180, 41, 0.3);
            border-left: 4px solid {COLORS['accent_gold']};
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}
        
        .info-card {{
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, {COLORS['bg_secondary']} 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-left: 4px solid {COLORS['accent_blue']};
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}
        
        .success-card {{
            background: linear-gradient(90deg, rgba(34, 197, 94, 0.1) 0%, {COLORS['bg_secondary']} 100%);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-left: 4px solid {COLORS['accent_green']};
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}
        
        /* ===== TABS STYLING ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            background: {COLORS['bg_secondary']};
            border-radius: 12px;
            padding: 4px;
            border: 1px solid {COLORS['border']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 12px 24px;
            border-radius: 8px;
            color: {COLORS['text_secondary']};
            font-weight: 500;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            color: {COLORS['text_primary']};
            background: {COLORS['bg_tertiary']};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {COLORS['accent_purple']} !important;
            color: white !important;
        }}
        
        /* ===== DATA TABLES ===== */
        .stDataFrame {{
            background: {COLORS['bg_secondary']};
            border-radius: 12px;
            overflow: hidden;
        }}
        
        [data-testid="stDataFrame"] > div {{
            background: {COLORS['bg_secondary']};
        }}
        
        /* ===== EXPANDERS ===== */
        .streamlit-expanderHeader {{
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            color: {COLORS['text_primary']};
        }}
        
        .streamlit-expanderContent {{
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-top: none;
            border-radius: 0 0 12px 12px;
        }}
        
        /* ===== BUTTONS ===== */
        .stButton > button {{
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            color: {COLORS['text_primary']};
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background: {COLORS['accent_purple']};
            border-color: {COLORS['accent_purple']};
            color: white;
        }}
        
        /* ===== INPUTS ===== */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {{
            background: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border']};
            color: {COLORS['text_primary']};
            border-radius: 8px;
        }}
        
        .stMultiSelect > div {{
            background: {COLORS['bg_tertiary']};
            border-color: {COLORS['border']};
        }}
        
        /* ===== CHECKBOXES ===== */
        .stCheckbox label {{
            color: {COLORS['text_primary']};
        }}
        
        /* ===== DIVIDERS ===== */
        hr {{
            border-color: {COLORS['border']};
            opacity: 0.5;
        }}
        
        /* ===== KPI SUMMARY ROW ===== */
        .kpi-row {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        
        .kpi-box {{
            flex: 1;
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        }}
        
        .kpi-box-highlight {{
            border-color: {COLORS['accent_gold']};
            box-shadow: 0 0 20px rgba(240, 180, 41, 0.15);
        }}
        
        /* ===== DONUT LEGEND ===== */
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
            color: {COLORS['text_secondary']};
            font-size: 0.85rem;
        }}
        
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS['bg_primary']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {COLORS['border']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['text_muted']};
        }}
        
        /* ===== HIDE STREAMLIT BRANDING ===== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* ===== PERIOD LABEL ===== */
        .period-label {{
            color: {COLORS['text_muted']};
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }}
        
        /* ===== CHART CONTAINER ===== */
        .chart-container {{
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }}
        
        .chart-title {{
            color: {COLORS['text_primary']};
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        /* ===== STREAMLIT METRICS OVERRIDE ===== */
        [data-testid="stMetricValue"] {{
            color: {COLORS['text_primary']};
            font-size: 2rem;
            font-weight: 700;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {COLORS['text_secondary']};
        }}
        
        [data-testid="stMetricDelta"] svg {{
            display: none;
        }}
        
        /* ===== SUCCESS/INFO/WARNING/ERROR STREAMLIT ===== */
        .stSuccess, .stInfo, .stWarning, .stError {{
            background: {COLORS['bg_secondary']};
            border-radius: 12px;
        }}
    </style>
    """


# Fonction pour créer le layout Plotly dark theme
def get_plotly_layout(title="", height=300, showlegend=True):
    """Retourne un layout Plotly avec le thème sombre."""
    return dict(
        title=dict(text=title, font=dict(color=COLORS['text_primary'], size=14)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_secondary'], size=11),
        height=height,
        margin=dict(l=40, r=40, t=40 if title else 20, b=40),
        showlegend=showlegend,
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text_secondary'], size=10),
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='center',
            x=0.5
        ),
        xaxis=dict(
            gridcolor=COLORS['border'],
            zerolinecolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_muted'], size=10),
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            gridcolor=COLORS['border'],
            zerolinecolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_muted'], size=10),
            showgrid=True,
            gridwidth=1
        ),
        hoverlabel=dict(
            bgcolor=COLORS['bg_tertiary'],
            font_size=12,
            font_color=COLORS['text_primary']
        )
    )


def create_area_chart(df, x, y, title="", color=COLORS['accent_gold']):
    """Crée un graphique en aire avec dégradé style GA4."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(**get_plotly_layout(title))
    return fig


def create_bar_chart(df, x, y, title="", color=COLORS['accent_orange']):
    """Crée un graphique en barres style GA4."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df[x],
        y=df[y],
        marker=dict(
            color=color,
            line=dict(width=0),
            cornerradius=4
        ),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(**get_plotly_layout(title))
    return fig


def create_donut_chart(values, labels, title="", colors=None):
    """Crée un graphique donut style GA4."""
    if colors is None:
        colors = [COLORS['accent_gold'], COLORS['accent_orange'], COLORS['accent_red'], 
                  COLORS['accent_blue'], COLORS['accent_green'], COLORS['accent_purple']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        values=values,
        labels=labels,
        hole=0.65,
        marker=dict(colors=colors[:len(values)]),
        textinfo='none',
        hovertemplate='%{label}: %{value}<br>%{percent}<extra></extra>'
    ))
    
    layout = get_plotly_layout(title, height=250, showlegend=True)
    layout['legend'] = dict(
        bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_secondary'], size=10),
        orientation='h',
        yanchor='top',
        y=-0.1,
        xanchor='center',
        x=0.5
    )
    fig.update_layout(**layout)
    return fig


def create_bubble_chart(df, x, y, size, color, title=""):
    """Crée un graphique à bulles style GA4."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode='markers',
        marker=dict(
            size=df[size],
            sizemode='area',
            sizeref=2.*max(df[size])/(40.**2),
            sizemin=4,
            color=df[color] if color in df.columns else COLORS['accent_gold'],
            colorscale='YlOrRd',
            showscale=True,
            colorbar=dict(
                title=dict(text=color, font=dict(color=COLORS['text_secondary'])),
                tickfont=dict(color=COLORS['text_muted'])
            )
        ),
        hovertemplate=f'{x}: %{{x}}<br>{y}: %{{y}}<br>{size}: %{{marker.size}}<extra></extra>'
    ))
    
    fig.update_layout(**get_plotly_layout(title, height=350))
    return fig


def format_variation_badge(value, inverse=False):
    """Crée un badge HTML pour afficher une variation."""
    if value == 0:
        return f'<span class="badge badge-neutral">0%</span>'
    
    is_positive = value > 0
    if inverse:
        is_positive = not is_positive
    
    badge_class = "badge-up" if is_positive else "badge-down"
    arrow = "▲" if value > 0 else "▼"
    
    return f'<span class="badge {badge_class}">{arrow} {abs(value):.1f}%</span>'


def render_metric_card(label, value, variation=None, prefix="", suffix="", inverse=False):
    """Render une metric card style GA4."""
    variation_html = ""
    if variation is not None:
        variation_html = format_variation_badge(variation, inverse)
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix} {variation_html}</div>
    </div>
    """


def render_kpi_card(label, value, subtitle="", highlight=False):
    """Render un KPI card compact."""
    highlight_class = "kpi-box-highlight" if highlight else ""
    return f"""
    <div class="kpi-box {highlight_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="period-label">{subtitle}</div>
    </div>
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
        'campagne': ['Nom de la campagne', 'Campaign name', 'campagne', 'nom_campagne'],
        'audience': ['Nom de l\'ensemble de publicités', 'Ad set name', 'audience', 'nom_adset', 'adset'],
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
    
    # Ajouter colonnes par défaut si absentes
    if 'campagne' not in df.columns:
        df['campagne'] = 'Non spécifié'
    if 'audience' not in df.columns:
        df['audience'] = 'Non spécifié'
    
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


# =============================================================================
# NOMENCLATURE CRÉATIVES — Configuration
# =============================================================================
# Structure: [FORMAT]_CCPT-[Concept]_USP-[Argument]_PERSONA-[Cible]_[Version]_[Date]
# Exemple:   VID_CCPT-Transformation_USP-Garantie-30-Jours_PERSONA-Prospect_V1_2026-01-15
# =============================================================================

FORMATS_VALIDES = ['IMG', 'VID', 'CAR', 'GIF', 'UGC', 'STO']  # STO = Story


def parse_creative_name(nom):
    """
    Extrait les composants du nom de la créative selon la nomenclature standardisée.
    
    Structure attendue:
        [FORMAT]_CCPT-[Concept]_USP-[Argument]_PERSONA-[Cible]_[Version]_[Date]
    
    Exemples:
        VID_CCPT-Transformation_USP-Garantie-30-Jours_PERSONA-Prospect_V1_2026-01-15
        IMG_CCPT-Temoignage_USP-Livraison-Gratuite_PERSONA-Client-Fidele_V2_2026-01-20
        CAR_CCPT-Promo-Flash_USP-Moins-50-Pourcent_PERSONA-All_V1_2026-02-01
    
    Returns:
        dict avec 'format', 'concept', 'usp', 'persona', 'version', 'date', 'valide', 'erreurs'
    """
    
    result = {
        'format': 'Autre',
        'concept': 'Autre',
        'usp': 'Autre',
        'persona': 'Autre',
        'version': 'Autre',
        'date': 'Autre',
        'valide': False,
        'erreurs': []
    }
    
    if not isinstance(nom, str) or not nom.strip():
        result['erreurs'].append('Nom vide ou invalide')
        return result
    
    nom = nom.strip()
    erreurs = []
    
    # EXTRACTION DU FORMAT
    format_found = False
    for fmt in FORMATS_VALIDES:
        if nom.upper().startswith(fmt):
            result['format'] = fmt
            format_found = True
            break
    if not format_found:
        erreurs.append('FORMAT manquant')
    
    # EXTRACTION DU CONCEPT (sigle CCPT)
    concept_match = re.search(r'CCPT-([A-Za-z0-9-]+?)(?:_|$)', nom, re.IGNORECASE)
    if concept_match:
        concept_raw = concept_match.group(1)
        result['concept'] = concept_raw.replace('-', ' ').title()
    else:
        erreurs.append('CCPT manquant')
    
    # EXTRACTION DE L'USP (Unique Selling Proposition)
    usp_match = re.search(r'USP-([A-Za-z0-9-]+?)(?:_|$)', nom, re.IGNORECASE)
    if usp_match:
        usp_raw = usp_match.group(1)
        result['usp'] = usp_raw.replace('-', ' ').title()
    else:
        erreurs.append('USP manquant')
    
    # EXTRACTION DU PERSONA
    persona_match = re.search(r'PERSONA-([A-Za-z0-9-]+?)(?:_|$)', nom, re.IGNORECASE)
    if persona_match:
        persona_raw = persona_match.group(1)
        result['persona'] = persona_raw.replace('-', ' ').title()
    else:
        erreurs.append('PERSONA manquant')
    
    # EXTRACTION DE LA VERSION
    version_match = re.search(r'_(V\d+)(?:_|$)', nom, re.IGNORECASE)
    if version_match:
        result['version'] = version_match.group(1).upper()
    else:
        erreurs.append('VERSION manquante')
    
    # EXTRACTION DE LA DATE (format YYYY-MM-DD ou YYYYMMDD)
    date_match = re.search(r'_(\d{4}-\d{2}-\d{2})$', nom)
    if date_match:
        result['date'] = date_match.group(1)
    else:
        # Format alternatif YYYYMMDD
        date_match_alt = re.search(r'_(\d{8})$', nom)
        if date_match_alt:
            d = date_match_alt.group(1)
            result['date'] = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
        else:
            erreurs.append('DATE manquante')
    
    # Déterminer la validité globale
    result['erreurs'] = erreurs
    result['valide'] = len(erreurs) == 0
    
    return result


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


def calculate_scores(df, trends=None, marge_moyenne=40):
    """Calcule les scores pour chaque créative.
    
    Score Profitabilité V2:
    - ROAS: 40%
    - CPA inversé: 25%
    - CVR: 15%
    - Panier moyen: 20%
    """
    
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
    
    # Calculer le panier moyen (AOV)
    df['panier_moyen'] = np.where(df['achats'] > 0, df['valeur_achats'] / df['achats'], 0)
    
    # Calculer le profit estimé
    marge_ratio = marge_moyenne / 100
    df['profit_estime'] = (df['valeur_achats'] * marge_ratio) - df['depense']
    df['profit_ratio'] = np.where(df['depense'] > 0, (df['profit_estime'] / df['depense']) * 100, 0)
    df['is_profitable'] = df['profit_estime'] > 0
    df['roas_seuil'] = round(1 / marge_ratio, 2)
    
    roas_mean, roas_std = calc_stats(df['roas'])
    ctr_mean, ctr_std = calc_stats(df['ctr_lien'])
    cpc_mean, cpc_std = calc_stats(df['cpc_lien'])
    cpm_mean, cpm_std = calc_stats(df['cpm'])
    cpmu_mean, cpmu_std = calc_stats(df['cpmu'])
    reach_mean, reach_std = calc_stats(df['reach'])
    clics_mean, clics_std = calc_stats(df['clics_lien'])
    panier_mean, panier_std = calc_stats(df['panier_moyen'])
    
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
        z_panier = z_score(row['panier_moyen'], panier_mean, panier_std)
        z_ctr = z_score(row['ctr_lien'], ctr_mean, ctr_std)
        z_cpc = z_score(row['cpc_lien'], cpc_mean, cpc_std, inverse=True)
        z_cpm = z_score(row['cpm'], cpm_mean, cpm_std, inverse=True)
        z_cpmu = z_score(row['cpmu'], cpmu_mean, cpmu_std, inverse=True)
        z_reach = z_score(row['reach'], reach_mean, reach_std)
        z_clics = z_score(row['clics_lien'], clics_mean, clics_std)
        
        def z_to_100(z):
            return max(0, min(100, 50 + z * 10))
        
        # Score Profitabilité V2: ROAS 40% + CPA 25% + CVR 15% + Panier 20%
        score_profit = round(z_to_100(0.40 * z_roas + 0.25 * z_cpa + 0.15 * z_cvr + 0.20 * z_panier))
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
    
    # Extraction des composants de la nomenclature
    parsed = df['nom'].apply(parse_creative_name)
    df['format'] = parsed.apply(lambda x: x['format'])
    df['concept'] = parsed.apply(lambda x: x['concept'])
    df['usp'] = parsed.apply(lambda x: x['usp'])
    df['persona'] = parsed.apply(lambda x: x['persona'])
    df['version'] = parsed.apply(lambda x: x['version'])
    df['date_creative'] = parsed.apply(lambda x: x['date'])
    df['nomenclature_valide'] = parsed.apply(lambda x: x['valide'])
    df['nomenclature_erreurs'] = parsed.apply(lambda x: ', '.join(x['erreurs']) if x['erreurs'] else '')
    
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
        
        # NOUVELLE ALERTE: ROAS trompeur (ROAS > 1 mais perte réelle)
        roas = row.get('roas', 0)
        profit_estime = row.get('profit_estime', 0)
        if roas > 1 and profit_estime < 0:
            alerts.append({
                'type': 'danger',
                'icon': '💸',
                'title': 'ROAS trompeur',
                'creative': nom,
                'message': f"ROAS {roas:.2f} mais perte de {abs(profit_estime):.0f}€",
                'action': 'Vérifier la marge ou pauser cette créative',
                'priority': 1
            })
        
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
        return {'score': 100, 'alerts': [], 'by_usp': {}, 'by_concept': {}, 'by_format': {}}
    
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
    
    # Analyse par Concept (remplace Hook)
    concept_budget = df.groupby('concept')['depense'].sum()
    concept_pct = (concept_budget / total_budget * 100).to_dict()
    
    for concept, pct in concept_pct.items():
        if pct > 50:
            alerts.append({
                'type': 'danger',
                'icon': '💡',
                'title': f'Concentration Concept: {concept}',
                'message': f'{pct:.0f}% du budget sur ce concept',
                'action': 'Tester d\'autres concepts créatifs',
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
    max_concept_pct = max(concept_pct.values()) if concept_pct else 0
    max_format_pct = max(format_pct.values()) if format_pct else 0
    
    # Score: 100 si tout est à 25%, 0 si tout est à 100%
    score = 100 - (max_usp_pct * 0.4 + max_concept_pct * 0.35 + max_format_pct * 0.25) * 0.7
    score = max(0, min(100, score))
    
    return {
        'score': round(score),
        'alerts': alerts,
        'by_usp': usp_pct,
        'by_concept': concept_pct,
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
        st.subheader("💵 Rentabilité")
        marge_moyenne = st.slider(
            "Marge moyenne (%)",
            min_value=10,
            max_value=80,
            value=40,
            step=1,
            help="Votre marge brute moyenne sur les produits vendus. Utilisé pour calculer le profit estimé et le ROAS seuil."
        )
        
        # Calculer et afficher le ROAS seuil
        roas_seuil = round(1 / (marge_moyenne / 100), 2)
        st.info(f"📊 **ROAS seuil**: {roas_seuil}  \nMinimum pour être rentable avec {marge_moyenne}% de marge")
        
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
        
        df = calculate_scores(df, trends, marge_moyenne)
        
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
        
        # Nouveaux KPIs V2.5
        avg_panier = total_revenue / total_achats if total_achats > 0 else 0
        total_profit = df['profit_estime'].sum()
        nb_profitable = df['is_profitable'].sum()
        nb_non_profitable = len(df) - nb_profitable
        
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
            roas_seuil_val = df['roas_seuil'].iloc[0] if len(df) > 0 else 2.5
            roas_status = f"↗ > seuil ({roas_seuil_val})" if avg_roas >= roas_seuil_val else f"↘ < seuil ({roas_seuil_val})"
            st.metric("📈 ROAS", f"{avg_roas:.2f}", delta=roas_status, delta_color="normal" if avg_roas >= roas_seuil_val else "inverse")
        
        with kpi3:
            st.metric("🛒 Achats", f"{total_achats:,.0f}")
        
        with kpi4:
            st.metric("🛍️ Panier moyen", f"{avg_panier:.0f}€")
        
        with kpi5:
            profit_status = "✅ Rentable" if total_profit > 0 else "❌ Perte"
            profit_color = "normal" if total_profit > 0 else "inverse"
            st.metric("💵 Profit estimé", f"{total_profit:+,.0f}€", delta=profit_status, delta_color=profit_color)
        
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
        
        # Info rentabilité
        if nb_non_profitable > 0:
            roas_seuil_val = df['roas_seuil'].iloc[0] if len(df) > 0 else 2.5
            st.warning(f"💸 **{nb_non_profitable}** créative{'s' if nb_non_profitable > 1 else ''} non rentable{'s' if nb_non_profitable > 1 else ''} (ROAS < {roas_seuil_val}) · {nb_profitable} rentable{'s' if nb_profitable > 1 else ''}")
        
        # ===== LIGNE 3: CARDS ACTIONS + GRAPHIQUE =====
        col_cards, col_chart = st.columns([3, 1])
        
        with col_cards:
            # 4 cards métriques enrichies sur une ligne
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown(f"""
                <div class="action-card scale-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700; color:{COLORS['text_primary']};">{scale_count}</div>
                    <div style="font-weight:600; color:{COLORS['text_primary']};">🚀 À scaler</div>
                    <div style="font-size:0.75rem; color:{COLORS['text_secondary']};">{pct_budget_scale:.0f}% budget · Pot. {pot_scale:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""
                <div class="action-card test-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700; color:{COLORS['text_primary']};">{test_count}</div>
                    <div style="font-weight:600; color:{COLORS['text_primary']};">⚡ À tester</div>
                    <div style="font-size:0.75rem; color:{COLORS['text_secondary']};">{pct_budget_test:.0f}% budget · Pot. {pot_test:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c3:
                st.markdown(f"""
                <div class="action-card monitor-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700; color:{COLORS['text_primary']};">{monitor_count}</div>
                    <div style="font-weight:600; color:{COLORS['text_primary']};">👁️ Surveiller</div>
                    <div style="font-size:0.75rem; color:{COLORS['text_secondary']};">{pct_budget_monitor:.0f}% budget</div>
                </div>
                """, unsafe_allow_html=True)
            
            with c4:
                st.markdown(f"""
                <div class="action-card pause-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700; color:{COLORS['text_primary']};">{pause_count}</div>
                    <div style="font-weight:600; color:{COLORS['text_primary']};">⏸️ À pauser</div>
                    <div style="font-size:0.75rem; color:{COLORS['text_secondary']};">{pct_budget_pause:.0f}% budget</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_chart:
            # Mini pie chart répartition budget
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Scale', 'Test', 'Monitor', 'Pause'],
                values=[budget_scale, budget_test, budget_monitor, budget_pause],
                hole=0.65,
                marker_colors=[COLORS['accent_green'], COLORS['accent_blue'], COLORS['accent_gold'], COLORS['accent_red']],
                textinfo='none',
                hovertemplate='%{label}: %{percent}<extra></extra>'
            )])
            fig_pie.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=120,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(text='Budget', x=0.5, y=0.5, font_size=11, font_color=COLORS['text_secondary'], showarrow=False)]
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
                        trend_badge = f"<span class='badge badge-up'>+{row['trend_score']:.0f}%</span>"
                    elif has_daily and row['trend_signal'] == 'down':
                        trend_badge = f"<span class='badge badge-down'>{row['trend_score']:.0f}%</span>"
                    
                    st.markdown(f"""
                    <div class="action-card scale-card" style="padding:0.6rem 0.8rem; margin-bottom:0.4rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <strong style="color:{COLORS['text_primary']};">{row['format']}</strong> <span style="color:{COLORS['text_secondary']};">·</span> <span style="color:{COLORS['text_primary']};">{row['nom'][:35]}{'...' if len(row['nom']) > 35 else ''}</span> {trend_badge}
                                <div style="font-size:0.75rem; color:{COLORS['text_secondary']};">ROAS {row['roas']:.1f} · CTR {row['ctr_lien']:.2f}% · Pot. {row['scale_potential']}</div>
                            </div>
                            <div style="font-size:0.7rem; background:{COLORS['accent_green']}; color:white; padding:2px 8px; border-radius:4px;">+20%</div>
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
                        <strong style="color:{COLORS['text_primary']};">{row['format']}</strong> <span style="color:{COLORS['text_secondary']};">·</span> <span style="color:{COLORS['text_primary']};">{row['nom'][:30]}...</span> <span style="color:{COLORS['text_muted']};">{trend_icon}</span>
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
                                <strong style="color:{COLORS['text_primary']};">{row['format']}</strong> <span style="color:{COLORS['text_secondary']};">·</span> <span style="color:{COLORS['text_primary']};">{row['nom'][:35]}{'...' if len(row['nom']) > 35 else ''}</span>
                                <div style="font-size:0.75rem; color:{COLORS['text_secondary']};">ROAS {row['roas']:.1f} · Confiance {row['coefficient_confiance']*100:.0f}%</div>
                            </div>
                            <div style="font-size:0.7rem; background:{COLORS['accent_blue']}; color:white; padding:2px 8px; border-radius:4px;">+50%</div>
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
                        trend_badge = f"<span class='badge badge-down'>{row['trend_score']:.0f}%</span>"
                    
                    st.markdown(f"""
                    <div class="action-card pause-card" style="padding:0.5rem 0.8rem; margin-bottom:0.3rem;">
                        <strong style="color:{COLORS['text_primary']};">{row['format']}</strong> <span style="color:{COLORS['text_secondary']};">·</span> <span style="color:{COLORS['text_primary']};">{row['nom'][:30]}...</span> {trend_badge}
                        <div style="font-size:0.7rem; color:{COLORS['text_secondary']};">Freq. {row['frequency']:.2f}</div>
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
        
        # INDICATEUR DE CONFORMITÉ NOMENCLATURE
        total_creatives = len(df)
        conformes = df['nomenclature_valide'].sum()
        non_conformes = total_creatives - conformes
        taux_conformite = (conformes / total_creatives * 100) if total_creatives > 0 else 0
        
        if taux_conformite == 100:
            conformite_color = "#10B981"  # Vert
            conformite_icon = "✅"
        elif taux_conformite >= 80:
            conformite_color = "#F59E0B"  # Orange
            conformite_icon = "⚠️"
        else:
            conformite_color = "#EF4444"  # Rouge
            conformite_icon = "❌"
        
        col_conf1, col_conf2, col_conf3 = st.columns([2, 2, 3])
        with col_conf1:
            st.metric(
                label=f"{conformite_icon} Conformité nomenclature",
                value=f"{taux_conformite:.0f}%",
                delta=f"{conformes}/{total_creatives} créatives"
            )
        with col_conf2:
            if non_conformes > 0:
                st.warning(f"**{non_conformes}** créative(s) non conforme(s)")
            else:
                st.success("Toutes les créatives sont conformes !")
        with col_conf3:
            # Toggle pour filtrer uniquement les conformes
            filter_conformes_only = st.checkbox(
                "Analyser uniquement les créatives conformes", 
                value=False,
                help="Exclut les créatives avec 'Autre' des analyses"
            )
        
        # Appliquer le filtre si activé
        df_analyse = df[df['nomenclature_valide'] == True] if filter_conformes_only else df
        
        if filter_conformes_only and len(df_analyse) == 0:
            st.error("Aucune créative conforme à analyser. Désactivez le filtre ou corrigez vos noms de créatives.")
        else:
            st.divider()
            
            # LIGNE 1: Concept et USP
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💡 Par Concept (CCPT)")
                concept_stats = df_analyse.groupby('concept').agg({
                    'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                    'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean'
                }).round(2)
                concept_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel']
                concept_stats = concept_stats.sort_values('Potentiel', ascending=False)
                st.dataframe(concept_stats, use_container_width=True)
            
            with col2:
                st.subheader("📌 Par USP")
                usp_stats = df_analyse.groupby('usp').agg({
                    'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                    'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean'
                }).round(2)
                usp_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel']
                usp_stats = usp_stats.sort_values('Potentiel', ascending=False)
            st.dataframe(usp_stats, use_container_width=True)
            
            st.divider()
            
            # LIGNE 2: Persona et Format
            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("👤 Par Persona")
                persona_stats = df_analyse.groupby('persona').agg({
                    'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                    'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean',
                    'profit_estime': 'sum'
                }).round(2)
                persona_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel', 'Profit €']
                persona_stats = persona_stats.sort_values('Potentiel', ascending=False)
                st.dataframe(persona_stats, use_container_width=True)
            
            with col4:
                st.subheader("🎬 Par Format")
                format_stats = df_analyse.groupby('format').agg({
                    'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                    'roas': 'mean', 'ctr_lien': 'mean', 'scale_potential': 'mean'
                }).round(2)
                format_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'CTR %', 'Potentiel']
                format_stats = format_stats.sort_values('Potentiel', ascending=False)
                st.dataframe(format_stats, use_container_width=True)
            
            st.divider()
            
            # LIGNE 3: Date de création
            with st.expander("📅 Par Date de création", expanded=False):
                date_stats = df_analyse.groupby('date_creative').agg({
                    'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                    'roas': 'mean', 'scale_potential': 'mean'
                }).round(2)
                date_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'Potentiel']
                date_stats = date_stats.sort_index(ascending=False)
                st.dataframe(date_stats, use_container_width=True)
            
            # LIGNE 3b: Campagne et Audience
            col_camp, col_aud = st.columns(2)
            
            with col_camp:
                with st.expander("📢 Par Campagne", expanded=False):
                    campagne_stats = df_analyse.groupby('campagne').agg({
                        'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                        'roas': 'mean', 'scale_potential': 'mean'
                    }).round(2)
                    campagne_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'Potentiel']
                    campagne_stats = campagne_stats.sort_values('Dépense €', ascending=False)
                    st.dataframe(campagne_stats, use_container_width=True)
            
            with col_aud:
                with st.expander("🎯 Par Audience (AdSet)", expanded=False):
                    audience_stats = df_analyse.groupby('audience').agg({
                        'nom': 'count', 'depense': 'sum', 'achats': 'sum',
                        'roas': 'mean', 'scale_potential': 'mean'
                    }).round(2)
                    audience_stats.columns = ['Créas', 'Dépense €', 'Achats', 'ROAS', 'Potentiel']
                    audience_stats = audience_stats.sort_values('Dépense €', ascending=False)
                    st.dataframe(audience_stats, use_container_width=True)
            
            st.divider()
            
            # LIGNE 4: Insights et recommandations
            best_concept = concept_stats.index[0] if len(concept_stats) > 0 else "N/A"
            best_usp = usp_stats.index[0] if len(usp_stats) > 0 else "N/A"
            best_persona = persona_stats.index[0] if len(persona_stats) > 0 else "N/A"
            best_format = format_stats.index[0] if len(format_stats) > 0 else "N/A"
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"**💡 Concept**\n\n{best_concept}")
            with col2:
                st.info(f"**📌 USP**\n\n{best_usp}")
            with col3:
                st.info(f"**👤 Persona**\n\n{best_persona}")
            with col4:
                st.info(f"**🎬 Format**\n\n{best_format}")
            
            # Combo gagnant complet
            combo_ccpt = best_concept.replace(' ', '-') if best_concept != "N/A" else "?"
            combo_usp = best_usp.replace(' ', '-') if best_usp != "N/A" else "?"
            combo_persona = best_persona.replace(' ', '-') if best_persona != "N/A" else "?"
            st.success(f"**🏆 Combo gagnant:** {best_format}_CCPT-{combo_ccpt}_USP-{combo_usp}_PERSONA-{combo_persona}")
            
            # LIGNE 5: Analyses croisées
            col_matrix1, col_matrix2 = st.columns(2)
            
            with col_matrix1:
                with st.expander("📊 Matrice Concept × USP", expanded=False):
                    pivot_concept_usp = df_analyse.pivot_table(
                        index='concept', 
                        columns='usp', 
                        values='roas', 
                        aggfunc='mean'
                    ).round(2)
                    if len(pivot_concept_usp) > 0:
                        st.write("**ROAS moyen par Concept × USP:**")
                        st.dataframe(pivot_concept_usp, use_container_width=True)
                    else:
                        st.info("Pas assez de données.")
            
            with col_matrix2:
                with st.expander("📊 Matrice Persona × Concept", expanded=False):
                    pivot_persona_concept = df_analyse.pivot_table(
                        index='persona', 
                        columns='concept', 
                        values='roas', 
                        aggfunc='mean'
                    ).round(2)
                    if len(pivot_persona_concept) > 0:
                        st.write("**ROAS moyen par Persona × Concept:**")
                        st.dataframe(pivot_persona_concept, use_container_width=True)
                    else:
                        st.info("Pas assez de données.")
            
            # LIGNE 6: Liste des créatives non conformes
            if non_conformes > 0:
                with st.expander(f"🔧 Créatives non conformes ({non_conformes})", expanded=False):
                    st.warning("Ces créatives ne respectent pas la nomenclature et sont classées 'Autre' dans les analyses.")
                    df_non_conformes = df[df['nomenclature_valide'] == False][['nom', 'nomenclature_erreurs', 'depense', 'roas']].copy()
                    df_non_conformes.columns = ['Nom créative', 'Erreurs', 'Dépense €', 'ROAS']
                    st.dataframe(df_non_conformes, use_container_width=True)
    
    # ========== TAB 4: Tableau détaillé ==========
    with tab4:
        # Initialiser les états de session pour les filtres
        if 'reset_filters' not in st.session_state:
            st.session_state.reset_filters = False
        
        # ===== LIGNE 1: FILTRES RAPIDES PAR ACTION =====
        action_counts = df['action'].value_counts()
        scale_count = action_counts.get('scale', 0)
        test_count = action_counts.get('test', 0)
        monitor_count = action_counts.get('monitor', 0)
        pause_count = action_counts.get('pause', 0)
        
        col_filters, col_reset = st.columns([5, 1])
        
        with col_filters:
            filter_cols = st.columns(7)
            with filter_cols[0]:
                show_scale = st.checkbox(f"🚀 Scale ({scale_count})", value=True, key="filter_scale")
            with filter_cols[1]:
                show_test = st.checkbox(f"⚡ Test ({test_count})", value=True, key="filter_test")
            with filter_cols[2]:
                show_monitor = st.checkbox(f"👁️ Monitor ({monitor_count})", value=True, key="filter_monitor")
            with filter_cols[3]:
                show_pause = st.checkbox(f"⏸️ Pause ({pause_count})", value=True, key="filter_pause")
            with filter_cols[4]:
                format_options = list(df['format'].unique())
                format_filter = st.multiselect("Format", options=format_options, placeholder="Tous formats", label_visibility="collapsed")
            with filter_cols[5]:
                persona_options = list(df['persona'].unique())
                persona_filter = st.multiselect("Persona", options=persona_options, placeholder="Tous personas", label_visibility="collapsed")
            with filter_cols[6]:
                # Filtre conformité nomenclature
                conformite_options = ["✅ Conforme", "❌ Non conforme"]
                conformite_filter = st.multiselect("Nomenclature", options=conformite_options, placeholder="Tous", label_visibility="collapsed")
        
        with col_reset:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.reset_filters = True
                st.rerun()
        
        # ===== LIGNE 1b: FILTRES CAMPAGNE / AUDIENCE =====
        col_camp_filter, col_aud_filter = st.columns(2)
        with col_camp_filter:
            campagne_options = list(df['campagne'].unique())
            campagne_filter = st.multiselect("📢 Campagne", options=campagne_options, placeholder="Toutes campagnes", label_visibility="visible")
        with col_aud_filter:
            audience_options = list(df['audience'].unique())
            audience_filter = st.multiselect("🎯 Audience", options=audience_options, placeholder="Toutes audiences", label_visibility="visible")
        
        # Construire le filtre d'action
        action_filter = []
        if show_scale: action_filter.append('scale')
        if show_test: action_filter.append('test')
        if show_monitor: action_filter.append('monitor')
        if show_pause: action_filter.append('pause')
        
        # ===== LIGNE 2: RECHERCHE + TRI + VUE =====
        col_search, col_sort, col_order, col_view = st.columns([3, 1.5, 1, 1.5])
        
        with col_search:
            search_query = st.text_input("🔍", placeholder="Rechercher une créative...", label_visibility="collapsed")
        
        with col_sort:
            sort_by = st.selectbox("Trier", 
                options=['scale_potential', 'score_global', 'roas', 'ctr_lien', 'depense', 'trend_score'],
                format_func=lambda x: {
                    'scale_potential': '🎯 Potentiel', 'score_global': '⭐ Score Global',
                    'roas': '💰 ROAS', 'ctr_lien': '👆 CTR', 'depense': '💵 Dépense',
                    'trend_score': '📈 Tendance'
                }.get(x, x),
                label_visibility="collapsed")
        
        with col_order:
            sort_order = st.selectbox("Ordre", ["↓ Desc", "↑ Asc"], label_visibility="collapsed")
        
        with col_view:
            view_mode = st.selectbox("Vue",
                options=['complete', 'scores', 'metrics', 'minimal'],
                format_func=lambda x: {
                    'complete': '📊 Complète', 'scores': '🎯 Scores',
                    'metrics': '📈 Métriques', 'minimal': '⚡ Minimale'
                }.get(x, x),
                label_visibility="collapsed")
        
        # ===== LIGNE 3: FILTRES AVANCÉS (inline) =====
        col_roas, col_pot, col_freq = st.columns(3)
        with col_roas:
            min_roas = st.number_input("ROAS ≥", min_value=0.0, max_value=50.0, value=0.0, step=0.5, label_visibility="visible")
        with col_pot:
            min_potential = st.number_input("Potentiel ≥", min_value=0, max_value=100, value=0, step=5)
        with col_freq:
            max_frequency = st.number_input("Frequency ≤", min_value=1.0, max_value=10.0, value=10.0, step=0.5)
        
        # Construire le filtre de conformité (vide = tout afficher)
        if len(conformite_filter) == 0:
            conformite_valeurs = [True, False]  # Tout
        else:
            conformite_valeurs = []
            if "✅ Conforme" in conformite_filter:
                conformite_valeurs.append(True)
            if "❌ Non conforme" in conformite_filter:
                conformite_valeurs.append(False)
        
        # ===== APPLIQUER LES FILTRES =====
        # Logique: si le filtre est vide, on affiche tout (pas de contrainte)
        filtered_df = df.copy()
        
        # Filtre Format (vide = tout)
        if len(format_filter) > 0:
            filtered_df = filtered_df[filtered_df['format'].isin(format_filter)]
        
        # Filtre Persona (vide = tout)
        if len(persona_filter) > 0:
            filtered_df = filtered_df[filtered_df['persona'].isin(persona_filter)]
        
        # Filtre Campagne (vide = tout)
        if len(campagne_filter) > 0:
            filtered_df = filtered_df[filtered_df['campagne'].isin(campagne_filter)]
        
        # Filtre Audience (vide = tout)
        if len(audience_filter) > 0:
            filtered_df = filtered_df[filtered_df['audience'].isin(audience_filter)]
        
        # Filtre Conformité nomenclature
        filtered_df = filtered_df[filtered_df['nomenclature_valide'].isin(conformite_valeurs)]
        
        # Filtre Action (checkboxes)
        filtered_df = filtered_df[filtered_df['action'].isin(action_filter)]
        
        # Filtres numériques
        filtered_df = filtered_df[
            (filtered_df['roas'] >= min_roas) &
            (filtered_df['scale_potential'] >= min_potential) &
            (filtered_df['frequency'] <= max_frequency)
        ]
        
        if search_query:
            filtered_df = filtered_df[filtered_df['nom'].str.lower().str.contains(search_query.lower())]
        
        # Trier
        filtered_df = filtered_df.sort_values(sort_by, ascending=(sort_order == "↑ Asc"))
        
        # ===== LIGNE 4: KPIs DYNAMIQUES =====
        total_creatives = len(df)
        filtered_creatives = len(filtered_df)
        
        if filtered_creatives > 0:
            avg_roas = filtered_df['roas'].mean()
            total_spend = filtered_df['depense'].sum()
            avg_potential = filtered_df['scale_potential'].mean()
            avg_trend = filtered_df['trend_score'].mean() if has_daily else 0
            
            filtered_scale = len(filtered_df[filtered_df['action'] == 'scale'])
            filtered_pause = len(filtered_df[filtered_df['action'] == 'pause'])
        else:
            avg_roas = 0
            total_spend = 0
            avg_potential = 0
            avg_trend = 0
            filtered_scale = 0
            filtered_pause = 0
        
        # Afficher les KPIs
        kpi_cols = st.columns(6)
        with kpi_cols[0]:
            st.metric("📊 Créatives", f"{filtered_creatives}/{total_creatives}")
        with kpi_cols[1]:
            st.metric("💰 ROAS moy.", f"{avg_roas:.2f}")
        with kpi_cols[2]:
            st.metric("💵 Dépense", f"{total_spend:,.0f}€")
        with kpi_cols[3]:
            st.metric("🎯 Potentiel moy.", f"{avg_potential:.0f}")
        with kpi_cols[4]:
            trend_delta = f"{avg_trend:+.0f}%" if has_daily else "N/A"
            st.metric("📈 Tendance moy.", trend_delta if has_daily else "-")
        with kpi_cols[5]:
            st.metric("🚀 À scaler", f"{filtered_scale}", delta=f"{filtered_pause} pauses" if filtered_pause > 0 else None, delta_color="inverse" if filtered_pause > 0 else "off")
        
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
        
        # ===== TABLEAU PRINCIPAL =====
        if filtered_creatives == 0:
            st.warning("⚠️ Aucune créative ne correspond aux filtres. Essayez de les réinitialiser.")
        else:
            # Préparer le dataframe pour l'affichage
            display_df = filtered_df.copy()
            
            # Colonnes de base
            display_df['Nom'] = display_df['nom']
            
            # Tendance formatée
            if has_daily:
                display_df['Tend.'] = display_df['trend_score'].apply(format_trend)
            else:
                display_df['Tend.'] = "-"
            
            # Scores formatés avec grades colorés
            display_df['Score💰'] = display_df.apply(
                lambda r: format_grade(r['score_profitabilite'], r.get('var_profit', 0)), axis=1
            )
            display_df['Trafic'] = display_df.apply(
                lambda r: format_grade(r['score_trafic'], r.get('var_trafic', 0)), axis=1
            )
            display_df['Notoriété'] = display_df.apply(
                lambda r: format_grade(r['score_notoriete'], r.get('var_notoriete', 0)), axis=1
            )
            display_df['Global'] = display_df.apply(
                lambda r: format_grade(r['score_global'], r.get('var_global', 0)), axis=1
            )
            
            # Métriques formatées
            display_df['ROAS'] = display_df['roas'].apply(lambda x: f"{x:.2f}" if x > 0 else "-")
            display_df['CTR'] = display_df['ctr_lien'].apply(lambda x: f"{x:.2f}%")
            display_df['Dépense'] = display_df['depense'].apply(lambda x: f"{x:.0f}€")
            display_df['Freq.'] = display_df['frequency'].apply(
                lambda x: f"{'🔴' if x > 3 else '🟡' if x > 2 else '🟢'} {x:.2f}"
            )
            # CPMu avec couleur (plus bas = meilleur)
            cpmu_mean = filtered_df['cpmu'].mean() if 'cpmu' in filtered_df.columns and len(filtered_df) > 0 else 0
            display_df['CPMu'] = display_df['cpmu'].apply(
                lambda x: f"{'🟢' if x < cpmu_mean * 0.8 else '🟡' if x < cpmu_mean * 1.5 else '🔴'} {x:.2f}€" if x > 0 else "-"
            )
            display_df['Conf.'] = display_df['coefficient_confiance'].apply(
                lambda x: f"{'🟢' if x >= 0.7 else '🟡' if x >= 0.5 else '🔴'} {x*100:.0f}%"
            )
            
            # Nouvelles colonnes V2.5 : Panier moyen et Profit estimé
            panier_mean = filtered_df['panier_moyen'].mean() if 'panier_moyen' in filtered_df.columns and len(filtered_df) > 0 else 0
            display_df['Panier'] = display_df['panier_moyen'].apply(
                lambda x: f"{'🟢' if x > panier_mean * 1.2 else '🟡' if x > panier_mean * 0.8 else '🔴'} {x:.0f}€" if x > 0 else "-"
            )
            display_df['Profit€'] = display_df.apply(
                lambda r: f"{'✅' if r['is_profitable'] else '❌'} {r['profit_estime']:+,.0f}€", axis=1
            )
            
            # Action formatée
            action_icons = {'scale': '🚀', 'test': '⚡', 'monitor': '👁️', 'pause': '⏸️'}
            display_df['Act.'] = display_df['action'].map(action_icons)
            
            # Définir les colonnes selon le mode de vue
            if view_mode == 'complete':
                columns_to_show = ['format', 'Nom', 'Tend.', 'Score💰', 'Panier', 'Profit€', 'ROAS', 'CTR', 'CPMu', 'Dépense', 'Freq.', 'scale_potential', 'Act.']
            elif view_mode == 'scores':
                columns_to_show = ['format', 'Nom', 'Tend.', 'Score💰', 'Trafic', 'Notoriété', 'Global', 'Conf.', 'scale_potential', 'Act.']
            elif view_mode == 'metrics':
                columns_to_show = ['format', 'Nom', 'Tend.', 'ROAS', 'Panier', 'Profit€', 'CTR', 'CPMu', 'Dépense', 'Freq.', 'scale_potential', 'Act.']
            else:  # minimal
                columns_to_show = ['format', 'Nom', 'Global', 'ROAS', 'Profit€', 'scale_potential', 'Act.']
            
            final_df = display_df[columns_to_show].copy()
            
            # Renommer les colonnes
            rename_cols = {'format': 'Fmt', 'scale_potential': 'Pot.'}
            final_df = final_df.rename(columns=rename_cols)
            
            # Configuration dynamique des colonnes
            column_config = {
                "Fmt": st.column_config.TextColumn("Fmt", width=55),
                "Nom": st.column_config.TextColumn("Nom", width=250),
                "Tend.": st.column_config.TextColumn("Tend.", width=75),
                "Score💰": st.column_config.TextColumn("Score💰", width=90),
                "Trafic": st.column_config.TextColumn("Trafic", width=90),
                "Notoriété": st.column_config.TextColumn("Notoriété", width=90),
                "Global": st.column_config.TextColumn("Global", width=90),
                "ROAS": st.column_config.TextColumn("ROAS", width=55),
                "Panier": st.column_config.TextColumn("Panier", width=75),
                "Profit€": st.column_config.TextColumn("Profit€", width=90),
                "CTR": st.column_config.TextColumn("CTR", width=60),
                "CPMu": st.column_config.TextColumn("CPMu", width=80),
                "Dépense": st.column_config.TextColumn("Dép.", width=60),
                "Freq.": st.column_config.TextColumn("Freq.", width=70),
                "Conf.": st.column_config.TextColumn("Conf.", width=70),
                "Pot.": st.column_config.ProgressColumn("Pot.", format="%d", min_value=0, max_value=100, width=70),
                "Act.": st.column_config.TextColumn("", width=35),
            }
            
            # Calculer la hauteur dynamique
            table_height = min(450, max(200, 40 + len(final_df) * 35))
            
            # Afficher le tableau
            st.dataframe(
                final_df,
                use_container_width=True,
                height=table_height,
                column_config=column_config,
                hide_index=True
            )
        
        # ===== BOUTONS D'ACTION =====
        col_export, col_scores = st.columns([1, 1])
        with col_export:
            if filtered_creatives > 0:
                st.download_button(
                    "📥 Exporter CSV",
                    data=filtered_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"meta_ads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime='text/csv',
                    use_container_width=True
                )
        
        # ===== SCORES DÉTAILLÉS (EXPANDER FERMÉ) =====
        with st.expander("📊 Détail des scores par dimension", expanded=False):
            if filtered_creatives > 0:
                # Fonctions de formatage
                def format_metric_color(value, thresholds, inverse=False, suffix="", decimals=2):
                    if pd.isna(value) or value == 0:
                        return "⚪ -"
                    low, mid, high = thresholds
                    if inverse:
                        color = "🟢" if value <= low else "🟡" if value <= mid else "🟠" if value <= high else "🔴"
                    else:
                        color = "🟢" if value >= high else "🟡" if value >= mid else "🟠" if value >= low else "🔴"
                    return f"{color} {value:.{decimals}f}{suffix}" if decimals > 0 else f"{color} {value:,.0f}{suffix}"
                
                def format_score_color(score):
                    grade = get_grade(score)
                    color = "🟢" if score >= 60 else "🟡" if score >= 50 else "🟠" if score >= 40 else "🔴"
                    return f"{color} {score} ({grade})"
                
                # Quartiles
                roas_q25, roas_q50, roas_q75 = filtered_df['roas'].quantile([0.25, 0.5, 0.75])
                ctr_q25, ctr_q50, ctr_q75 = filtered_df['ctr_lien'].quantile([0.25, 0.5, 0.75])
                cpm_q25, cpm_q50, cpm_q75 = filtered_df[filtered_df['cpm'] > 0]['cpm'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpm'] > 0]) > 0 else (2, 5, 10)
                cpmu_q25, cpmu_q50, cpmu_q75 = filtered_df[filtered_df['cpmu'] > 0]['cpmu'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpmu'] > 0]) > 0 else (2, 5, 10)
                reach_q25, reach_q50, reach_q75 = filtered_df['reach'].quantile([0.25, 0.5, 0.75])
                
                tab_profit, tab_trafic, tab_notoriete, tab_tendance = st.tabs(["💰 Profit", "🚀 Trafic", "👁️ Notoriété", "📈 Tendance"])
                
                with tab_profit:
                    st.caption("**Score Profit V2** = ROAS (40%) + CPA inversé (25%) + CVR (15%) + Panier moyen (20%)")
                    cpa_q25, cpa_q50, cpa_q75 = filtered_df[filtered_df['cpa_calc'] > 0]['cpa_calc'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpa_calc'] > 0]) > 0 else (10, 20, 40)
                    cvr_q25, cvr_q50, cvr_q75 = filtered_df[filtered_df['cvr'] > 0]['cvr'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cvr'] > 0]) > 0 else (1, 2, 5)
                    panier_q25, panier_q50, panier_q75 = filtered_df[filtered_df['panier_moyen'] > 0]['panier_moyen'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['panier_moyen'] > 0]) > 0 else (20, 40, 80)
                    
                    profit_df = filtered_df[['nom', 'format', 'roas', 'cpa_calc', 'cvr', 'panier_moyen', 'profit_estime', 'is_profitable', 'achats', 'score_profitabilite']].copy()
                    profit_df['ROAS'] = profit_df['roas'].apply(lambda x: format_metric_color(x, (roas_q25, roas_q50, roas_q75), inverse=False, decimals=2))
                    profit_df['CPA'] = profit_df['cpa_calc'].apply(lambda x: format_metric_color(x, (cpa_q25, cpa_q50, cpa_q75), inverse=True, suffix="€", decimals=2))
                    profit_df['CVR'] = profit_df['cvr'].apply(lambda x: format_metric_color(x, (cvr_q25, cvr_q50, cvr_q75), inverse=False, suffix="%", decimals=2))
                    profit_df['Panier'] = profit_df['panier_moyen'].apply(lambda x: format_metric_color(x, (panier_q25, panier_q50, panier_q75), inverse=False, suffix="€", decimals=0))
                    profit_df['Profit €'] = profit_df.apply(lambda r: f"{'✅' if r['is_profitable'] else '❌'} {r['profit_estime']:+,.0f}€", axis=1)
                    profit_df['Score'] = profit_df['score_profitabilite'].apply(format_score_color)
                    st.dataframe(profit_df[['format', 'nom', 'ROAS', 'CPA', 'CVR', 'Panier', 'Profit €', 'achats', 'Score']], use_container_width=True, height=min(300, 40 + len(profit_df) * 35), hide_index=True)
                
                with tab_trafic:
                    st.caption("**Score Trafic** = CTR (50%) + CPC inversé (30%) + Clics (20%)")
                    cpc_q25, cpc_q50, cpc_q75 = filtered_df[filtered_df['cpc_lien'] > 0]['cpc_lien'].quantile([0.25, 0.5, 0.75]) if len(filtered_df[filtered_df['cpc_lien'] > 0]) > 0 else (0.2, 0.5, 1)
                    clics_q25, clics_q50, clics_q75 = filtered_df['clics_lien'].quantile([0.25, 0.5, 0.75])
                    
                    trafic_df = filtered_df[['nom', 'format', 'ctr_lien', 'cpc_lien', 'clics_lien', 'impressions', 'score_trafic']].copy()
                    trafic_df['CTR'] = trafic_df['ctr_lien'].apply(lambda x: format_metric_color(x, (ctr_q25, ctr_q50, ctr_q75), inverse=False, suffix="%", decimals=2))
                    trafic_df['CPC'] = trafic_df['cpc_lien'].apply(lambda x: format_metric_color(x, (cpc_q25, cpc_q50, cpc_q75), inverse=True, suffix="€", decimals=2))
                    trafic_df['Clics'] = trafic_df['clics_lien'].apply(lambda x: format_metric_color(x, (clics_q25, clics_q50, clics_q75), inverse=False, decimals=0))
                    trafic_df['Score'] = trafic_df['score_trafic'].apply(format_score_color)
                    st.dataframe(trafic_df[['format', 'nom', 'CTR', 'CPC', 'Clics', 'Score']], use_container_width=True, height=min(300, 40 + len(trafic_df) * 35), hide_index=True)
                
                with tab_notoriete:
                    st.caption("**Score Notoriété** = CPMu inversé (50%) + Couverture (50%)")
                    notoriete_df = filtered_df[['nom', 'format', 'cpmu', 'cpm', 'reach', 'frequency', 'score_notoriete']].copy()
                    notoriete_df['CPMu'] = notoriete_df['cpmu'].apply(lambda x: format_metric_color(x, (cpmu_q25, cpmu_q50, cpmu_q75), inverse=True, suffix="€", decimals=2))
                    notoriete_df['CPM'] = notoriete_df['cpm'].apply(lambda x: format_metric_color(x, (cpm_q25, cpm_q50, cpm_q75), inverse=True, suffix="€", decimals=2))
                    notoriete_df['Reach'] = notoriete_df['reach'].apply(lambda x: format_metric_color(x, (reach_q25, reach_q50, reach_q75), inverse=False, decimals=0))
                    notoriete_df['Score'] = notoriete_df['score_notoriete'].apply(format_score_color)
                    st.dataframe(notoriete_df[['format', 'nom', 'CPMu', 'CPM', 'Reach', 'Score']], use_container_width=True, height=min(300, 40 + len(notoriete_df) * 35), hide_index=True)
                
                with tab_tendance:
                    if has_daily:
                        st.caption("**Score Tendance** = Δ CTR (40%) + Δ CPC inversé (25%) + Δ CPM inversé (20%) + Δ Impressions (15%)")
                        
                        def format_trend_metric(value, inverse=False):
                            if pd.isna(value) or value == 0:
                                return "⚪ 0%"
                            if inverse:
                                color = "🟢" if value <= -5 else "⚪" if value <= 5 else "🟠" if value <= 20 else "🔴"
                            else:
                                color = "🟢" if value >= 5 else "⚪" if value >= -5 else "🟠" if value >= -20 else "🔴"
                            return f"{color} {value:+.0f}%"
                        
                        def format_trend_score(score):
                            if score >= 15:
                                return f"🟢 {score:+.0f} (Excellent)"
                            elif score >= 5:
                                return f"🟢 {score:+.0f} (Bon)"
                            elif score >= -5:
                                return f"⚪ {score:+.0f} (Stable)"
                            elif score >= -15:
                                return f"🟠 {score:+.0f} (Baisse)"
                            else:
                                return f"🔴 {score:+.0f} (Chute)"
                        
                        tendance_df = filtered_df[['nom', 'format', 'trend_ctr', 'trend_cpm', 'trend_score']].copy()
                        tendance_df['trend_cpc'] = tendance_df['nom'].apply(lambda x: trends.get(x, {}).get('cpc', 0))
                        tendance_df['trend_impr'] = tendance_df['nom'].apply(lambda x: trends.get(x, {}).get('impressions', 0))
                        
                        tendance_df['Δ CTR'] = tendance_df['trend_ctr'].apply(lambda x: format_trend_metric(x, inverse=False))
                        tendance_df['Δ CPC'] = tendance_df['trend_cpc'].apply(lambda x: format_trend_metric(x, inverse=True))
                        tendance_df['Δ CPM'] = tendance_df['trend_cpm'].apply(lambda x: format_trend_metric(x, inverse=True))
                        tendance_df['Δ Impr.'] = tendance_df['trend_impr'].apply(lambda x: format_trend_metric(x, inverse=False))
                        tendance_df['Score'] = tendance_df['trend_score'].apply(format_trend_score)
                        
                        tendance_df = tendance_df.sort_values('trend_score', ascending=False)
                        st.dataframe(tendance_df[['format', 'nom', 'Δ CTR', 'Δ CPC', 'Δ CPM', 'Δ Impr.', 'Score']], use_container_width=True, height=min(300, 40 + len(tendance_df) * 35), hide_index=True)
                    else:
                        st.info("⚠️ Chargez les données quotidiennes pour voir les tendances.")
        
        # ===== DÉTAIL CRÉATIVE (COMPACT) =====
        if filtered_creatives > 0:
            with st.expander("🔍 Détail d'une créative", expanded=False):
                selected_creative = st.selectbox(
                    "Sélectionner une créative",
                    options=filtered_df['nom'].tolist(),
                    format_func=lambda x: f"{filtered_df[filtered_df['nom']==x]['format'].values[0]} | {x}",
                    label_visibility="collapsed"
                )
                
                if selected_creative:
                    row = filtered_df[filtered_df['nom'] == selected_creative].iloc[0]
                    
                    # 3 colonnes compactes
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📊 Métriques**")
                        st.caption(f"Impressions: {row['impressions']:,.0f}")
                        st.caption(f"Clics: {row['clics_lien']:,.0f}")
                        st.caption(f"CTR: {row['ctr_lien']:.2f}%")
                        st.caption(f"CPC: {row['cpc_lien']:.2f}€")
                        st.caption(f"CPM: {row['cpm']:.2f}€")
                        st.caption(f"CPMu: {row['cpmu']:.2f}€")
                    
                    with col2:
                        st.markdown("**💰 Conversions**")
                        st.caption(f"Achats: {row['achats']:.0f}")
                        st.caption(f"ROAS: {row['roas']:.2f}")
                        st.caption(f"Dépense: {row['depense']:.2f}€")
                        st.caption(f"Frequency: {row['frequency']:.2f}")
                        st.caption(f"Confiance: {row['coefficient_confiance']*100:.0f}%")
                    
                    with col3:
                        st.markdown("**🎯 Scores**")
                        st.caption(f"Profit: {row['score_profitabilite']} ({get_grade(row['score_profitabilite'])})")
                        st.caption(f"Trafic: {row['score_trafic']} ({get_grade(row['score_trafic'])})")
                        st.caption(f"Notoriété: {row['score_notoriete']} ({get_grade(row['score_notoriete'])})")
                        st.caption(f"Global: {row['score_global']} ({get_grade(row['score_global'])})")
                        st.caption(f"**Potentiel: {row['scale_potential']}**")
                    
                    # Graphique évolution (si données quotidiennes)
                    if has_daily and selected_creative in sparklines:
                        st.markdown("**📈 Évolution (14 derniers jours)**")
                        sparkline_data = sparklines[selected_creative][-14:]
                        
                        if sparkline_data:
                            metric_choice = st.selectbox("Métrique", ['CTR (%)', 'CPMu (€)', 'CPM (€)', 'Impressions'], key="detail_metric")
                            metric_map = {'CTR (%)': 'ctr', 'CPMu (€)': 'cpmu', 'CPM (€)': 'cpm', 'Impressions': 'impressions'}
                            metric_key = metric_map[metric_choice]
                            
                            dates = [d.get('date', '') for d in sparkline_data]
                            values = [d.get(metric_key, 0) for d in sparkline_data]
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=dates, y=values, mode='lines+markers', 
                                line=dict(color=COLORS['accent_gold'], width=2), 
                                marker=dict(size=6, color=COLORS['accent_gold']),
                                fill='tozeroy',
                                fillcolor=f'rgba(240, 180, 41, 0.1)'
                            ))
                            layout = get_plotly_layout("", height=200)
                            layout['xaxis']['tickangle'] = 45
                            fig.update_layout(**layout)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    st.info(f"**Recommandation:** {row['recommendation']}")
        
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
                colors_list = [COLORS['accent_gold'], COLORS['accent_orange'], COLORS['accent_blue'], COLORS['accent_green']]
                for i, nom in enumerate(selected):
                    if nom in sparklines:
                        values = [d.get('ctr', 0) for d in sparklines[nom]]
                        fig.add_trace(go.Scatter(
                            x=list(range(len(values))), y=values,
                            mode='lines+markers', name=nom[:25] + '...', 
                            line=dict(width=2, color=colors_list[i % len(colors_list)]),
                            marker=dict(size=6)
                        ))
                layout = get_plotly_layout("", height=250)
                layout['xaxis']['title'] = dict(text="Jour", font=dict(color=COLORS['text_secondary']))
                layout['yaxis']['title'] = dict(text="CTR %", font=dict(color=COLORS['text_secondary']))
                fig.update_layout(**layout)
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
            colors_list = [COLORS['accent_gold'], COLORS['accent_orange'], COLORS['accent_blue'], COLORS['accent_green']]
            for i, nom in enumerate(selected):
                row = compare_df[compare_df['nom'] == nom].iloc[0]
                values = [row['score_profitabilite'], row['score_trafic'], row['score_notoriete'], row['scale_potential'], row['score_profitabilite']]
                fig.add_trace(go.Scatterpolar(
                    r=values, theta=['Profit', 'Trafic', 'Notoriété', 'Potentiel', 'Profit'],
                    name=nom[:25] + '...', fill='toself', opacity=0.5,
                    line=dict(color=colors_list[i % len(colors_list)])
                ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(range=[0, 100], gridcolor=COLORS['border'], tickfont=dict(color=COLORS['text_muted'])),
                    angularaxis=dict(gridcolor=COLORS['border'], tickfont=dict(color=COLORS['text_secondary'])),
                    bgcolor='rgba(0,0,0,0)'
                ),
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text_secondary']),
                legend=dict(font=dict(color=COLORS['text_secondary']))
            )
            st.plotly_chart(fig, use_container_width=True)
            
            winner = compare_df.sort_values('scale_potential', ascending=False).iloc[0]
            st.success(f"🏆 **Meilleur potentiel:** {winner['format']} | {winner['nom'][:40]}... (Potentiel: {winner['scale_potential']})")
        else:
            st.info("👆 Sélectionnez au moins 2 créatives")


if __name__ == "__main__":
    main()
