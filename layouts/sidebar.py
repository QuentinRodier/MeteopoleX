#!/usr/bin/env python3

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

import datetime
from datetime import timedelta, date

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

today = datetime.date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)

# Période par défaut
start_day = yesterday
end_day = today


# --- Calendrier ---------------------------------------------------------------

date_picker = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        first_day_of_week=1,
        min_date_allowed=date(2015, 1, 1),
        max_date_allowed=date(tomorrow.year, tomorrow.month, tomorrow.day),
        display_format="DD/MM/YYYY",
        initial_visible_month=date(today.year, today.month, today.day),
        start_date=yesterday,
        end_date=today,
        minimum_nights=0
    ),
    html.Div(id='output-container-date-picker-range')
])


# --- Dropdowns ----------------------------------------------------------------

dropdown_obs = dcc.Dropdown(
    id="multi_select_line_chart_obs",
    options=[{"value": "Obs", "label": "Obs"}],
    value=["Obs"],
    multi=True,
    clearable=False
)

dropdown_arp = dcc.Dropdown(
    id="multi_select_line_chart_ARP",
    options=[{"value": label, "label": label} for label in
             ["Arp_J-1_00h", "Arp_J-1_12h", "Arp_J0_00h", "Arp_J0_12h"]],
    value=["Arp_J0_00h", "Arp_J-1_12h"],
    multi=True,
    clearable=False
)

dropdown_aro = dcc.Dropdown(
    id="multi_select_line_chart_ARO",
    options=[{"value": label, "label": label} for label in
             ["Aro_J-1_00h", "Aro_J-1_12h", "Aro_J0_00h", "Aro_J0_12h"]],
    value=["Aro_J0_00h", "Aro_J-1_12h"],
    multi=True,
    clearable=False
)

dropdown_arome = dcc.Dropdown(
    id="multi_select_line_chart_AROME",
    options=[{"value": label, "label": label} for label in
             ["Arome_J-1_00h", "Arome_J-1_12h", "Arome_J0_00h", "Arome_J0_12h"]],
    value=["Arome_J0_00h", "Arome_J-1_12h"],
    multi=True,
    clearable=False
)

dropdown_mnh = dcc.Dropdown(
    id="multi_select_line_chart_MNH",
    options=[{"value": label, "label": label} for label in
             ["MésoNH_Arp", "MésoNH_Aro", "MésoNH_Obs"]],
    value=["MésoNH_Arp", "MésoNH_Aro"],
    multi=True,
    clearable=False
)

dropdown_surfex = dcc.Dropdown(
    id="multi_select_line_chart_SURFEX",
    options=[{"value": label, "label": label} for label in
             ["SURFEX_Arp", "SURFEX_Aro", "SURFEX_Obs"]],
    value=["SURFEX_Arp"],
    multi=True,
    clearable=False
)


# --- Inputs utilisateur (rejeu) -----------------------------------------------

user_id_inputs = html.Div([
    dcc.Input(id=f'id_user{i}', type='text', placeholder='Rejeu ID',
              style={'width': '50%'})
    for i in range(1, 6)
])


# -----------------------------------------------------------------------------
#   1.3 LAYOUT
# -----------------------------------------------------------------------------

layout_sidebar = html.Div(
    [
        html.H1("MeteopoleX", className="display-10"),
        html.Hr(),

        html.H2("Menu", className="display-10"),
        html.Hr(),

        dbc.Nav(
            [
                dbc.NavLink("Séries temporelles", href="/MeteopoleX/"),
                dbc.NavLink("Biais", href="/MeteopoleX/biais"),
                dbc.NavLink("Biais moyens", href="/MeteopoleX/biaisM"),
                dbc.NavLink("Profils verticaux", href="/MeteopoleX/rs"),
                dbc.NavLink("Rejeu MésoNH", href="/MeteopoleX/mesoNH"),
                dbc.NavLink("Rejeu SURFEX", href="/MeteopoleX/surfex"),
                dbc.NavLink("Panneaux Photovoltaïques", href="/MeteopoleX/PV"),
                dbc.NavLink("Notice", href="/MeteopoleX/notice"),
            ],
            vertical=True,
            pills=True,
        ),

        html.Hr(),
        html.H2("Données", className="display-10"),
        html.Hr(),

        date_picker,

        html.Div(
            [
                dropdown_obs,
                dropdown_arp,
                dropdown_aro,
                dropdown_arome,
                dropdown_mnh,
                dropdown_surfex,
            ],
            className="six columns",
            style={"text-align": "center", "justifyContent": "center"},
        ),

        user_id_inputs,
    ],
    style=SIDEBAR_STYLE,
)