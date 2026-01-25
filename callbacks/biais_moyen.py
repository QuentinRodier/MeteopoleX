from app import app
from datetime import date, timedelta
import datetime

from dash import Input, Output
import plotly.graph_objects as go

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import MODELS, RESEAUX, MODELS_PLOT

from data.biais_moyen import biais_moyen
from data.biais import biais

import lecture_mesoNH
import lecture_surfex
import numpy as np

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