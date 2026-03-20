#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------------------
##########################################################################################
#-----------------------------------------------------------------------------------------
#app/
#├── app.py                  # Création de l'objet Dash (UNIQUE)
#├── navigation.py           # Routing entre les pages
#│
#├── layouts/                # Définition des layouts Dash (HTML / DCC)
#│   ├── sidebar.py
#│   ├── series_temporelles.py
#│   ├── notice.py
#│   ├── biais.py
#│   └── ...
#│
#├── callbacks/              # Callbacks Dash (logique d'interaction)
#│   ├── series_temporelles.py
#│   ├── notice.py
#│   ├── biais.py
#│   └── ...
#│
#├── data/                   # Accès et préparation des données
#│   ├── selection_donnees.py
#│   ├── lecture_mesoNH.py
#│   ├── lecture_surfex.py
#│   └── ...
#│
#├── config/                 # Configuration globale (pas de logique)
#│   ├── variables.py
#│   └── models.py
#│
#└── assets/                 # CSS, images, fichiers statiques
#
#-----------------------------------------------------------------------------------------
##########################################################################################
#-----------------------------------------------------------------------------------------

from app import app
import dash
from dash import dcc
from dash import html

# Layouts
from layouts.sidebar import layout_sidebar
from layouts.notice import layout_notice
from layouts.paneaux_solaire import layout_pv
from layouts.radiosoundings import layout_radiosoundings
from layouts.serie_temporelle import layout_serie_temporelle
from layouts.biais import layout_biais
from layouts.biais_moyen import layout_biais_moyen

CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    layout_sidebar,
    content
])

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
    elif pathname == '/MeteopoleX/surfex':
        return layout_surfex
    elif pathname=='/MeteopoleX/PV':
        return layout_pv
    elif pathname == '/MeteopoleX/rs':
        return layout_radiosoundings
    elif pathname == '/MeteopoleX/notice':
        return layout_notice
    else:
        return "Error 404 URL not found"
    
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8091)
#    app.run_server(debug=True, port=8087)
