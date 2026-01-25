#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------------------
##########################################################################################
#-----------------------------------------------------------------------------------------

# Organisation de ce code :
# Toutes les pages du site se touvent ici, elles sont délimités par leur titre de type :

# -----------------------------------------------------------------------------
#   2. SERIES TEMPORELLES : Comparaison Obs/Modèles
# -----------------------------------------------------------------------------

# La plupart des pages contiennent plusieurs parties des 4 ci-dessous, dans cet ordre :
# x.1. DONNEES
# x.2. WIDGETS
# x.3. CALLBACKS
# x.4. LAYOUT

# Les données contiennent les fonctions nécessaires à la récupérations des valeurs de tous les modèles.

# Les widgets sont les objets qui permettent de choisir quoi afficher (quelles courbes à quelle date/heure/période)

# Les callbacks actualisent la page.
# Ils ont obligatoirement besoin d'une liste Output et une liste Input pour fonctionner
# Ils contiennent la/les fonction(s) qui vont actualiser l'/les Output(s)
# à chaque fois qu'un/que des Input(s) est/sont modifié(s)

# Le layout est la mise en page.

# La dernière partie du code est :
# -----------------------------------------------------------------------------
#   9. GESTION DES PAGES
# -----------------------------------------------------------------------------

# qui est destinée à la gestion des pages lors de la navigation sur le site.

#-----------------------------------------------------------------------------------------
##########################################################################################
#-----------------------------------------------------------------------------------------

from app import app
# Callbacks
#import callbacks # force le chargement des callbacks

import os
import time
import datetime
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import matplotlib.dates as mdates
import base64                                   # encode binaire en ASCII. Rq: pybase64 utile pour accélérer ?

# Biais computation
import numpy as np
import pandas as pd                             # dataframes pour les calculs biais obs/modèle (grille temporelle différente)

# Dash Vue
import flask                                    # web framework (faire du web facilement)
import dash                                     # Python framework for building analytical web applications.
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import json

# Layouts
from layouts.sidebar import layout_sidebar
from layouts.notice import layout_notice
from layouts.paneaux_solaire import layout_pv
from layouts.surfex import layout_surfex
from layouts.radiosoundings import layout_radiosoundings

# Config static
from config.variables import VARIABLES_PLOT, VARIABLES, VARIABLES_PV_PLOT, VARIABLES_RS_PLOT, VARIABLES_RS
from config.models import MODELS_PLOT, MODELS_PLOT_RS, MODELS, MODELS_BIAIS, MODELS_PV, RESEAUX, LEGENDE_HEURES_PROFILS, LEGENDE_HEURES_PROFILS_AROARP


# Data extraction
import read_aida
import lecture_mesoNH
import lecture_surfex
import read_arome
from data.selection_data_pv import selection_donnees_PV

# Les programmes appelés par navigation.py
import mesonh

# -----------------------------------------------------------------------------
#   1. CREATION App Object
# -----------------------------------------------------------------------------

# 1.1 CREATION CSS
# -----------------------------------------------------------------------------

#external_stylesheets = ['assets/bootstrap.min.css']

#app = dash.Dash(
#    __name__,
#    external_stylesheets=external_stylesheets,
#    suppress_callback_exceptions=True,
#    title='MeteopoleX'
#    requests_pathname_prefix='/MeteopoleX/',
#    routes_pathname_prefix='/'
#)

#app.css.config.serve_locally = True
#app.scripts.config.serve_locally = True
#server = app.server


# -----------------------------------------------------------------------------
#   Styles globaux
# -----------------------------------------------------------------------------

CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


# -----------------------------------------------------------------------------
#   1.2 WIDGETS
# -----------------------------------------------------------------------------

today = datetime.date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)

# Période par défaut
start_day = yesterday
end_day = today

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    layout_sidebar,
    content
])

# -----------------------------------------------------------------------------
#   3. SERIES TEMPORELLES : Comparaison Obs/Modèles
# -----------------------------------------------------------------------------

#   3.1. DONNEES : Lecture des données dans AIDA
# -----------------------------------------------------------------------------

def selection_donnees(start_day, end_day):
    """
    Récupère les données disponibles sur AIDA :
    - Observations Météopole Flux
    - Modèles Arpège, Arome (ancienne et nouvelle version)
    """

    # Conversion des dates en jour de l'année
    start_doy = datetime.datetime(
        start_day.year, start_day.month, start_day.day
    ).strftime('%j')

    end_doy = datetime.datetime(
        end_day.year, end_day.month, end_day.day
    ).strftime('%j')

    data = {}
    charts = {}
    graphs = {}

    # -------------------------------------------------------------------------
    # Boucle principale sur les paramètres
    # -------------------------------------------------------------------------
    for param in VARIABLES_PLOT:

        data.setdefault(param, {})

        # ---------------------------------------------------------------------
        # Observations
        # ---------------------------------------------------------------------
        obs_model = 'Tf'
        data[param][obs_model] = {}

        obs_index = VARIABLES[param]["index_obs"]

        values_obs, time_obs, _ = read_aida.donnees(
            start_doy,
            end_doy,
            str(start_day.year),
            str(end_day.year),
            obs_index,
            obs_model
        )

        data[param][obs_model]['values'] = values_obs
        data[param][obs_model]['time'] = time_obs

        # ---------------------------------------------------------------------
        # Modèles numériques
        # ---------------------------------------------------------------------
        for model in MODELS:

            data[param].setdefault(model, {})

            for reseau in RESEAUX:

                data[param][model].setdefault(reseau, {})

                # -------------------------------------------------------------
                # AROME nouvelle version (enveloppes)
                # -------------------------------------------------------------
                if model == "Arome":

                    model_data = data[param][model][reseau]

                    model_data.update({
                        'values_mean': {},
                        'values_mean_plus_std': {},
                        'values_mean_moins_std': {},
                        'values_max': {},
                        'values_min': {},
                        'values_P1': {},
                        'values_P2': {},
                        'values_P3': {},
                        'values_P4': {},
                        'time': {}
                    })

                    param_arome = VARIABLES[param]['index_model_arome']

                    if param_arome is not None:

                        arome_data = read_arome.donnees(
                            start_day, end_day, reseau, param_arome
                        )

                        if not arome_data.empty:

                            time_index = arome_data.index

                            model_data['values_mean'] = (
                                arome_data.groupby(time_index).mean()[param_arome]
                            )

                            std = arome_data.groupby(time_index).std()[param_arome]

                            model_data['values_mean_plus_std'] = (
                                model_data['values_mean'] + std
                            )
                            model_data['values_mean_moins_std'] = (
                                model_data['values_mean'] - std
                            )

                            model_data['values_max'] = (
                                arome_data.groupby(time_index).max()[param_arome]
                            )
                            model_data['values_min'] = (
                                arome_data.groupby(time_index).min()[param_arome]
                            )

                            model_data['values_P1'] = arome_data.loc[
                                arome_data['Point'] == 11, param_arome
                            ]
                            model_data['values_P2'] = arome_data.loc[
                                arome_data['Point'] == 15, param_arome
                            ]
                            model_data['values_P3'] = arome_data.loc[
                                arome_data['Point'] == 6, param_arome
                            ]
                            model_data['values_P4'] = arome_data.loc[
                                arome_data['Point'] == 1, param_arome
                            ]

                            model_data['time'] = model_data['values_P4'].index

                # -------------------------------------------------------------
                # AROME / ARPEGE ancienne version (AIDA)
                # -------------------------------------------------------------
                else:

                    model_index = f"{VARIABLES[param]['index_model']}_{reseau}"

                    values_mod, time_mod, _ = read_aida.donnees(
                        start_doy,
                        end_doy,
                        str(start_day.year),
                        str(end_day.year),
                        model_index,
                        model
                    )

                    data[param][model][reseau]['values'] = values_mod
                    data[param][model][reseau]['time'] = time_mod

                    # Correction ARPEGE : H-1:59 → H:00
                    if time_mod is not None:
                        for i, ts in enumerate(time_mod):
                            if ts.minute == 59:
                                time_mod[i] = ts + datetime.timedelta(minutes=1)

                    # Décalage des flux à H:30
                    if param in [
                        'flx_mvt', 'flx_chaleur_sens', 'flx_chaleur_lat',
                        'SWD', 'SWU', 'LWD', 'LWU'
                    ]:
                        if time_mod is not None:
                            for i, ts in enumerate(time_mod):
                                time_mod[i] = ts - datetime.timedelta(minutes=30)

        # ---------------------------------------------------------------------
        # Création des figures
        # ---------------------------------------------------------------------
        charts[param] = go.Figure()
        graphs[param] = dcc.Graph(
            id=f'graph_{param}',
            figure=charts[param]
        )

    return data, charts, graphs

