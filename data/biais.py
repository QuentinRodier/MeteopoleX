from app import app

from dash import dcc
import plotly.graph_objects as go

import read_aida
import lecture_mesoNH

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import MODELS, MODELS_BIAIS, RESEAUX

import numpy as np
import pandas as pd

import datetime
from datetime import date, timedelta
import matplotlib.dates as mdates


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

    return biais, chartB, graphB
