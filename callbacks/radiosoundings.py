#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date, timedelta
import datetime

from dash import Input, Output, html, dcc
from app import app

from config.variables import VARIABLES_RS_PLOT
from config.models import MODELS, LEGENDE_HEURES_PROFILS, LEGENDE_HEURES_PROFILS_AROARP

from data.radio_sondage import radio_sondage
from data_processing.data_processing_rs import build_rs_figures


@app.callback(
    Output("rs-graphs-container", "children"),
    [
        Input("wich_heure", "value"),
        Input("my-date-picker-single", "date"),
        Input("multi_select_line_chart_model", "value"),
    ],
)
def update_rs(wich_heure, date_value, model_choisi):

    if date_value is not None:
        date_object = date.fromisoformat(date_value)
    else:
        date_object = datetime.date.today() - timedelta(days=1)

    # Lecture des données (inchangée)
    data_rs = radio_sondage(
        date_object, MODELS,
        VARIABLES_RS_PLOT,
        LEGENDE_HEURES_PROFILS,
        LEGENDE_HEURES_PROFILS_AROARP,
    )

    # Construction des figures
    figures = build_rs_figures(data_rs, wich_heure or [], model_choisi or [])

    graphs = []
    for param in VARIABLES_RS_PLOT:
        graphs.append(
            html.Div(
                dcc.Graph(
                    id=f"graph_{param}",
                    figure=figures[param],
                    config={'responsive': True},
                ),
                className="six columns",
                style={'display': 'inline-block'},
            )
        )

    return graphs