# Première extraction des données
data, chart, graph = selection_donnees(start_day, end_day)
#print(data['tmp_2m']['Arome']['J0:00_%3600']['values_P1'])
#print(data['tmp_2m']['Arome']['J0:00_%3600']['time'])
#print(data['tmp_2m']['Gt']['J0:00_%3600']['values'])
#print(data['tmp_2m']['Gt']['J0:00_%3600']['time'])

# Pour ajouter un nouveau run de MesoNH, changer la liste MODELS : en créer une autre
data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS, VARIABLES_PLOT)
data_surfex = lecture_surfex.surfex(start_day, end_day, MODELS, VARIABLES_PLOT)

# -----------------------------------------------------------------------------
#   3.2 CALLBACKS
# -----------------------------------------------------------------------------
# Contient les fonctions qui actualisent les Outputs lorsque les Inputs changent

output_graphs = []

for param in VARIABLES_PLOT:
    output_graphs.append(Output(f'graph_{param}', 'figure'))


@app.callback(
    output_graphs,
    [
        Input('multi_select_line_chart_obs', 'value'),
        Input('multi_select_line_chart_ARP', 'value'),
        Input('multi_select_line_chart_ARO', 'value'),
        Input('multi_select_line_chart_AROME', 'value'),
        Input('multi_select_line_chart_MNH', 'value'),
        Input('multi_select_line_chart_SURFEX', 'value'),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('id_user1', 'value'),
        Input('id_user2', 'value'),
        Input('id_user3', 'value'),
        Input('id_user4', 'value'),
        Input('id_user5', 'value'),
    ],
)
def update_line(
    reseau_obs,
    reseau_arp,
    reseau_aro,
    reseau_arome,
    reseau_mnh,
    reseau_surfex,
    start_day,
    end_day,
    id_user1,
    id_user2,
    id_user3,
    id_user4,
    id_user5,
):
    """
    Callback principal mettant à jour l'ensemble des graphiques.
    L'ordre des arguments correspond strictement à celui des Inputs.
    """

    # -------------------------------------------------------------------------
    # Conversion des dates
    # -------------------------------------------------------------------------
    if start_day is not None:
        start_day = date.fromisoformat(start_day)

    if end_day is not None:
        end_day = date.fromisoformat(end_day)


    # -------------------------------------------------------------------------
    # Chargement des données
    # -------------------------------------------------------------------------
    data, chart, graph = selection_donnees(start_day, end_day)

    data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS, VARIABLES_PLOT)
    data_surfex = lecture_surfex.surfex(start_day, end_day, MODELS, VARIABLES_PLOT)


    # -------------------------------------------------------------------------
    # Initialisation des figures
    # -------------------------------------------------------------------------
    for param in VARIABLES_PLOT:
        chart[param] = go.Figure()


    # -------------------------------------------------------------------------
    # Rejeux MésoNH (par id utilisateur)
    # -------------------------------------------------------------------------
    line_styles = ['solid', 'dot', 'dash', 'longdash', 'dashdot']

    for idx, user_id in enumerate([id_user1, id_user2, id_user3, id_user4, id_user5]):

        data_user = lecture_mesoNH.mesoNH_user(start_day, end_day, user_id, VARIABLES_PLOT)
        nb_days = (end_day - start_day).days

        displayed_curves = []

        for i in range(nb_days + 1):
            date_run = start_day + datetime.timedelta(days=i)
            day_str = date_run.strftime('%Y%m%d')

            if (
                user_id not in displayed_curves
                and 'tmp_2m' in data_user.get(day_str, {})
            ):
                displayed_curves.append(user_id)
                show_legend = True
            else:
                show_legend = False

            for param in VARIABLES_PLOT:
                try:
                    if isinstance(data_user[day_str][param], (list, np.ndarray)):
                        chart[param].add_trace(
                            go.Scatter(
                                x=data_user[day_str]['time'],
                                y=data_user[day_str][param],
                                line=dict(color='black', dash=line_styles[idx]),
                                name=f'MésoNH modifié (id : {user_id})',
                                showlegend=show_legend,
                            )
                        )
                except KeyError:
                    pass


    # -------------------------------------------------------------------------
    # Rejeux SURFEX (par id utilisateur)
    # -------------------------------------------------------------------------
    for idx, user_id in enumerate([id_user1, id_user2, id_user3, id_user4, id_user5]):

        data_user = lecture_surfex.surfex_user(start_day, end_day, user_id, VARIABLES_PLOT)
        nb_days = (end_day - start_day).days

        displayed_curves = []

        for i in range(nb_days + 1):
            date_run = start_day + datetime.timedelta(days=i)
            day_str = date_run.strftime('%Y%m%d')

            if (
                user_id not in displayed_curves
                and 'tmp_2m' in data_user.get(day_str, {})
            ):
                displayed_curves.append(user_id)
                show_legend = True
            else:
                show_legend = False

            for param in VARIABLES_PLOT:
                try:
                    if isinstance(data_user[day_str][param], (list, np.ndarray)):

                        if param in [
                            'flx_mvt', 'flx_chaleur_sens', 'flx_chaleur_lat',
                            'SWD', 'SWU', 'LWD', 'LWU'
                        ]:
                            x_time = data_user[day_str]['timeFlux']
                        else:
                            x_time = data_user[day_str]['time']

                        chart[param].add_trace(
                            go.Scatter(
                                x=x_time,
                                y=data_user[day_str][param],
                                line=dict(color='black', dash=line_styles[idx]),
                                name=f'SURFEX modifié (id : {user_id})',
                                showlegend=show_legend,
                            )
                        )
                except KeyError:
                    pass


    # -------------------------------------------------------------------------
    # Observations Météopole Flux
    # -------------------------------------------------------------------------
    for selection in reseau_obs:
        if selection == "Obs":
            for param in VARIABLES_PLOT:
                if isinstance(data[param]['Tf']['values'], (list, np.ndarray)):
                    chart[param].add_trace(
                        go.Scatter(
                            x=data[param]['Tf']['time'],
                            y=data[param]['Tf']['values'].data,
                            marker={"color": "red"},
                            mode="lines",
                            name=selection,
                        )
                    )


    # -------------------------------------------------------------------------
    # Arpège
    # -------------------------------------------------------------------------
    for selection in reseau_arp:

        if selection == "Arp_J-1_00h":
            reseau = RESEAUX[0]
            line_param = dict(color='navy', dash='dot')
            visible_settings = True

        if selection == "Arp_J-1_12h":
            reseau = RESEAUX[1]
            line_param = dict(color='mediumslateblue', dash='dot')
            visible_settings = 'legendonly'

        if selection == "Arp_J0_00h":
            reseau = RESEAUX[2]
            line_param = dict(color='navy')
            visible_settings = True

        if selection == "Arp_J0_12h":
            reseau = RESEAUX[3]
            line_param = dict(color='mediumslateblue')
            visible_settings = True

        for param in VARIABLES_PLOT:
            if isinstance(data[param]['Gt'][reseau]['values'], (list, np.ndarray)):
                chart[param].add_trace(
                    go.Scatter(
                        x=data[param]['Gt'][reseau]['time'],
                        y=data[param]['Gt'][reseau]['values'].data,
                        line=line_param,
                        visible=visible_settings,
                        name=selection,
                    )
                )


    # -------------------------------------------------------------------------
    # AROME ancienne version
    # -------------------------------------------------------------------------
    for selection in reseau_aro:

        if selection == "Aro_J-1_00h":
            reseau = RESEAUX[0]
            line_param = dict(color='green', dash='dot')

        if selection == "Aro_J-1_12h":
            reseau = RESEAUX[1]
            line_param = dict(color='olive', dash='dot')

        if selection == "Aro_J0_00h":
            reseau = RESEAUX[2]
            line_param = dict(color='green')

        if selection == "Aro_J0_12h":
            reseau = RESEAUX[3]
            line_param = dict(color='olive')

        for param in VARIABLES_PLOT:
            if isinstance(data[param]['Rt'][reseau]['values'], (list, np.ndarray)):
                chart[param].add_trace(
                    go.Scatter(
                        x=data[param]['Rt'][reseau]['time'],
                        y=data[param]['Rt'][reseau]['values'].data,
                        line=line_param,
                        name=selection,
                    )
                )


    # -------------------------------------------------------------------------
    # Mise à jour finale des figures
    # -------------------------------------------------------------------------
    updated_charts = []

    for param in VARIABLES_PLOT:
        chart[param].update_layout(
            height=450,
            width=800,
            xaxis_title="Date et heure",
            yaxis_title=str(VARIABLES[param]['unit']),
            title=VARIABLES[param]['title'],
        )
        updated_charts.append(chart[param])

    return updated_charts

