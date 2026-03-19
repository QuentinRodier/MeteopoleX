#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout pour la page d'analyse des biais instantanés.
"""

from dash import html

layout_biais = html.Div(
    [
        html.H1("Biais Instantanés"),

        html.Div(
            id="biais-graphs-container",
            #className="row"
        )
    ],
    style={
        "textAlign": "center",
        "justifyContent": "center"
    }
)
