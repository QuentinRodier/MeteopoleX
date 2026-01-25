from dash import html

import datetime
from datetime import date, timedelta

from config.variables import VARIABLES_PLOT

from data.biais import calcul_biais

today = datetime.date.today()
yesterday = today - timedelta(days=1)
start_day = yesterday
end_day = today

biais, chartB, graphB = calcul_biais(start_day, end_day)

all_graphsB = []

for param in VARIABLES_PLOT:
    all_graphsB.append(
        html.Div(
            graphB[param],
            className="six columns",
            style={
                'display': 'inline-block'}))

row2 = html.Div(children=all_graphsB, className="twelve columns")

layout_biais = html.Div([
    html.H1('Biais'),
    row2,
], className="twelve columns", style={"text-align": "center", "justifyContent": "center"})