# -----------------------------------------------------------------------------
#   3.3 LAYOUT
# -----------------------------------------------------------------------------

# Chaque graphique est placé dans une Div individuelle afin de contrôler
# l'affichage (2 graphiques par ligne environ via "six columns")

graphs_layout = []

for param in VARIABLES_PLOT:
    graphs_layout.append(
        html.Div(
            graph[param],
            className="six columns",
            style={'display': 'inline-block'}
        )
    )

graphs_row = html.Div(
    children=graphs_layout,
    className="six columns"
)

# Mise en page finale de la page "Séries temporelles"
obs_modeles_layout = html.Div(
    [
        html.H1('Séries temporelles'),
        graphs_row
    ],
    className="row",
    style={"text-align": "center", "justifyContent": "center"}
)



# -----------------------------------------------------------------------------
#   4. BIAIS OBS/MODELES
# -----------------------------------------------------------------------------

#   4.1 CALCUL DES BIAIS
# -----------------------------------------------------------------------------

def calcul_biais(start_day, end_day):

    doy1 = datetime.datetime(int(start_day.year), int(
        start_day.month), int(start_day.day)).strftime('%j')
    doy2 = datetime.datetime(int(end_day.year), int(end_day.month), int(end_day.day)).strftime('%j')

    chartB = {}
    graphB = {}

    biais = {}
    #biais_mnh = {}

    # création d'un dataframe vide avec les valeurs des dates de la période
    # (start_day,end_day), toutes les heures car modele OPER = sorties
    # horaires.
    dt = mdates.num2date(mdates.drange(datetime.datetime(int(start_day.year),
                                                         int(start_day.month),
                                                         int(start_day.day)),
                                       datetime.datetime(int(end_day.year),
                                                         int(end_day.month),
                                                         int(end_day.day)),
                                       datetime.timedelta(minutes=30)))

    dataallyear = [i.replace(tzinfo=None) for i in dt]
    dataframe_sanstrou = pd.DataFrame(index=dataallyear)

    # Données des simulations MésoNH OPER
    data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS_BIAIS, VARIABLES_PLOT)

    for param in VARIABLES_PLOT:
        if param not in biais:
            biais[param] = {}
        for model in MODELS_BIAIS:
            id_aida_obs = VARIABLES[param]["index_obs"]
            (values_obs, time_obs, header_obs) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year), id_aida_obs, "Tf")
            if model not in biais[param]:
                biais[param][model] = {}
            for reseau in RESEAUX:
                if reseau not in biais[param][model]:
                    biais[param][model][reseau] = {}
                id_aida_mod = VARIABLES[param]["index_model"] + "_" + reseau
                (values_mod, time_mod, header_mod) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year), id_aida_mod, model)

                # Correction des données ARPEGE parfois datées à H-1:59 au lieu de H:00
                if time_mod is not None:
                    i = 0
                    for ts in time_mod:
                        if ts.minute == 59.:
                            time_mod[i] = time_mod[i] + datetime.timedelta(minutes=1)
                            i = i + 1
                        else:
                            i = i + 1

                # Les flux pour AROME et ARPEGE OPER sont agrégés entre H et H+1 : On les
                # replace à H:30 pour davantage de réalisme
                if param == 'flx_mvt' or param == 'flx_chaleur_sens' or param == 'flx_chaleur_lat' or param == 'SWD' or param == 'SWU' or param == 'LWD' or param == 'LWU':
                    if time_mod is not None:
                        i = 0
                        for ts in time_mod:
                            time_mod[i] = time_mod[i] - datetime.timedelta(minutes=30)
                            i = i + 1

                if values_mod is None or values_obs is None:
                    biais[param][model][reseau]['values'] = np.nan
                else:
                    # Création de dataframes des valeurs obs et modèles
                    df_obs = pd.DataFrame(list(values_obs), index=(time_obs))
                    df_mod = pd.DataFrame(list(values_mod), index=(time_mod))

                    # concordance des dates sur le dataframe défini au début
                    df_obs = dataframe_sanstrou.join(df_obs)
                    df_mod = dataframe_sanstrou.join(df_mod)

                    # Calcul du biais
                    df_biais = df_mod - df_obs

                    #df_biais = dataframe_sanstrou.join(df_biais)
                    #df_biais = df_biais.fillna(0)
                    df_biais = df_biais.dropna()
                    df_biais.index = pd.to_datetime(df_biais.index)

                    # Passage du dataframes "biais" en listes pour intégrations dans les
                    # dictionnaires biais
                    biais[param][model][reseau]['values'] = list(df_biais[0])
                    biais[param][model][reseau]['time'] = list(df_biais.index)
                    
            # Pour MesoNH, une simulation = 1 jour, calcul du biais par jour
            # TODO: optimisation
            nb_jour = (end_day - start_day).days

            for i in range(nb_jour):

                day = start_day + timedelta(days=i)
                today_str = day.strftime('%Y%m%d')

                day_after = start_day + timedelta(days=i + 1)
                after_str = day_after.strftime('%Y%m%d')

                day_1 = datetime.datetime(int(day.year), int(
                    day.month), int(day.day)).strftime('%j')
                day_2 = datetime.datetime(int(day_after.year), int(
                    day_after.month), int(day_after.day)).strftime('%j')

                id_aida_obs = VARIABLES[param]["index_obs"]
                (values_obs, time_obs, header_obs) = read_aida.donnees(
                    day_1, day_2, str(start_day.year), str(end_day.year), id_aida_obs, "Tf")

                dt_mnh = mdates.num2date(
                    mdates.drange(
                        datetime.datetime(
                            int(
                                day.year), int(
                                day.month), int(
                                day.day)), datetime.datetime(
                            int(
                                day_after.year), int(
                                    day_after.month), int(
                                        day_after.day)), datetime.timedelta(
                                            minutes=30)))

                dataallyear_mnh = [i.replace(tzinfo=None) for i in dt_mnh]
                dataframe_sanstrou_mnh = pd.DataFrame(index=dataallyear_mnh)

                if today_str not in biais[param][model]:
                    biais[param][model][today_str] = {}
                
                # Pas de calcul du biais (obs-obs)
                if model != 'Tf':
                    if values_obs is not None:
                        try:
                            values_mnh = data_mnh[today_str][model][param]
                            time_mnh = data_mnh[today_str]['time']

                            if len(values_mnh) != 0:

                                # Création de dataframes des valeurs obs et modèles
                                df_obs = pd.DataFrame(list(values_obs), index=(time_obs))
                                df_mnh = pd.DataFrame(list(values_mnh[0:96]), index=(time_mnh))

                                # concordance des dates sur le dataframe défini au début
                                df_obs = dataframe_sanstrou_mnh.join(df_obs)
                                df_mnh = dataframe_sanstrou_mnh.join(df_mnh)

                                # Calcul du biais
                                df_biais_mnh = df_mnh - df_obs

                                #df_biais = dataframe_sanstrou.join(df_biais)
                                df_biais_mnh = df_biais_mnh.fillna(0)
                                df_biais_mnh.index = pd.to_datetime(df_biais_mnh.index)

                                biais[param][model][today_str]['values'] = list(df_biais_mnh[0])
                                biais[param][model][today_str]['time'] = list(df_biais_mnh.index)

                        except KeyError:
                            pass
                             
        #for id_user in enumerate([id_user1, id_user2, id_user3, id_user4, id_user5]):
        #data_user = lecture_mesoNH.mesoNH_user(start_day,end_day,id_user,VARIABLES_PLOT)  
        #print("MODEL ID_USER :", id_user)                
        #on utilise le 'id_user' en tant que nom du 'model' pour le dictionnaire                  

        chartB[param] = go.Figure()
        # Tracé des figures

        graphB[param] = dcc.Graph(
            id='graphB_' + param,
            figure=chartB[param],
        )
        # Tranformation en HTML

        # Ces 2 dernières étapes sont essentielles : d'abord on effectue le tracé,
        # puis on le transforme en objet html pour pouvoir l'afficher

    return biais, chartB, graphB


