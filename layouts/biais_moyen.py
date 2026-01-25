from dash import html

import datetime
from datetime import date, timedelta

from config.variables import VARIABLES_PLOT

from data.biais_moyen import biais_moyen

today = datetime.date.today()
yesterday = today - timedelta(days=1)
start_day = yesterday
end_day = today

biais_moy, chartM, graphM = biais_moyen(start_day, end_day)

all_graphsM = []

for param in VARIABLES_PLOT:
    all_graphsM.append(
        html.Div(
            graphM[param],
            className="six columns",
            style={
                'display': 'inline-block'}))

row3 = html.Div(children=all_graphsM, className="twelve columns")

layout_biais_moyen = html.Div([
    html.H1('Biais moyens'),
    row3,
], className="twelve columns", style={"text-align": "center", "justifyContent": "center"})