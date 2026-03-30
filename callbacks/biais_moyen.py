#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Callbacks pour la page d'analyse des biais moyens horaires.
"""

from dash import Input, Output, html, dcc
from dash.exceptions import PreventUpdate
from app import app
from datetime import date, timedelta, datetime
from config.variables import VARIABLES_PLOT
from config.config import MODELS_CONFIG
from data_processing.data_processing_biais_moyen import build_biais_moyen_figures


dynamic_inputs = [
    Input(cfg['dropdown_id'], "value")
    for cfg in MODELS_CONFIG.values()
]


@app.callback(
    Output("biais-moyen-graphs-container", "children"),
    [
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
    ] + dynamic_inputs,
) 
def update_biais_moyen(start_day, end_day, *args):
    
    start_day = date.fromisoformat(start_day)
    end_day = date.fromisoformat(end_day)

    kwargs = {
        cfg['callback_param']: val
        for cfg, val in zip(MODELS_CONFIG.values(), args)
    }
    
    # Construction des figures via le module de traitement
    chartM, graphM = build_biais_moyen_figures(start_day, end_day, **kwargs)
    
    # Génération dynamique des graphes
    graphs = []
    
    for param in VARIABLES_PLOT:
        graphs.append(
            html.Div(
                dcc.Graph(
                    id=f"graphM_{param}",
                    figure=chartM[param],
                    config={'responsive': True}
                ),
                className="six columns",
                style={'display': 'inline-block'}  # Interaction zoom / nbr de colonnes
            )
        )

    return graphs