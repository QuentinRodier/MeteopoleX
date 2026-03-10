'''from app import app
import datetime

from dash import dcc
import plotly.graph_objects as go

from . import read_aida
from . import read_arome

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import MODELS, RESEAUX

# -----------------------------------------------------------------------------
#   3. SERIES TEMPORELLES : Comparaison Obs/Modèles
# -----------------------------------------------------------------------------

def selection_data_brut_serieT(start_day, end_day):
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

    return data, charts, graphs'''


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
import datetime
from dash import dcc
import plotly.graph_objects as go

from . import read_aida 
from . import read_arome
from . import read_surfex
from . import read_operationnel

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import MODELS, RESEAUX


def selection_data_brut_serieT(start_day, end_day):
    """
    Récupération des données
    """
    
    # Conversion des dates en jour de l'année
    start_doy = datetime.datetime(
        start_day.year, start_day.month, start_day.day
    ).strftime('%j')

    end_doy = datetime.datetime(
        end_day.year, end_day.month, end_day.day
    ).strftime('%j')

    data = {}

    #----------------------------------------------------------------------------------
    # Listes des paramètres à charger
    # Paramètres observations
    params_obs = {
        param: VARIABLES[param]["index_obs"] 
        for param in VARIABLES_PLOT
    }
    
    '''# Paramètres modèles (Arpège, Arome ancien)
    params_models = {}
    for model in ['Gt', 'Rt']:  # Arpège et Arome AIDA
        params_models[model] = {}
        for reseau in RESEAUX:
            params_models[model][reseau] = {
                param: f"{VARIABLES[param]['index_model']}_{reseau}"
                for param in VARIABLES_PLOT
            }'''
    
    # Paramètres AROME enveloppe
    '''params_arome = {
        param: VARIABLES[param]['index_model_arome']
        for param in VARIABLES_PLOT
        if VARIABLES[param]['index_model_arome'] is not None
    }'''

    # Paramètres SURFEX Arpège expérience
    params_surfex = {
       param: VARIABLES[param]['index_model_surfex']
       for param in VARIABLES_PLOT
       if VARIABLES[param].get('index_model_surfex') is not None
    }

    # Paramètres Arpège opérationnel
    params_ope = {
       param: VARIABLES[param]['index_ope']
       for param in VARIABLES_PLOT
       if VARIABLES[param].get('index_ope') is not None
    }

    #----------------------------------------------------------------------------------
    # Lecture batch des observations 
    obs_data_batch = read_aida.donnees_batch(
        start_doy, end_doy,
        str(start_day.year), str(end_day.year),
        params_obs,
        'Tf'
    )
    
    # Lecture batch des modèles AIDA
    '''models_data_batch = {}
    for model in ['Gt', 'Rt']:
        models_data_batch[model] = {}
        for reseau in RESEAUX:
            models_data_batch[model][reseau] = read_aida.donnees_batch(
                start_doy, end_doy,
                str(start_day.year), str(end_day.year),
                params_models[model][reseau],
                model
            )'''
    
    # Lecture batch AROME enveloppe
    '''arome_params_to_load = [v for v in params_arome.values() if v is not None]
    arome_data_batch = {}
    for reseau in RESEAUX:
        # Une seule lecture de tous les fichiers pour tous les paramètres
        arome_data_batch[reseau] = read_arome.donnees_batch(
            start_day, end_day, reseau, arome_params_to_load
        )'''

    # Lecture batch SURFEX Arpège expérience
    surfex_params_to_load = [v for v in params_surfex.values() if v is not None]
    surfex_data_batch = read_surfex.donnees_surfex_batch(
       start_day, end_day, surfex_params_to_load
    )

    # Lecture batch Arpège opérationnel
    ope_params_to_load = [v for v in params_ope.values() if v is not None]
    arpege_data_batch = {}
    arome_data_batch = {}
    for reseau in RESEAUX:
        reseau_hr = reseau[-8:-6]  # '00' ou '12'
        reseau_j = reseau[0:2]     # 'J-' ou 'J0'
        if reseau.startswith('J0'):
            arpege_data_batch[reseau] = read_operationnel.donnees_operationnel_batch(
                start_day, end_day, ope_params_to_load, model='Arpege', reseau=reseau) 
            arome_data_batch[reseau] = read_operationnel.donnees_operationnel_batch(
                start_day, end_day, ope_params_to_load, model='Arome', reseau=reseau)
        elif reseau.startswith('J-1'):
            arpege_data_batch[reseau] = read_operationnel.donnees_operationnel_batch(
                start_day, end_day, ope_params_to_load, model='Arpege', reseau=reseau) 
            arome_data_batch[reseau] = read_operationnel.donnees_operationnel_batch(
                start_day, end_day, ope_params_to_load, model='Arome', reseau=reseau)
    
    #----------------------------------------------------------------------------------
    # Structure données
    for param in VARIABLES_PLOT:
        
        data.setdefault(param, {})
        
        # Observations
        obs_model = 'Tf'
        data[param][obs_model] = {}
        
        if param in obs_data_batch:
            values_obs, time_obs, _ = obs_data_batch[param]
            data[param][obs_model]['values'] = values_obs
            data[param][obs_model]['time'] = time_obs
        else:
            data[param][obs_model]['values'] = None
            data[param][obs_model]['time'] = None
        
        # Modèles numériques
        for model in MODELS:
            
            data[param].setdefault(model, {})
            
            for reseau in RESEAUX:
                
                data[param][model].setdefault(reseau, {})
                
                # AROME enveloppes
                '''if model == "Arome":
                    
                    param_arome = VARIABLES[param]['index_model_arome']
                    
                    if param_arome is not None and param_arome in arome_data_batch[reseau]:
                        
                        # Récupérer les données brutes
                        arome_df = arome_data_batch[reseau][param_arome]
                        
                        if not arome_df.empty:
                            # Calculer toutes les stats en une fois
                            stats = read_arome.compute_statistics(arome_df, param_arome)
                            
                            # Stocker dans la structure
                            data[param][model][reseau].update(stats)
                        else:
                            # Données vides
                            data[param][model][reseau].update({
                                #'values_mean': {},
                                #'values_mean_plus_std': {},
                                #'values_mean_moins_std': {},
                                #'values_max': {},
                                #'values_min': {},
                                'values_P': {},
                                #'values_P2': {},
                                #'values_P3': {},
                                #'values_P4': {},
                                'time': {}
                            })
                    else:
                        # Paramètre non disponible
                        data[param][model][reseau].update({
                            #'values_mean': {},
                            #'values_mean_plus_std': {},
                            #'values_mean_moins_std': {},
                            #'values_max': {},
                            #'values_min': {},
                            'values_P': {},
                            #'values_P2': {},
                            #'values_P3': {},
                            #'values_P4': {},
                            'time': {}
                        })'''
                
                # AROME / ARPEGE (AIDA) 
                '''else:
                    
                    if param in models_data_batch[model][reseau]:
                        values_mod, time_mod, _ = models_data_batch[model][reseau][param]
                        
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
                    else:
                        data[param][model][reseau]['values'] = None
                        data[param][model][reseau]['time'] = None'''

                # SURFEX Arpège expérience
                if model == 'Surfex_arpege':
                    param_surfex = VARIABLES[param].get('index_model_surfex')

                    if param_surfex is not None and param_surfex in surfex_data_batch:

                        surfex_df = surfex_data_batch[param_surfex]

                        if not surfex_df.empty:
                            stats = read_surfex.compute_statistics_surfex(surfex_df, param_surfex)
                            data[param][model][reseau].update(stats)
                        else:
                            data[param][model][reseau].update({
                               'values_P': {},
                               'time': {}
                            })
                    else:
                        data[param][model][reseau].update({
                           'values_P': {},
                           'time': {}
                        })
                
                # ARPEGE operationnel
                if model == 'Arpege':
                    param_oper = VARIABLES[param].get('index_ope')
 
                    if param_oper is not None and param_oper in arpege_data_batch[reseau]:
 
                        arpege_oper_df = arpege_data_batch[reseau][param_oper]
 
                        if not arpege_oper_df.empty:
                            stats = read_operationnel.compute_statistics_operationnel(arpege_oper_df, param_oper)
                            data[param][model][reseau].update(stats)
                        else:
                            data[param][model][reseau].update({'values_P': {}, 'time': {}})
                    else:
                        data[param][model][reseau].update({'values_P': {}, 'time': {}})

                # AROME operationnel
                if model == 'Arome':
                    param_oper = VARIABLES[param].get('index_ope')
 
                    if param_oper is not None and param_oper in arome_data_batch[reseau]:
 
                        arome_oper_df = arome_data_batch[reseau][param_oper]
 
                        if not arome_oper_df.empty:
                            stats = read_operationnel.compute_statistics_operationnel(arome_oper_df, param_oper)
                            data[param][model][reseau].update(stats)
                        else:
                            data[param][model][reseau].update({'values_P': {}, 'time': {}})
                    else:
                        data[param][model][reseau].update({'values_P': {}, 'time': {}})
    
    return data