from app import app

from dash import dcc
import plotly.graph_objects as go

from config.variables import VARIABLES_PLOT
from config.models import MODELS_BIAIS, RESEAUX

import numpy as np
import pandas as pd

from datetime import  timedelta

from data.biais import calcul_biais
from data.selection_data_brut_serieT import selection_data_brut_serieT

#   Calcul des biais horaires moyens sur la journée
# -----------------------------------------------------------------------------

def biais_moyen(start_day, end_day):
    data, chart, graph = selection_data_brut_serieT(start_day, end_day)
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