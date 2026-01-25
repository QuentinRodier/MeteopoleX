from dash import html
from dash import dcc
import plotly.graph_objects as go

import datetime
from datetime import date, timedelta

from config.models import MODELS, MODELS_PLOT_RS, LEGENDE_HEURES_PROFILS, LEGENDE_HEURES_PROFILS_AROARP
from config.variables import VARIABLES_RS_PLOT

from data.radio_sondage import radio_sondage

# -----------------------------------------------------------------------------
#   6. PROFILS VERTICAUX
# -----------------------------------------------------------------------------

today = datetime.date.today()
yesterday = today - timedelta(days=1)
start_day = yesterday
end_day = today

calendrier = html.Div([
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        first_day_of_week=1,
        min_date_allowed=date(2015, 1, 1),
        max_date_allowed=date(yesterday.year, yesterday.month, yesterday.day),
        date=yesterday,
        display_format="DD/MM/YYYY",
        initial_visible_month=date(yesterday.year, yesterday.month, yesterday.day),
    ), html.Div(id='output-container-date-picker-single')], className="twelve columns", style={"text-align": "center", "justifyContent": "center"})

wich_heure = html.Div([
dcc.Checklist(
        options=[{'label': x, 'value': x} for x in LEGENDE_HEURES_PROFILS],
        value=["6h"],
        id='wich_heure')])

labels = []
for model in MODELS_PLOT_RS:
    labels.append(MODELS_PLOT_RS[model]["name"])

# Widget to select curves to plot
multi_select_line_chart_model = html.Div([
    dcc.Dropdown(
        id="multi_select_line_chart_model",
        options=[{"value": value, "label": label} for value, label in zip(MODELS_PLOT_RS, labels)],
        value=["Ab"],
        multi=True,
        clearable=False,
        style={'width':'100%'}
    )], className="six columns", style={"text-align": "center", "justifyContent": "center"})

# Load data at the date of TODAY
data_rs = radio_sondage.radio_sondage(today, MODELS, VARIABLES_RS_PLOT, LEGENDE_HEURES_PROFILS, LEGENDE_HEURES_PROFILS_AROARP)
#aroarp_rs = radio_sondage.pv_aroarp(day,MODELS,VARIABLES_RS_PLOT,LEGENDE_HEURES_PROFILS)

# Create charts to plot
chart = {}
for param in VARIABLES_RS_PLOT:
    chart[param] = go.Figure()

# Convert to HTML
graph = {}
for param in VARIABLES_RS_PLOT:
    graph[param] = dcc.Graph(id='graph_' + param, figure=chart[param])

all_graphs = []
for param in VARIABLES_RS_PLOT:
    all_graphs.append(
        html.Div(
            graph[param],
            className="six columns",
            style={
                'display': 'inline-block'}))

row2 = html.Div(children=all_graphs, className="six columns")

layout_radiosoundings = html.Div([
    html.H1('Profils verticaux'),
    calendrier,
    html.Br(),
    html.Br(),
    wich_heure,
    multi_select_line_chart_model,
    row2,
    html.Br(),
], className="twelve columns", style={"text-align": "center", "justifyContent": "center"})
