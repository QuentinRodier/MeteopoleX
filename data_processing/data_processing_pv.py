#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import plotly.graph_objects as go

from config.variables import VARIABLES_PV_PLOT, VARIABLES
from config.models import MODELS_PV_CONFIG
from data.data_loader import data_loader_pv


def build_pv_figures(start_day, end_day):

    data = data_loader_pv.load(start_day, end_day)

    figures = {param: go.Figure() for param in VARIABLES_PV_PLOT}

    for param in VARIABLES_PV_PLOT:

        for model, cfg in MODELS_PV_CONFIG.items():

            model_data = data[param].get(model, {})
            values     = model_data.get('values')
            time       = model_data.get('time')

            # Ignorer les séries vides
            if values is None or time is None:
                continue
            if not isinstance(values, (list, np.ndarray)) or len(values) == 0:
                continue

            # Construction du style de ligne depuis la config
            line_style = dict(color=cfg["color"])
            if cfg.get("dash"):
                line_style["dash"] = cfg["dash"]

            figures[param].add_trace(
                go.Scatter(
                    x=time,
                    y=values.data if hasattr(values, 'data') else values,
                    mode="lines",
                    name=cfg["label"],
                    line=line_style,
                    showlegend=True,
                )
            )

        # Layout
        figures[param].update_layout(
            height=450,
            width=800,
            xaxis_title="Date et heure",
            yaxis_title=str(VARIABLES[param]['unit']),
            title=VARIABLES[param]['title'],
            hovermode="x unified",
            template="plotly_white",
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
            ),
        )

    return figures
