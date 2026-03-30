# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from dash import html

layout_pv = html.Div(
    [
        html.H1("Panneaux photovoltaïques"),

        html.Div(
            id="pv-graphs-container",
        ),
    ],
    style={
        "textAlign": "center",
        "justifyContent": "center",
    },
)