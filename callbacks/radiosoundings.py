from app import app
from datetime import date, timedelta
import datetime

from dash import Input, Output
import plotly.graph_objects as go

from data.selection_data_pv import selection_donnees_PV
from config.variables import VARIABLES_RS_PLOT, VARIABLES_RS, VARIABLES
from config.models import MODELS, LEGENDE_HEURES_PROFILS, LEGENDE_HEURES_PROFILS_AROARP, MODELS_PLOT_RS

from data.radio_sondage import radio_sondage


# 6.3   CALLBACKS (voir 2.3)
# -----------------------------------------------------------------------------
# Contient fonctions qui vont actualiser les Outputs à chaque fois qu'un Input est modifié

output_rs = []
for param in VARIABLES_RS_PLOT:
    output_rs.append(Output('graph_' + param, 'figure'))  # Graphs qui seront mis à jour

@app.callback(output_rs, [Input('wich_heure', 'value'),
                          Input('my-date-picker-single', 'date'),
                          Input('multi_select_line_chart_model', 'value')])

def update_rs(wich_heure, date_value, model_choisi):

    if date_value is not None:
        date_object = date.fromisoformat(date_value)

    # Puis, mise à jour des graphes :
    chart = {}
    for param in VARIABLES_RS_PLOT:
        chart[param] = go.Figure()

    # Extraction des données
    data_rs = radio_sondage(date_object, MODELS, VARIABLES_RS_PLOT, LEGENDE_HEURES_PROFILS, LEGENDE_HEURES_PROFILS_AROARP)
    #aroarp_rs = pv_aroarp(date_object,MODELS,VARIABLES_RS_PLOT,LEGENDE_HEURES_PROFILS)

    # Mise à jour des courbes
    courbe_affichee = []
    for selection in wich_heure:
        if selection not in courbe_affichee:
            courbe_affichee.append(selection)
            afficher_legende = True
        else:
            afficher_legende = False
        for param in VARIABLES_RS_PLOT:
            for model in model_choisi:

                if model == 'Ab' and len(data_rs[model][selection][param]) > 1:
                    try:

                        chart[param].add_trace(
                            go.Scatter(
                                x=data_rs[model][selection][param],
                                y=data_rs[model][selection]['level'],
                                line=dict(
                                    color=LEGENDE_HEURES_PROFILS[selection]["color"],
                                    width=8,
                                    dash=MODELS_PLOT_RS[model]["line"]),
                                mode="markers",
                                name=MODELS_PLOT_RS[model]["name"] +
                                ' - ' +
                                LEGENDE_HEURES_PROFILS[selection]["value"],
                                showlegend=afficher_legende))
                    except KeyError:
                        pass

                else:

                    try:
                        chart[param].add_trace(
                            go.Scatter(
                                x=data_rs[model][selection][param],
                                y=data_rs[model]['level'],
                                line=dict(
                                    color=LEGENDE_HEURES_PROFILS[selection]["color"],
                                    width=4,
                                    dash=MODELS_PLOT_RS[model]["line"]),
                                mode="lines",
                                name=MODELS_PLOT_RS[model]["name"] +
                                ' - ' +
                                LEGENDE_HEURES_PROFILS[selection]["value"],
                                showlegend=afficher_legende))
                    except KeyError:
                        pass
    list_charts = []
    for param in VARIABLES_RS_PLOT:
        chart[param].update_layout(height=1000, width=500,
                                   xaxis_title=VARIABLES_RS[param]["label"] +
                                   " (" + VARIABLES_RS[param]["unit"] + ")",
                                   yaxis_title="Altitude (m agl)",
                                   title=param)
        list_charts.append(chart[param])

    return list_charts
