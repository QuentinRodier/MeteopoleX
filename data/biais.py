from app import app

from dash import dcc
import plotly.graph_objects as go

#from . import read_aida
#from . import read_arome
#import lecture_mesoNH

from config.variables import VARIABLES_PLOT, VARIABLES
from config.config import MODELS, RESEAUX
from data.data_loader import data_loader

import numpy as np
import pandas as pd

import datetime
from datetime import date, timedelta
import matplotlib.dates as mdates


def calcul_biais(start_day, end_day):

    doy1 = datetime.datetime(int(start_day.year), int(
        start_day.month), int(start_day.day)).strftime('%j')
    doy2 = datetime.datetime(int(end_day.year), int(end_day.month), int(end_day.day)).strftime('%j')

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

    # Chargement des données
    #data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS_BIAIS, VARIABLES_PLOT)
    loader = data_loader.load_series(start_day, end_day)
    base = loader["base"]

    '''for param in VARIABLES_PLOT:
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

    return biais, chartB, graphB'''


    for param in VARIABLES_PLOT:
            biais.setdefault(param, {})

            # --- OBS ---
            obs_pack = base.get(param, {}).get("Tf", {})
            values_obs = obs_pack.get("values", None)
            time_obs = obs_pack.get("time", None)

            if values_obs is None or time_obs is None:
                # pas d'obs => NaN partout
                for model in MODELS:
                    biais[param].setdefault(model, {})
                    for reseau in RESEAUX:
                        biais[param][model][reseau] = {"values": np.nan}
                continue

            df_obs = pd.DataFrame(list(values_obs), index=time_obs)
            df_obs = dataframe_sanstrou.join(df_obs).dropna()
            df_obs.index = pd.to_datetime(df_obs.index)

            # --- MODELES ---
            for model in MODELS:  
                biais[param].setdefault(model, {})

                for reseau in RESEAUX:
                    biais[param][model].setdefault(reseau, {})

                    mod_pack = base.get(param, {}).get(model, {}).get(reseau, {})

                    runs = mod_pack.get("runs", {}) 
                    if not runs: 
                        biais[param][model][reseau]["values"] = np.nan 
                        continue 
                        
                    # Concaténer tous les runs en une seule série 
                    s_p1 = pd.concat(list(runs.values()))
                    s_p1 = s_p1[~s_p1.index.duplicated(keep='last')].sort_index()

                    s_mod = s_p1.copy()
                    s_mod.index = pd.to_datetime(s_mod.index)

                    df_mod = pd.DataFrame(s_mod)
                    df_mod = dataframe_sanstrou.join(df_mod).dropna()
                    df_mod.index = pd.to_datetime(df_mod.index)

                    joined = df_mod.join(df_obs, how="inner", lsuffix="_mod", rsuffix="_obs").dropna()
                    if joined.empty:
                        biais[param][model][reseau]["values"] = np.nan
                        continue

                    b = joined.iloc[:, 0] - joined.iloc[:, 1]  # mod - obs
                    biais[param][model][reseau]["values"] = list(b.values)
                    biais[param][model][reseau]["time"] = list(b.index)

    return biais

