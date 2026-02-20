
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de traitement des données pour l'analyse des biais moyens horaires.
Construit les figures pour la comparaison du cycle diurne des biais.
"""

import plotly.graph_objects as go
from dash import dcc

from data.biais_moyen import biais_moyen
from config.variables import VARIABLES, VARIABLES_PLOT
from config.models import MODELS_BIAIS, RESEAUX


# Fonction principale appelée par le callback
def build_biais_moyen_figures(start_day, end_day):
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
    # CHARGEMENT DES DONNÉES (fonction originale)
    # ------------------------------------------------------------------
    biais_moy, _, _ = biais_moyen(start_day, end_day)
    
    # ------------------------------------------------------------------
    # CONSTRUCTION DES GRAPHIQUES
    # ------------------------------------------------------------------
    chartM = {}
    graphM = {}
    
    for param in VARIABLES_PLOT:
        # Créer la figure Plotly
        fig = go.Figure()
        
        # Configuration des couleurs et styles par modèle
        model_styles = {
            'Rt': {'color': 'limegreen', 'name': 'ARO'},
            'Gt': {'color': 'purple', 'name': 'ARP'}
        }
        
        reseau_styles = {
            "J-1:00_%3600": {'dash': 'dot', 'suffix': ' J-1 00h'},
            "J-1:12_%3600": {'dash': 'dot', 'suffix': ' J-1 12h'},
            "J0:00_%3600": {'dash': 'solid', 'suffix': ' J0 00h'},
            "J0:12_%3600": {'dash': 'solid', 'suffix': ' J0 12h'},
        }
        
        for model in MODELS_BIAIS:
            if model == 'Tf':  # Skip observations
                continue
            
            model_style = model_styles.get(model, {'color': 'gray', 'name': model})
            
            # Ajouter les modèles opérationnels (ARO/ARP)
            '''for reseau in RESEAUX:
                try:
                    values = biais_moy[param][model][reseau]['values']
                    time = biais_moy[param][model][reseau]['time']
                    
                    if values != 0. and len(values) > 1:
                        reseau_style = reseau_styles.get(reseau, {'dash': 'solid', 'suffix': ''})
                        
                        fig.add_trace(go.Scatter(
                            x=time,
                            y=values,
                            mode='lines+markers',
                            name=model_style['name'] + reseau_style['suffix'],
                            line=dict(
                                color=model_style['color'],
                                dash=reseau_style['dash']
                            ),
                            marker=dict(size=6)
                        ))
                except (KeyError, TypeError):
                    pass'''
            
            # Ajouter MésoNH
            try:
                values_mnh = biais_moy[param][model]['MNH']['values']
                time_mnh = biais_moy[param][model]['MNH']['time']
                
                if values_mnh != 0. and len(values_mnh) > 1:
                    fig.add_trace(go.Scatter(
                        x=time_mnh,
                        y=values_mnh,
                        mode='lines+markers',
                        name=f'MésoNH {model_style["name"]}',
                        line=dict(
                            color=model_style['color'],
                            dash='dashdot',
                            width=2
                        ),
                        marker=dict(size=8, symbol='diamond')
                    ))
            except (KeyError, TypeError):
                pass
        
        # Mise en forme du graphique
        fig.update_layout(
            title=f"{VARIABLES[param]['title']}",
            xaxis_title="Heure (UTC)",
            yaxis_title=f"Biais ({VARIABLES[param]['unit']})",
            hovermode="x unified",
            template="plotly_white",
            height=500,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        
        # Configuration de l'axe X (heures de 0 à 23)
        fig.update_xaxes(
            tickmode='linear',
            tick0=0,
            dtick=3,
            range=[-0.5, 23.5]
        )
        
        chartM[param] = fig
        graphM[param] = dcc.Graph(id=f'graphM_{param}', figure=fig)
    
    return chartM, graphM