biais, chartB, graphB = calcul_biais(start_day, end_day)

#   4.2 CALLBACKS
# -----------------------------------------------------------------------------
# Contient fonctions qui vont actualiser les Outputs à chaque fois qu'un Input est modifié

output_graphsB = []

for param in VARIABLES_PLOT:
    # Définition des Outputs c-à-d des graphs qui seront mis à jour
    output_graphsB.append(Output('graphB_' + param, 'figure'))

# BIAIS MNH
# for param in VARIABLES_PLOT:
#    output_graphsB.append(Output('graphB_mnh_' + param, 'figure'))

# Chaque Input prend en argument l'id d'une dcc.Input et la valeur qu'elle récupère
@app.callback(output_graphsB,
              #               [Input('multi_select_line_chartB_obs', 'value'),
              [Input('multi_select_line_chart_ARP', 'value'),
               Input('multi_select_line_chart_ARO', 'value'),
               Input('multi_select_line_chart_MNH', 'value'),
               Input('multi_select_line_chart_SURFEX', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),
               Input('id_user1', 'value'), Input('id_user2', 'value'),
               Input('id_user3', 'value'), Input('id_user4', 'value'), Input('id_user5', 'value')
               ])

def update_lineB(reseau2, reseau3, reseau4, reseau5, start_day, end_day,
                 id_user1, id_user2, id_user3, id_user4, id_user5):
    # On donne ici le nom que l'on veut aux arguments, seul l'ordre (et le
    # nombre) est important et correspond à l'ordre (et au nombre) d'Inputs du
    # callback.

    if start_day is not None:
        start_day = date.fromisoformat(start_day)
    if end_day is not None:
        end_day = date.fromisoformat(end_day)
    # transformation des dates de type str que l'on récupère du "calendrier" en datetime.date

    # UPDATE DES DATES APRES LE CALLBACK
    data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS, VARIABLES_PLOT)
    data_surfex = lecture_surfex.surfex(start_day, end_day, MODELS, VARIABLES_PLOT)
    #data_user = lecture_mesoNH.mesoNH_user(start_day,end_day,id_user,VARIABLES_PLOT) 
    
    # CALCUL DES BIAIS correspondants à la période choisie
    biais, chartB, graphB = calcul_biais(start_day, end_day)

    # Puis, mise à jour des graphes :
    for param in VARIABLES_PLOT:
        chartB[param] = go.Figure()

    # Pour les 5 rejeux possibles de MésoNH, correspondants aux différents id_user :
    # différentes valeurs pour l'attribut "dash" du paramètre "line" qui
    # donnent le type de tracé (trait plein/pointillés/tirets/longs
    # tirets/alternance tirets-points)
    types = ['solid', 'dot', 'dash', 'longdash', 'dashdot']
    for j, id_user in enumerate([id_user1, id_user2, id_user3, id_user4, id_user5]):
        #data_user = lecture_mesoNH.mesoNH_user(start_day, end_day, id_user, VARIABLES_PLOT)
        nb_jour = (end_day - start_day).days
        
        #Calcul du biais USER doit se faire ici normalement (après avoir défini le "id_user")
        #biais, chartB, graphB = calcul_biais(start_day, end_day)

        for i in range(nb_jour):
            date_run = start_day + datetime.timedelta(days=i)
            today_str = date_run.strftime('%Y%m%d')
            for param in VARIABLES_PLOT:
                #print(biais[param][id_user][today_str])
                # Ici try/except permet de rien afficher lorsque les données ne sont pas disponibles
                try:
                    if isinstance(biais[param][id_user][today_str],
                                  (list, np.ndarray)):  # On vérifie qu'il y a des données

                        chartB[param].add_trace(
                            go.Scatter(
                                x=biais[param][id_user][today_str]['time'],
                                y=biais[param][id_user][today_str]['values'],
                                line=dict(
                                    color='black',
                                    dash=types[j]),
                                name='MésoNH modifié (id : ' + str(id_user) + ' )'))
                except KeyError:
                    pass

    # BIAIS -> le calcul sur les obs permet d'avoir le zéro en affichage (obs - obs = 0)
    # Ici plus besoin de try/except, c'est AIDA qui s'en charge
    #    for selection in reseau1:
    #        if selection == "Obs" :
    #            for param in VARIABLES_PLOT:
    #                if isinstance(biais[param]['Tf']['values'],(list,np.ndarray)):
    #                    chartB[param].add_trace(go.Scatter(x=biais[param]['Tf']['time'], y=biais[param]['Tf']['values'],marker={"color":"red"},mode="lines",name=selection))

    # Pour les différents réseaux d'Arpège :
    for selection in reseau2:
        if selection == "Arp_J-1_00h":
            reseau = RESEAUX[0]
            line_param = dict(color='navy', dash='dot')
        if selection == "Arp_J-1_12h":
            reseau = RESEAUX[1]
            line_param = dict(color='mediumslateblue', dash='dot')
        if selection == "Arp_J0_00h":
            reseau = RESEAUX[2]
            line_param = dict(color='navy')
        if selection == "Arp_J0_12h":
            reseau = RESEAUX[3]
            line_param = dict(color='mediumslateblue')

        for param in VARIABLES_PLOT:
            if isinstance(biais[param]['Gt'][reseau]['values'], (list, np.ndarray)):
                chartB[param].add_trace(
                    go.Scatter(
                        x=biais[param]['Gt'][reseau]['time'],
                        y=biais[param]['Gt'][reseau]['values'],
                        line=line_param,
                        name=selection))

    # Pour les différents réseaux d'Arome :
    for selection in reseau3:
        if selection == "Aro_J-1_00h":
            reseau = RESEAUX[0]
            line_param = dict(color='green', dash='dot')
        if selection == "Aro_J-1_12h":
            reseau = RESEAUX[1]
            line_param = dict(color='olive', dash='dot')
        if selection == "Aro_J0_00h":
            reseau = RESEAUX[2]
            line_param = dict(color='green')
        if selection == "Aro_J0_12h":
            reseau = RESEAUX[3]
            line_param = dict(color='olive')

        for param in VARIABLES_PLOT:
            if isinstance(biais[param]['Rt'][reseau]['values'], (list, np.ndarray)):
                chartB[param].add_trace(
                    go.Scatter(
                        x=biais[param]['Rt'][reseau]['time'],
                        y=biais[param]['Rt'][reseau]['values'],
                        line=line_param,
                        name=selection))

