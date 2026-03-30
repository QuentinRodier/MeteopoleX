#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout pour la page d'analyse des biais moyens horaires (cycle diurne).
"""

from dash import html

layout_biais_moyen = html.Div(
    [
        html.H1("Biais Moyens Horaires"),
        html.Div(
            id="biais-moyen-graphs-container",
            #className="row"
        )
    ],
    style={
        "textAlign": "center",
        "justifyContent": "center"
    }
)