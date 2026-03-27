#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from datetime import timedelta
import numpy as np
import plotly.graph_objects as go
from dash import dcc
import pandas as pd
import re
from itertools import groupby
import matplotlib.colors as mcolors

from data.biais import calcul_biais
from config.variables import VARIABLES, VARIABLES_PLOT
from config.config import RESEAUX, MODELS_CONFIG, today, end, OPACITY_MAX, OPACITY_MIN


def _apply_opacity(color: str, opacity: float) -> str:
    opacity = round(max(0.0, min(1.0, opacity)), 3)
    color = color.strip()

    # rgba() e
    m = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)", color)
    if m:
        return f"rgba({m.group(1)},{m.group(2)},{m.group(3)},{opacity})"

    # rgb()
    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color)
    if m:
        return f"rgba({m.group(1)},{m.group(2)},{m.group(3)},{opacity})"

    try:
        r, g, b = mcolors.to_rgb(color)  
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return f"rgba({r},{g},{b},{opacity})"
    except ValueError:
        return color  # fallback : couleur inconnue, retournée telle quelle



def build_biais_figures(start_day, end_day, **kwargs): 
    """
    Construit les figures des biais instantanés.
    
    Args:
        start_day: Date de début
        end_day: Date de fin
        reseau_arome
        id_user1 à id_user5: IDs des rejeux utilisateur
    
    Returns:
        Tuple (chartB, graphB)
        - chartB: Dictionnaire des figures Plotly par paramètre
        - graphB: Dictionnaire des composants dcc.Graph par paramètre
    """
    
    # ------------------------------------------------------------------
    # CHARGEMENT DES DONNÉES
    # ------------------------------------------------------------------
    biais = calcul_biais(start_day, end_day)
    
    nb_jour = (end_day - start_day).days
    
    # ------------------------------------------------------------------
    # CONSTRUCTION DES GRAPHIQUES
    # ------------------------------------------------------------------
    chartB = {}
    graphB = {}
    
    for param in VARIABLES_PLOT:
        # Créer la figure Plotly
        fig = go.Figure()
        
        active_selections = {
            model: kwargs.get(cfg['callback_param'], []) or []
            for model, cfg in MODELS_CONFIG.items()
        }

        MAX_FORECAST_DAYS = end+1

        for model, selections in active_selections.items():
            ui_mapping = MODELS_CONFIG[model]['mapping']

            for selection in selections:
                if selection not in ui_mapping:
                    continue

                reseau, base_style = ui_mapping[selection]

                try:
                    runs = biais[param][model][reseau].get("runs", {})
                except (KeyError, TypeError, AttributeError):
                    continue

                if not runs:
                    continue

                sorted_dates = sorted(runs.keys())
                line_color = base_style.get("color", "blue")
                legend_shown = False

                for date_str in sorted_dates:
                    series = runs[date_str]
                    if not isinstance(series, pd.Series) or series.empty:
                        continue

                    run_date = datetime.datetime.strptime(date_str, "%Y%m%d").date()

                    cutoff = pd.Timestamp(run_date) + pd.Timedelta(days=MAX_FORECAST_DAYS)
                    series = series[series.index <= cutoff]

                    if series.empty:
                        continue

                    def get_age(t):
                        forecast_date = t.date() if hasattr(t, 'date') else t
                        return max(0, (forecast_date - run_date).days)

                    points = list(zip(series.index, series.values))
                    grouped = groupby(points, key=lambda p: get_age(p[0]))

                    prev_last_point = None
                    first_segment = True

                    for age_days, group in grouped:
                        segment = list(group)
                        if prev_last_point:
                            segment = [prev_last_point] + segment 

                        opacity = OPACITY_MAX - (OPACITY_MAX - OPACITY_MIN) * min(age_days / MAX_FORECAST_DAYS, 1.0)
                        color_str = _apply_opacity(line_color, opacity)

                        seg_x = [p[0] for p in segment]
                        seg_y = [p[1] for p in segment]
                        prev_last_point = segment[-1]

                        if len(seg_x) < 2:
                            continue

                        CUSTOM_KEY = {'color', "mode", "marker_size"}
                        
                        trace_mode = base_style.get("mode", "lines") 
                        marker_size = base_style.get("marker_size", 6)
                        line_style = {k: v for k, v in base_style.items() if k not in CUSTOM_KEY} 

                        fig.add_trace(
                            go.Scatter(
                                x=seg_x,
                                y=seg_y,
                                name=f"{selection}",
                                mode=trace_mode,
                                line={"color": color_str, **line_style},
                                marker=dict(color=color_str, size=marker_size),
                                legendgroup=f"{model}_{selection}",
                                showlegend=(not legend_shown and first_segment),
                                connectgaps=True,
                            )
                        )
                        first_segment = False

                    legend_shown = True

        # MISE EN FORME DU GRAPHIQUE
        fig.update_layout(
            title=VARIABLES[param]['title'],
            xaxis=dict(
                title="Date",
                tickformat='%a %d',
            ),
            yaxis_title=VARIABLES[param]['unit'],
            hovermode="x unified",
            template="plotly_white",
            height=500,
            width=872,
            showlegend=False
        )
        
        chartB[param] = fig
        graphB[param] = dcc.Graph(id=f'graphB_{param}', figure=fig)
    
    return chartB, graphB


