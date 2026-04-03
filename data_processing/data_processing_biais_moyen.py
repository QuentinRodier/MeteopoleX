
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de traitement des données pour l'analyse des biais moyens horaires.
Construit les figures pour la comparaison du cycle diurne des biais.
"""

import plotly.graph_objects as go
from dash import dcc
import numpy as np

from data.biais_moyen import biais_moyen
from config.variables import VARIABLES, VARIABLES_PLOT
from config.config import MODELS, RESEAUX, MODELS_CONFIG


# Fonction principale appelée par le callback
def build_biais_moyen_figures(start_day, end_day, **kwargs):
    """
    Construit les figures du cycle diurne des biais moyens.
    
    Args:
        start_day: Date de début
        end_day: Date de fin
    
    Returns:
        Tuple (chartM, graphM)
        - chartM: Dictionnaire des figures Plotly par paramètre
        - graphM: Dictionnaire des composants dcc.Graph par paramètre
    """
    
    # ------------------------------------------------------------------
    # CHARGEMENT DES DONNÉES
    # ------------------------------------------------------------------
    biais_moy = biais_moyen(start_day, end_day)
    
    # ------------------------------------------------------------------
    # CONSTRUCTION DES GRAPHIQUES
    # ------------------------------------------------------------------
    chartM = {}
    graphM = {}

    for param in VARIABLES_PLOT:
        # Créer la figure Plotly
        fig = go.Figure()
        
        # Ajout des courbes
        active_selections = {
            model: kwargs.get(cfg['callback_param'], []) or []
            for model, cfg in MODELS_CONFIG.items()
        }

        for model, selections in active_selections.items():

            if MODELS_CONFIG[model].get('is_climatology', False):
                continue

            ui_mapping = MODELS_CONFIG[model]['mapping'] 

            for selection in selections:
                if selection not in ui_mapping:
                    continue

                reseau, style = ui_mapping[selection]

                try:
                    block  = biais_moy.get(param, {}).get(model, {}).get(reseau, {})
                    values = block.get("values")
                    time   = block.get("time")

                    arr = np.array(values, dtype=float)
                    if np.all(np.isnan(arr)):
                        continue

                    CUSTOM_KEY = {"mode", "marker_size"}

                    trace_mode = style.get("mode", "lines+markers") 
                    marker_size = 6
                    line_style = {k: v for k, v in style.items() if k not in CUSTOM_KEY} 

                    if isinstance(time, (list, np.ndarray)):
                        fig.add_trace(go.Scatter(
                            x=time,
                            y=arr,
                            mode=trace_mode,
                            name=selection,
                            line=line_style,
                            marker=dict(size=marker_size),
                            connectgaps=False,
                        ))

                except (KeyError, TypeError, AttributeError):
                    pass
            
        # Mise en forme du graphique
        fig.update_layout(
            title=f"{VARIABLES[param]['title']}",
            xaxis_title="Echéance",
            yaxis_title=f"Biais ({VARIABLES[param]['unit']})",
            hovermode="x unified",
            template="plotly_white",
            height=500,
            width=872,
            showlegend=False,
            shapes=[
                dict(type="line", xref="x", yref="paper", x0=24, x1=24, y0=0, y1=1, line=dict(color="lightgrey", width=1)),
                dict(type="line", xref="x", yref="paper", x0=48, x1=48, y0=0, y1=1, line=dict(color="lightgrey", width=1)), 
                dict(type="line", xref="x", yref="paper", x0=72, x1=72, y0=0, y1=1, line=dict(color="lightgrey", width=1)), 
                dict(type="line", xref="x", yref="paper", x0=96, x1=96, y0=0, y1=1, line=dict(color="lightgrey", width=1)), ]
        )
        
        # Configuration de l'axe X (heures de 0 à 23)
        fig.update_xaxes(
            tickmode='array',
            tickvals=[0, 24, 48, 72, 96],
            ticktext=["J", "J+1", "J+2", "J+3", "J+4"],
            range=[-0.5, 102.5],
            showgrid = False
        )
        
        chartM[param] = fig
        graphM[param] = dcc.Graph(id=f'graphM_{param}', figure=fig)
    
    return chartM , graphM