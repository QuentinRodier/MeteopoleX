#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import date
from dash import Input, Output, html, dcc

from app import app
from config.variables import VARIABLES_PV_PLOT
from data_processing.data_processing_pv import build_pv_figures


@app.callback(
    Output("pv-graphs-container", "children"),
    [
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
    ],
)
def update_pv(start_day, end_day):

    if start_day:
        start_day = date.fromisoformat(start_day)
    if end_day:
        end_day = date.fromisoformat(end_day)

    figures = build_pv_figures(start_day, end_day)

    graphs = []
    for param in VARIABLES_PV_PLOT:
        graphs.append(
            html.Div(
                dcc.Graph(
                    id=f"graph_PV_{param}",
                    figure=figures[param],
                    config={'responsive': True},
                ),
                className="six columns",
                style={'display': 'inline-block'},
            )
        )

    return graphs
