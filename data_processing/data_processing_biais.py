#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de traitement des données pour l'analyse des biais instantanés.
Construit les figures pour la comparaison des biais modèles vs observations.
"""

import datetime
from datetime import timedelta
import numpy as np
import plotly.graph_objects as go
from dash import dcc

from data.biais import calcul_biais
from config.variables import VARIABLES, VARIABLES_PLOT
from config.models import MODELS_PLOT, RESEAUX
from config.config import arome_mapping, arpege_mapping, surfex_arp_mapping


def build_biais_figures(start_day, end_day, 
                        reseau_arome, reseau_arpege, show_surfex): #, 
                        #id_user1=None, id_user2=None, id_user3=None, 
                        #id_user4=None, id_user5=None):
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
    
    # Valeurs par défaut si None
    '''if reseau_mnh is None:
        reseau_mnh = []'''
    
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
        
        # ------------------------------------------------------------------
        # AJOUT DES REJEUX UTILISATEUR (MésoNH modifié)
        # ------------------------------------------------------------------
        '''types = ['solid', 'dot', 'dash', 'longdash', 'dashdot']
        for j, id_user in enumerate([id_user1, id_user2, id_user3, id_user4, id_user5]):
            if id_user:
                for i in range(nb_jour):
                    date_run = start_day + datetime.timedelta(days=i)
                    today_str = date_run.strftime('%Y%m%d')
                    
                    try:
                        if isinstance(biais[param][id_user][today_str], dict) and \
                           isinstance(biais[param][id_user][today_str].get('values'), 
                                    (list, np.ndarray)):
                            fig.add_trace(
                                go.Scatter(
                                    x=biais[param][id_user][today_str]['time'],
                                    y=biais[param][id_user][today_str]['values'],
                                    line=dict(color='black', dash=types[j]),
                                    name=f'MésoNH modifié (id : {id_user})',
                                    showlegend=(i == 0)  # Légende une seule fois
                                )
                            )
                    except KeyError:
                        pass'''
        
        # ------------------------------------------------------------------
        # AJOUT DES RÉSEAUX ARPEGE AIDA 
        # ------------------------------------------------------------------
        '''for selection in reseau_arp:
            if selection == "Arp_J-1_00h":
                reseau = RESEAUX[0]
                line_param = dict(color='navy', dash='dot')
            elif selection == "Arp_J-1_12h":
                reseau = RESEAUX[1]
                line_param = dict(color='mediumslateblue', dash='dot')
            elif selection == "Arp_J0_00h":
                reseau = RESEAUX[2]
                line_param = dict(color='navy')
            elif selection == "Arp_J0_12h":
                reseau = RESEAUX[3]
                line_param = dict(color='mediumslateblue')
            else:
                continue
            
            try:
                if isinstance(biais[param]['Gt'][reseau]['values'], (list, np.ndarray)):
                    fig.add_trace(
                        go.Scatter(
                            x=biais[param]['Gt'][reseau]['time'],
                            y=biais[param]['Gt'][reseau]['values'],
                            line=line_param,
                            name=selection
                        )
                    )
            except (KeyError, TypeError):
                pass'''
        
        # ------------------------------------------------------------------
        # AJOUT DES RÉSEAUX AROME AIDA
        # ------------------------------------------------------------------
        '''for selection in reseau_aro:
            if selection == "Aro_J-1_00h":
                reseau = RESEAUX[0]
                line_param = dict(color='green', dash='dot')
            elif selection == "Aro_J-1_12h":
                reseau = RESEAUX[1]
                line_param = dict(color='olive', dash='dot')
            elif selection == "Aro_J0_00h":
                reseau = RESEAUX[2]
                line_param = dict(color='green')
            elif selection == "Aro_J0_12h":
                reseau = RESEAUX[3]
                line_param = dict(color='olive')
            else:
                continue
            
            try:
                if isinstance(biais[param]['Rt'][reseau]['values'], (list, np.ndarray)):
                    fig.add_trace(
                        go.Scatter(
                            x=biais[param]['Rt'][reseau]['time'],
                            y=biais[param]['Rt'][reseau]['values'],
                            line=line_param,
                            name=selection
                        )
                    )
            except (KeyError, TypeError):
                pass'''

        # ------------------------------------------------------------------
        # AJOUT DES RÉSEAUX AROME 
        # ------------------------------------------------------------------
        for selection in (reseau_arome or []):
            if selection not in arome_mapping:
                continue

            reseau, style = arome_mapping[selection]

            try:
                block = biais[param]['Arome'][reseau]
                time = block.get("time")
                values = block.get("values")

                if isinstance(time, (list, np.ndarray)) and isinstance(values, (list, np.ndarray)):
                    fig.add_trace(
                        go.Scatter(
                            x=time,
                            y=values,
                            name=f"{selection}",
                            line=style,
                        )
                    )
            except (KeyError, TypeError, AttributeError):
                pass
            
        # ------------------------------------------------------------------
        # AJOUT DES RÉSEAUX ARPEGE 
        # ------------------------------------------------------------------
        for selection in (reseau_arpege or []):
            if selection not in arpege_mapping:
                continue

            reseau, style = arpege_mapping[selection]

            try:
                block = biais[param]['Arpege'][reseau]
                time = block.get("time")
                values = block.get("values")

                if isinstance(time, (list, np.ndarray)) and isinstance(values, (list, np.ndarray)):
                    fig.add_trace(
                        go.Scatter(
                            x=time,
                            y=values,
                            name=f"{selection}",
                            connectgaps=True,
                            line=style,
                        )
                    )
            except (KeyError, TypeError, AttributeError):
                pass

       # ------------------------------------------------------------------
       # AJOUT DES COURBES SURFEX
       # ------------------------------------------------------------------
        if show_surfex:
            try:
                block = biais[param].get('Surfex_arpege', {}).get(RESEAUX[0], {})
                time   = block.get("time")
                values = block.get("values")

                if isinstance(time, (list, np.ndarray)) and isinstance(values, (list, np.ndarray)):
                    fig.add_trace(
                        go.Scatter(
                            x=time,
                            y=values,
                            name="SURFEX",
                            line=surfex_arp_mapping,
                        )
                    )
            except (KeyError, TypeError, AttributeError):
                pass

        # ------------------------------------------------------------------
        # AJOUT DES COURBES MESO-NH
        # ------------------------------------------------------------------
        '''courbe_affichee = []
        for selection in reseau_mnh:
            for i in range(nb_jour + 1):
                day = start_day + timedelta(days=i)
                today_str = day.strftime('%Y%m%d')
                
                # Gestion de la légende (affichée une seule fois)
                if selection not in courbe_affichee and \
                   MODELS_PLOT[selection]['name'] in biais[param]:
                    courbe_affichee.append(selection)
                    afficher_legende = True
                else:
                    afficher_legende = False
                
                try:
                    if isinstance(biais[param][MODELS_PLOT[selection]['name']][today_str].get('values'), 
                                (list, np.ndarray)):
                        fig.add_trace(
                            go.Scatter(
                                x=biais[param][MODELS_PLOT[selection]['name']][today_str]['time'],
                                y=biais[param][MODELS_PLOT[selection]['name']][today_str]['values'],
                                marker={"color": MODELS_PLOT[selection]['color']},
                                mode="lines",
                                name=selection,
                                showlegend=afficher_legende
                            )
                        )
                except (KeyError, TypeError):
                    pass'''
        
        # ------------------------------------------------------------------
        # AJOUT DES COURBES SURFEX
        # ------------------------------------------------------------------
        '''courbe_affichee_surfex = []
        for selection in reseau_surfex:
            for i in range(nb_jour + 1):
                day = start_day + timedelta(days=i)
                today_str = day.strftime('%Y%m%d')
                
                # Gestion de la légende
                if selection not in courbe_affichee_surfex and \
                   MODELS_PLOT[selection]['name'] in data_surfex.get(today_str, {}) and \
                   isinstance(data_surfex[today_str][MODELS_PLOT[selection]['name']].get('tmp_2m'), 
                            (list, np.ndarray)):
                    courbe_affichee_surfex.append(selection)
                    afficher_legende_surfex = True
                else:
                    afficher_legende_surfex = False
                
                try:
                    if isinstance(data_surfex[today_str][MODELS_PLOT[selection]['name']].get(param), 
                                (list, np.ndarray)):
                        fig.add_trace(
                            go.Scatter(
                                x=data_surfex[today_str]['time'],
                                y=data_surfex[today_str][MODELS_PLOT[selection]['name']][param],
                                line=dict(
                                    color=MODELS_PLOT[selection]['color'],
                                    dash='dashdot'
                                ),
                                name=selection,
                                showlegend=afficher_legende_surfex
                            )
                        )
                except (KeyError, TypeError):
                    pass'''
        
        # ------------------------------------------------------------------
        # MISE EN FORME DU GRAPHIQUE
        # ------------------------------------------------------------------
        fig.update_layout(
            title=VARIABLES[param]['title'],
            xaxis_title="Date et heure",
            yaxis_title=VARIABLES[param]['unit'],
            hovermode="x unified",
            template="plotly_white",
            height=450,
            width=800,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        chartB[param] = fig
        graphB[param] = dcc.Graph(id=f'graphB_{param}', figure=fig)
    
    return chartB, graphB


