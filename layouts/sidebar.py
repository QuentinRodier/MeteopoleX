#!/usr/bin/env python3

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from collections import defaultdict

import datetime
from datetime import timedelta, date
from config.config import start_day, end_day, today,MODELS_CONFIG, CONFIG_OBS 

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "scroll",
}

# --- Calendrier ---------------------------------------------------------------

date_picker = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        first_day_of_week=1,
        min_date_allowed=date(2015, 1, 1),
        max_date_allowed=date(end_day.year, end_day.month, end_day.day),
        display_format="DD/MM/YYYY",
        initial_visible_month=date(today.year, today.month, today.day),
        start_date=start_day,
        end_date=end_day,
        minimum_nights=0
    ),
    html.Div(id='output-container-date-picker-range')
])

# --- Dropdowns ----------------------------------------------------------------

# Les sélections par défaut sont extraites dynamiquement depuis MODELS_CONFIG
def get_default_selection(model_name):
    """Retourne la liste de sélection des modèles affichés par défaut."""
    return list(MODELS_CONFIG[model_name]['default_selection'].keys())

def make_dropdown(models_config, config_obs):
    categories = defaultdict(lambda: {'options': [], 'defaults': []})
    
    for name, cfg in config_obs.items():
        if not isinstance(cfg, dict): 
            continue
        if not cfg.get('in_dropdown', True):
            continue
        cat = cfg.get('category', 'Observations')
        categories[cat]['options'].append({"value": name, "label": name})
        defaults = cfg.get('default_selection', [])
        if isinstance(defaults, list):
            categories[cat]['defaults'].extend(defaults)
    
    for model_name, cfg in models_config.items():
        cat = cfg.get('category', 'Autres')
        for label in cfg['mapping'].keys():
            categories[cat]['options'].append({"value": label, "label": label})
        categories[cat]['defaults'].extend(cfg.get('default_selection', []))
    
    dropdowns = []
    for cat_name, data in categories.items():
        dropdowns.append(html.P(cat_name, style={"marginBottom": "2px"}))
        dropdowns.append(dcc.Dropdown(
            id=f"dropdown_cat_{cat_name.lower().replace('é','e').replace(' ','_')}",
            options=data['options'],
            value=data['defaults'],
            multi=True,
            clearable=False,
        ))
    
    return dropdowns


# -----------------------------------------------------------------------------
#   1.3 LAYOUT
# -----------------------------------------------------------------------------

common_legend = html.Div(id='common-legend', style={'marginTop': '1rem'})

layout_sidebar = html.Div(
    [
        html.H1("MeteopoleX", className="display-10"),
        html.Hr(),

        html.H2("Menu", className="display-10"),
        html.Hr(),

        html.Div(
            [
                html.Div(dbc.NavLink("Séries temporelles", href="/MeteopoleX/")),
                html.Div(dbc.NavLink("Biais", href="/MeteopoleX/biais")),
                html.Div(dbc.NavLink("Biais moyens", href="/MeteopoleX/biaisM")),
                html.Div(dbc.NavLink("Panneaux Photovoltaïques", href="/MeteopoleX/PV")),
                html.Div(dbc.NavLink("Profils verticaux", href="/MeteopoleX/rs")),
                html.Div(dbc.NavLink("Notice", href="/MeteopoleX/notice")),
            ],
            style={"display": "flex", "flexDirection": "column", "gap": "0.5rem"}
        ),

        html.Hr(),
        html.H2("Données", className="display-10"),
        html.Hr(),

        date_picker,

        html.Div(
            make_dropdown(MODELS_CONFIG, CONFIG_OBS),
            className='six columns',
            style={"text-align": "center", "justifyContent": "center"}
        ),

        html.Hr(),
        html.H2("Légende", className="display-10"),
        html.Hr(),

        common_legend,
    ],
    style=SIDEBAR_STYLE,
)