#!!!!!! A COMPLETER POUR MESO-NH ET SURFEX !!!!!!!!!!!!

    # Pour les courbes de MésoNH :
    # A la différence des 3 réseaux précédents où l'on récupère les données sur la période choisie à chaque nouvelle période grâce à AIDA, MésoNH et SURFEX sont stockés par dossier nommé à la date de run.
    # Il faut donc parcourir tous les jours entre le start_day et le end_day et stocker les informations lues.
    courbe_affichee = []
    for selection in reseau4:
        nb_jour = (end_day - start_day).days
        for i in range(nb_jour + 1):
            day = start_day + timedelta(days=i)
            today_str = day.strftime('%Y%m%d')

            # Gestion du nombre de légende affichée : La légende est affichée si elle absente avant cad si courbe_affichee est vide (courbe affichee est remplie au 1er jour affiche)
            # if selection not in courbe_affichee and MODELS_PLOT[selection]['name'] in
            # biais['tmp_2m'] and
            # isinstance(biais['tmp_2m'][MODELS_PLOT[selection]['name']][today_str],(list,np.ndarray)):
            if selection not in courbe_affichee and MODELS_PLOT[selection]['name'] in biais['tmp_2m']:
                courbe_affichee.append(selection)
                afficher_legende = True
            else:
                afficher_legende = False

                # Ce montage un peu douteux de if/else permet de n'afficher qu'une seule fois la légende de la courbe MésoNH choisie. Sans ça, le programme affichait autant de fois la légende
                # qu'il y avait de jours entre le start_day et le end_day.

            for param in VARIABLES_PLOT:
                # Le retour du try/except pour éviter que le script ne se bloque.
                try:
                    if isinstance(biais[param][MODELS_PLOT[selection]['name']]
                                  [str(today_str)]['values'], (list, np.ndarray)):

                        chartB[param].add_trace(go.Scatter(x=biais[param][MODELS_PLOT[selection]['name']][str(today_str)]['time'], y=biais[param][MODELS_PLOT[selection]['name']][str(
                            today_str)]['values'], marker={"color": MODELS_PLOT[selection]['color']}, mode="lines", name=selection, showlegend=afficher_legende))
                   
                    #Partie user "manuelle" en attendant de pouvoir la coder automatiquement  
                    """       
                    for id_user in ["RM17", "LIMA"]:
                    
                        if isinstance(biais[param][id_user]
                                      [str(today_str)]['values'], (list, np.ndarray)):
                                      
                           chartB[param].add_trace(go.Scatter(x=biais[param][id_user][str(today_str)]['time'], y=biais[param][id_user][str(
                            today_str)]['values'], marker={"color": "black"}, mode="lines", name=id_user, showlegend=True))
                    """
                except KeyError:
                    pass

    # Pour les courbes de Surfex :
    courbe_affichee_surfex = []
    for selection in reseau5:
        nb_jour = (end_day - start_day).days
        for i in range(nb_jour + 1):
            day = start_day + timedelta(days=i)
            today_str = day.strftime('%Y%m%d')

            if selection not in courbe_affichee_surfex and MODELS_PLOT[selection]['name'] in data_surfex[today_str] and isinstance(
                    data_surfex[today_str][MODELS_PLOT[selection]['name']]['tmp_2m'], (list, np.ndarray)):
                courbe_affichee_surfex.append(selection)
                afficher_legende_surfex = True
            else:
                afficher_legende_surfex = False
            for param in VARIABLES_PLOT:
                # Ici try/except permet de rien afficher lorsque les données ne sont pas disponibles
                try:
                    if isinstance(data_surfex[today_str][MODELS_PLOT[selection]
                                  ['name']][param], (list, np.ndarray)):
                        chartB[param].add_trace(go.Scatter(x=data_surfex[today_str]['time'],
                                                           y=data_surfex[today_str][MODELS_PLOT[selection]
                                                                                    ['name']][param],
                                                           line=dict(color=MODELS_PLOT[selection]['color'],
                                                                     dash='dashdot'),
                                                           name=selection,
                                                           showlegend=afficher_legende_surfex))
                except KeyError:
                    pass
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Mise à jour des graphiques après tous les changements
    list_chartsB = []
    for param in VARIABLES_PLOT:
        chartB[param].update_layout(height=450, width=800,
                                    xaxis_title="Date et heure",
                                    yaxis_title=str(VARIABLES[param]['unit']),
                                    title=VARIABLES[param]['title'])
        list_chartsB.append(chartB[param])

    return list_chartsB  # Le callback attend des Outputs qui sont contenus dans chartB[param]

