from dash import Input, Output, html, dcc
from app import app
from datetime import date
from config.variables import VARIABLES_PLOT
from config.config import MODELS_CONFIG
from data_processing.data_processing_serieT import build_series_figures


dynamic_inputs = [
    Input(cfg['dropdown_id'], "value")
    for cfg in MODELS_CONFIG.values()
]


@app.callback(
    Output("series-graphs-container", "children"),
    [
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
        Input("multi_select_line_chart_obs", "value"),
    ] + dynamic_inputs,
)
def update_line(start_day, end_day, reseau_obs, *args):

    if start_day:
        start_day = date.fromisoformat(start_day)
    if end_day:
        end_day = date.fromisoformat(end_day)

    kwargs = {
        cfg['callback_param']: val
        for cfg, val in zip(MODELS_CONFIG.values(), args)
    }

    figures = build_series_figures(start_day, end_day, reseau_obs, **kwargs)

    graphs = []

    for param in VARIABLES_PLOT:
        graphs.append(
            html.Div(
                dcc.Graph(
                    id=f"graph_{param}",
                    figure=figures[param],
                    config={'responsive':True}
                ),
                className="six columns",
                style={'display': 'inline-block'}       #Intéraction zoom / nbr de colonnes
            )
        )

    return graphs