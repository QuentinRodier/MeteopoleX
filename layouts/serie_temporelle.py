from dash import html

import datetime
from datetime import timedelta

from config.models import MODELS
from config.variables import VARIABLES_PLOT

from data.selection_data_brut_serieT import selection_data_brut_serieT
import lecture_mesoNH
import lecture_surfex

today = datetime.date.today()
yesterday = today - timedelta(days=1)
start_day = yesterday
end_day = today

# Première extraction des données
data, chart, graph = selection_data_brut_serieT(start_day, end_day)
data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS, VARIABLES_PLOT)
data_surfex = lecture_surfex.surfex(start_day, end_day, MODELS, VARIABLES_PLOT)

graphs_layout = []

for param in VARIABLES_PLOT:
    graphs_layout.append(
        html.Div(
            graph[param],
            className="six columns",
            style={'display': 'inline-block'}
        )
    )

graphs_row = html.Div(
    children=graphs_layout,
    className="six columns"
)

# Mise en page finale de la page "Séries temporelles"
layout_serie_temporelle = html.Div(
    [
        html.H1('Séries temporelles'),
        graphs_row
    ],
    className="row",
    style={"text-align": "center", "justifyContent": "center"}
)