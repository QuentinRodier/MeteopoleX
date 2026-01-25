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
from layouts.serie_temporelle import layout_serie_temporelle
from layouts.biais import layout_biais
from layouts.biais_moyen import layout_biais_moyen

# Config static
from config.variables import VARIABLES_PLOT, VARIABLES, VARIABLES_PV_PLOT, VARIABLES_RS_PLOT, VARIABLES_RS
from config.models import MODELS_PLOT, MODELS_PLOT_RS, MODELS, MODELS_BIAIS, MODELS_PV, RESEAUX, LEGENDE_HEURES_PROFILS, LEGENDE_HEURES_PROFILS_AROARP


# Data extraction
import read_aida
import lecture_mesoNH
import lecture_surfex
import read_arome

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
        return layout_serie_temporelle
    elif pathname == '/MeteopoleX/biais':
        return layout_biais
    elif pathname == '/MeteopoleX/biaisM':
        return layout_biais_moyen
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