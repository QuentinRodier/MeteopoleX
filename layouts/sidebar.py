#!/usr/bin/env python3

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

import datetime
from datetime import timedelta, date
from config.config import start_day, end_day, today,MODELS_CONFIG,selection_obs 

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


def make_dropdown(model_name, config):
    """Crée un dropdown Dash à partir d'une entrée de MODELS_CONFIG."""
    labels = list(config['mapping'].keys())
    default = config.get('default_selection', labels)
    return dcc.Dropdown(
        id=config['dropdown_id'],
        options=[{"value": l, "label": l} for l in labels],
        value=default,          
        multi=True,
        clearable=False
    )

dropdown_obs = dcc.Dropdown(
    id="multi_select_line_chart_obs",
    options=[{"value": "Obs", "label": "Obs"}],
    value=selection_obs,
    multi=True,
    clearable=False
)

dropdowns_models = [
    make_dropdown(name, cfg)
    for name, cfg in MODELS_CONFIG.items()
]


'''dropdown_arpege = dcc.Dropdown(
    id="multi_select_line_chart_ARPEGE",
    options=[{"value": label, "label": label} for label in
             ["Arpege_00h"]],
    value=selection_arpege,
    multi=True,
    clearable=False
)

dropdown_arome = dcc.Dropdown(
    id="multi_select_line_chart_AROME",
    options=[{"value": label, "label": label} for label in
             ["Arome_00h"]],
    value=selection_arome, 
    multi=True,
    clearable=False
)'''

'''dropdown_mnh = dcc.Dropdown(
    id="multi_select_line_chart_MNH",
    options=[{"value": label, "label": label} for label in
             ["MésoNH_Arp", "MésoNH_Aro", "MésoNH_Obs"]],
    value=selection_mnh,
    multi=True,
    clearable=False
)'''

'''dropdown_surfex_mascot = dcc.Dropdown(
    id="multi_select_line_chart_SURFEX_Mascot",
    options=[{"value": label, "label": label} for label in
             ["Surfex_Mascot_00h"]],
    value=selection_surfex_mascot,
    multi=True,
    clearable=False
)'''

'''dropdown_surfex_offline = dcc.Dropdown(
    id="multi_select_line_chart_SURFEX_Offline",
    options=[{"value": label, "label": label} for label in
             ["SURFEX_Offline"]],
    value=selection_surfex_offline,
    multi=True,
    clearable=False
)'''


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
            [dropdown_obs] + dropdowns_models,  
            className="six columns",
            style={"text-align": "center", "justifyContent": "center"},
        ),

        html.Hr(),
        html.H2("Légende", className="display-10"),
        html.Hr(),

        common_legend,
    ],
    style=SIDEBAR_STYLE,
)