# 4.3   LAYOUT
# -----------------------------------------------------------------------------
#!!!!!!!!!!!!!!! Tracé des graphes sur la page correspondantes: à modifier avec les graphes affichant les biais (calculés plus haut)
all_graphsB = []

for param in VARIABLES_PLOT:
    all_graphsB.append(
        html.Div(
            graphB[param],
            className="six columns",
            style={
                'display': 'inline-block'}))

row2 = html.Div(children=all_graphsB, className="twelve columns")

# Puisqu'on n'a pas la main sur la css (pour l'instant)(cf external_stylesheets au début du code), on joue sur les html.Div.
# Ici par exemple, chaque graph est d'abord mis dans une Div dont on réduit la taille ("className="five columns"),
# puis on met toutes ces Div dans une seule qui elle prend toute la page
# ("className="twelve columns")
biais_layout = html.Div([
    html.H1('Biais'),
    row2,
], className="twelve columns", style={"text-align": "center", "justifyContent": "center"})


# -----------------------------------------------------------------------------
#   5. BIAIS MOYEN OBS/MODELE : Cycle diurne moyen
# -----------------------------------------------------------------------------

#   5.1. DONNEES : Calcul des biais horaires moyens sur la journée
# -----------------------------------------------------------------------------
#biais, chartB, graphB = calcul_biais(start_day, end_day)
#print(biais['tmp_2m']['Rt']['J0:00_%3600'])

def biais_moyen(start_day, end_day):
   
    biais, chartB, graphB = calcul_biais(start_day, end_day)
    # Initialisation du DataFrame final vide
    DF = []
    # Axe des temps: on prend la résolution des obs
    try:
        DF = pd.DataFrame(DF, index=list(data['tmp_2m']['Tf']['time']))
    except TypeError:
        pass

    for param in VARIABLES_PLOT:
        for model in MODELS_BIAIS:
            if model != 'Tf':
                # Ajout des données ARO/ARP OPER
                for reseau in RESEAUX:
                    if len(biais[param][model][reseau]) > 1 :
                       dico_loc = {}
                       df_loc = []
                       # Nom des colonnes du DF
                       colname = str(param + '_' + model + '_' + reseau)
                       
                       try:
                           # Concaténation des biais moyens par paramètres/modèles/réseau (ARO/ARP)
                           dico_loc = {colname: list(biais[param][model][reseau]['values'])}
                           df_loc = pd.DataFrame(data=dico_loc, index=list(biais[param][model][reseau]['time']))
                           DF = pd.concat([DF, df_loc], axis=1)
                       except BaseException:
                           pass

            # Ajout des données MNH-OPER
            nb_jour = (end_day - start_day).days

            #Création d'un dataframe vide où vont se concaténer tous les jours de la période
            df_mnh = []
            df_mnh = pd.DataFrame(df_mnh)

            for i in range(nb_jour):
                day = start_day + timedelta(days=i)
                today_str = day.strftime('%Y%m%d')
                if model != 'Tf' and len(biais[param][model][str(today_str)]) > 1 :
                   df_loc = []
                   colname = str(param + '_MesoNH_' + model)
                   #Création d'un dataframe vide pour les jours où les simulations MNH-OPER ne sont pas disponibles
                   dummyarray = np.full(len(biais[param][model][str(today_str)]['time']), np.nan)
                   df_nan = pd.DataFrame(data={colname:list(dummyarray)}, index=list(biais[param][model][str(today_str)]['time']))

                   try:
                       #Lecture des biais quotidiens + mis sous la forme d'un dataframe
                       data_loc = {colname: list(biais[param][model][str(today_str)]['values'])}
                       df_loc = pd.DataFrame(data=data_loc, index=list(biais[param][model][str(today_str)]['time']))
                       #Concaténation progressive par jour
                       df_mnh = pd.concat([df_mnh, df_loc], axis=0)
                   except BaseException:
                       df_mnh = pd.concat([df_mnh, df_nan], axis=0)
                       pass

            # Concatenation des biais moyen mesonh au DF avec les autres modèles
            try:
                DF = pd.concat([DF, df_mnh], axis=1)
            except TypeError:
                pass

   # Conversion colonnes type 'object' en type 'numeric'
   # Sinon le 'groupby' enlève les colonnes 'object'
    try:
        cols = DF.columns[DF.dtypes.eq('object')]
        DF[cols] = DF[cols].astype('float')
    except AttributeError:
        pass

    # Dataframe regroupé par heures
    try: #If missing data at first call 
       DF_CyDi = DF.groupby(DF.index.hour).mean()
    except:
        try:
           DF_CyDi = pd.DataFrame(DF, index=DF.index)
        except:
            DF_CyDi = pd.DataFrame()

    # Création du dictionnaire associé aux biais moyens + graphes html
    chartM = {}
    graphM = {}
    biais_moy = {}

    # Intégration des données du DataFrame DF_CyDi dans le dictionnaire biais_moy
    for param in VARIABLES_PLOT:
        if param not in biais_moy:
            biais_moy[param] = {}
        for model in MODELS_BIAIS:
            if model not in biais_moy[param]:
                biais_moy[param][model] = {}
            if model != 'Tf':
                # Ajout des données ARO/ARP OPER
                for reseau in RESEAUX:
                    if reseau not in biais_moy[param][model]:
                        biais_moy[param][model][reseau] = {}
                    colname = str(param + '_' + model + '_' + reseau)

                    try:
                        biais_moy[param][model][reseau]['values'] = list(DF_CyDi[colname])
                        biais_moy[param][model][reseau]['time'] = list(DF_CyDi.index)
                    except BaseException:
                        biais_moy[param][model][reseau]['values'] = 0.
                        biais_moy[param][model][reseau]['time'] = list(DF_CyDi.index)
                        pass

            if 'MNH' not in biais_moy[param][model]:
                biais_moy[param][model]['MNH'] = {}
            colname = str(param + '_MesoNH_' + model)

            try:
                biais_moy[param][model]['MNH']['values'] = list(DF_CyDi[colname])
                biais_moy[param][model]['MNH']['time'] = list(DF_CyDi.index)
            except BaseException:
                biais_moy[param][model]['MNH']['values'] = 0.
                biais_moy[param][model]['MNH']['time'] = list(DF_CyDi.index)
                pass

        # Ces 2 dernières étapes sont essentielles : d'abord on effectue le tracé,
        # puis on le transforme en objet html pour pouvoir l'afficher
        chartM[param] = go.Figure()  # tracé
        graphM[param] = dcc.Graph(id='graphM_' + param,figure=chartM[param])    # objet html

    return biais_moy, chartM, graphM

