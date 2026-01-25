from app import app
from datetime import date, timedelta
import datetime

from dash import Input, Output
import plotly.graph_objects as go

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import MODELS, RESEAUX

from data.selection_data_brut_serieT import selection_data_brut_serieT
import lecture_mesoNH
import lecture_surfex
import numpy as np

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
    data, chart, graph = selection_data_brut_serieT(start_day, end_day)

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