from dash import html
import datetime
from datetime import date, timedelta
from data.selection_data_pv import selection_donnees_PV
from config.variables import VARIABLES_PV_PLOT

# Période par défaut
today = datetime.date.today()
yesterday = today - timedelta(days=1)
start_day = yesterday
end_day = today

# Extraction des données PV
data_PV, chart_PV, graph_PV = selection_donnees_PV(start_day, end_day)

all_graphs_PV = []
for param in VARIABLES_PV_PLOT:
    all_graphs_PV.append(html.Div(graph_PV[param], className="six columns", style={'display': 'inline-block'}))
#all_graphs_PV.append(html.Div(graph_PV_2,className="six columns",style={'display': 'inline-block'}))
row = html.Div(children=all_graphs_PV, className="six columns")

# Ces dernières lignes sont la mise en forme finale de la page
layout_pv = html.Div([html.H1('Panneaux photovoltaïques'), row], 
                     className="row",
                     style={"text-align": "center", "justifyContent": "center"})