biais_moy, chartM, graphM = biais_moyen(start_day, end_day)

# 5.2   CALLBACKS
# -----------------------------------------------------------------------------
# Contient fonctions qui vont actualiser les Outputs à chaque fois qu'un Input est modifié

output_graphsM = []

for param in VARIABLES_PLOT:
    # Définition des Outputs c-à-d des graphs qui seront mis à jour
    output_graphsM.append(Output('graphM_' + param, 'figure'))

# BIAIS MNH
# for param in VARIABLES_PLOT:
#    output_graphsB.append(Output('graphB_mnh_' + param, 'figure'))

# Chaque Input prend en argument l'id d'une dcc.Input et la valeur qu'elle récupère
@app.callback(output_graphsM,
              #               [Input('multi_select_line_chartB_obs', 'value'),
              [Input('multi_select_line_chart_ARP', 'value'),
               Input('multi_select_line_chart_ARO', 'value'),
               Input('multi_select_line_chart_MNH', 'value'),
               Input('multi_select_line_chart_SURFEX', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),
               Input('id_user1', 'value'), Input('id_user2', 'value'), 
               Input('id_user3', 'value'), Input('id_user4', 'value'), Input('id_user5', 'value')
               ])

def update_lineM(reseau2, reseau3, reseau4, reseau5, start_day, end_day,
                 id_user1, id_user2, id_user3, id_user4, id_user5):
    # On donne ici le nom que l'on veut aux arguments, seul l'ordre (et le
    # nombre) est important et correspond à l'ordre (et au nombre) d'Inputs du
    # callback.

    # transformation des dates de type str que l'on récupère du "calendrier" en datetime.date
    if start_day is not None:
        start_day = date.fromisoformat(start_day)
    if end_day is not None:
        end_day = date.fromisoformat(end_day)

    # UPDATE DES DATES APRES LE CALLBACK
    data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS, VARIABLES_PLOT)
    data_surfex = lecture_surfex.surfex(start_day, end_day, MODELS, VARIABLES_PLOT)

    # CALCUL DES BIAIS moyens sur la période choisie - Cycle Diurne:
    biais_moy, chartM, graphM = biais_moyen(start_day, end_day)

    # Puis, mise à jour des graphes :
    for param in VARIABLES_PLOT:
        chartM[param] = go.Figure()

    # Pour les 5 rejeux possibles de MésoNH, correspondants aux différents id_user :
    # différentes valeurs pour l'attribut "dash" du paramètre "line" qui
    # donnent le type de tracé (trait plein/pointillés/tirets/longs
    # tirets/alternance tirets-points)
    types = ['solid', 'dot', 'dash', 'longdash', 'dashdot']
    for j, id_user in enumerate([id_user1, id_user2, id_user3, id_user4, id_user5]):
        data_user = lecture_mesoNH.mesoNH_user(start_day, end_day, id_user, VARIABLES_PLOT)
        nb_jour = (end_day - start_day).days
        for i in range(nb_jour + 1):
            date_run = start_day + datetime.timedelta(days=i)
            today_str = date_run.strftime('%Y%m%d')
            for param in VARIABLES_PLOT:
                # Ici try/except permet de rien afficher lorsque les données ne sont pas disponibles
                try:
                    if isinstance(data_user[today_str][param],
                                  (list, np.ndarray)):  # On vérifie qu'il y a des données

                        chartM[param].add_trace(
                            go.Scatter(
                                x=data_user[today_str]['time'],
                                y=data_user[today_str][param],
                                line=dict(
                                    color='black',
                                    dash=types[j]),
                                name='MésoNH modifié (id : ' + str(id_user) + ' )'))

                except KeyError:
                    pass

    # BIAIS -> le calcul sur les obs permet d'avoir le zéro en affichage (obs - obs = 0)
    #    for selection in reseau1:
    #        if selection == "Obs" :
    #            for param in VARIABLES_PLOT:
    #                if isinstance(biais[param]['Tf']['values'],(list,np.ndarray)):
    #                    chartB[param].add_trace(go.Scatter(x=biais[param]['Tf']['time'], y=biais[param]['Tf']['values'],marker={"color":"red"},mode="lines",name=selection))
    # Ici plus besoin de try/except, c'est AIDA qui s'en charge

    # Pour les différents réseaux d'Arpège :
    for selection in reseau2:
        if selection == "Arp_J-1_00h":
            reseau = RESEAUX[0]
            line_param = dict(color='navy', dash='dot')
        if selection == "Arp_J-1_12h":
            reseau = RESEAUX[1]
            line_param = dict(color='mediumslateblue', dash='dot')
        if selection == "Arp_J0_00h":
            reseau = RESEAUX[2]
            line_param = dict(color='navy')
        if selection == "Arp_J0_12h":
            reseau = RESEAUX[3]
            line_param = dict(color='mediumslateblue')

        for param in VARIABLES_PLOT:
            if isinstance(biais_moy[param]['Gt'][reseau]['values'], (list, np.ndarray)):
                chartM[param].add_trace(
                    go.Scatter(
                        x=biais_moy[param]['Gt'][reseau]['time'],
                        y=biais_moy[param]['Gt'][reseau]['values'],
                        line=line_param,
                        name=selection))

    # Pour les différents réseaux d'Arome :
    for selection in reseau3:
        if selection == "Aro_J-1_00h":
            reseau = RESEAUX[0]
            line_param = dict(color='green', dash='dot')
        if selection == "Aro_J-1_12h":
            reseau = RESEAUX[1]
            line_param = dict(color='olive', dash='dot')
        if selection == "Aro_J0_00h":
            reseau = RESEAUX[2]
            line_param = dict(color='green')
        if selection == "Aro_J0_12h":
            reseau = RESEAUX[3]
            line_param = dict(color='olive')

        for param in VARIABLES_PLOT:
            if isinstance(biais_moy[param]['Rt'][reseau]['values'], (list, np.ndarray)):
                chartM[param].add_trace(
                    go.Scatter(
                        x=biais_moy[param]['Rt'][reseau]['time'],
                        y=biais_moy[param]['Rt'][reseau]['values'],
                        line=line_param,
                        name=selection))


#!!!!!! A COMPLETER POUR MESO-NH ET SURFEX !!!!!!!!!!!!

    # Pour les courbes de MésoNH :
    # A la différence des 3 réseaux précédents où l'on récupère les données sur la période choisie à chaque nouvelle période grâce à AIDA, MésoNH et SURFEX sont stockés par dossier nommé à la date de run.
    # Il faut donc parcourir tous les jours entre le start_day et le end_day et stocker les informations lues.
    courbe_affichee = []
    for selection in reseau4:
        nb_jour = (end_day - start_day).days
        for i in range(nb_jour):
            day = start_day + timedelta(days=i)
            today_str = day.strftime('%Y%m%d')

            # Gestion du nombre de légende affichée : La légende est affichée si elle absente avant cad si courbe_affichee est vide (courbe affichee est remplie au 1er jour affiche)
            # if selection not in courbe_affichee and MODELS_PLOT[selection]['name'] in
            # biais['tmp_2m'] and
            # isinstance(biais['tmp_2m'][MODELS_PLOT[selection]['name']][today_str],(list,np.ndarray)):
            if selection not in courbe_affichee and MODELS_PLOT[selection]['name'] in biais['tmp_2m']:
                courbe_affichee.append(selection)
                afficher_legende = True
            else:
                afficher_legende = False

                # Ce montage un peu douteux de if/else permet de n'afficher qu'une seule fois la légende de la courbe MésoNH choisie. Sans ça, le programme affichait autant de fois la légende
                # qu'il y avait de jours entre le start_day et le end_day.

            for param in VARIABLES_PLOT:
                # Le retour du try/except pour éviter que le script ne se bloque.
                try:
                    if isinstance(biais_moy[param][MODELS_PLOT[selection]['name']]
                                  ['MNH']['values'], (list, np.ndarray)):

                        chartM[param].add_trace(go.Scatter(x=biais_moy[param][MODELS_PLOT[selection]['name']]['MNH']['time'],
                                                           y=biais_moy[param][MODELS_PLOT[selection]
                                                                              ['name']]['MNH']['values'],
                                                           marker={
                            "color": MODELS_PLOT[selection]['color']},
                            mode="lines",
                            name=selection,
                            showlegend=afficher_legende))
                except KeyError:
                    pass

    # Pour les courbes de Surfex :
    courbe_affichee_surfex = []
    for selection in reseau5:
        nb_jour = (end_day - start_day).days
        for i in range(nb_jour + 1):
            day = start_day + timedelta(days=i)
            today_str = day.strftime('%Y%m%d')

            if selection not in courbe_affichee_surfex and MODELS_PLOT[selection]['name'] in data_surfex[today_str] and isinstance(
                    data_surfex[today_str][MODELS_PLOT[selection]['name']]['tmp_2m'], (list, np.ndarray)):
                courbe_affichee_surfex.append(selection)
                afficher_legende_surfex = True
            else:
                afficher_legende_surfex = False
            for param in VARIABLES_PLOT:
                try:
                    if isinstance(data_surfex[today_str][MODELS_PLOT[selection]
                                  ['name']][param], (list, np.ndarray)):
                        chartM[param].add_trace(go.Scatter(x=data_surfex[today_str]['time'],
                                                           y=data_surfex[today_str][MODELS_PLOT[selection]
                                                                                    ['name']][param],
                                                           line=dict(color=MODELS_PLOT[selection]['color'],
                                                                     dash='dashdot'),
                                                           name=selection,
                                                           showlegend=afficher_legende_surfex))
                except KeyError:
                    pass

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Mise à jour des graphiques après tous les changements
    list_chartsM = []
    for param in VARIABLES_PLOT:
        chartM[param].update_layout(height=450, width=800,
                                    xaxis_title="Heure de la journée",
                                    yaxis_title=str(VARIABLES[param]['unit']),
                                    title=VARIABLES[param]['title'])
        list_chartsM.append(chartM[param])

    return list_chartsM  # Le callback attend des Outputs qui sont contenus dans chartB[param]

# 5.3   LAYOUT
# ----------------------------------------------------------------------------
#!!!!!!!!!!!!!!! Tracé des graphes sur la page correspondantes: à modifier avec les graphes affichant les biais (calculés plus haut)
all_graphsM = []

for param in VARIABLES_PLOT:
    all_graphsM.append(
        html.Div(
            graphM[param],
            className="six columns",
            style={
                'display': 'inline-block'}))

row3 = html.Div(children=all_graphsM, className="twelve columns")

# Puisqu'on n'a pas la main sur la css (pour l'instant)(cf external_stylesheets au début du code), on joue sur les html.Div.
# Ici par exemple, chaque graph est d'abord mis dans une Div dont on réduit la taille ("className="five columns"),
# puis on met toutes ces Div dans une seule qui elle prend toute la page
# ("className="twelve columns")
biaisM_layout = html.Div([
    html.H1('Biais moyens'),
    row3,
], className="twelve columns", style={"text-align": "center", "justifyContent": "center"})

# -----------------------------------------------------------------------------
#   7. REJEU MESO-NH
# -----------------------------------------------------------------------------

from GUI_MESONH import rejeu_gui

# Instanciation de la GUI
mesonhgui = rejeu_gui.get_mesonh_gui()

# Recuperation du Layout
layout_mesonh_gui = mesonhgui.layout_mesonh_gui

# Introduction du layout dans le layout principal
mesoNH_layout = html.Div([layout_mesonh_gui])

# Mise en place des callbacks associees a la GUI
mesonhgui.start_callbacks(app)


# -----------------------------------------------------------------------------
#   10. GESTION DES PAGES
# -----------------------------------------------------------------------------

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/MeteopoleX/':
        return obs_modeles_layout
    elif pathname == '/MeteopoleX/biais':
        return biais_layout
    elif pathname == '/MeteopoleX/biaisM':
        return biaisM_layout
    elif pathname == '/MeteopoleX/mesoNH':
        return mesoNH_layout
    elif pathname == '/MeteopoleX/surfex':
        return layout_surfex
    elif pathname == '/MeteopoleX/rs':
        return layout_radiosoundings
    elif pathname == '/MeteopoleX/notice':
        return layout_notice
    elif pathname=='/MeteopoleX/PV':
        return layout_pv
    else:
        return "Error 404 URL not found"
    


if __name__ == '__main__':
#    app.run_server(debug=True, host="0.0.0.0", port=8010)
    app.run_server(debug=True, port=8087)

# print(data)
