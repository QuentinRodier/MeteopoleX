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
"""
Version optimisée de selection_data_brut_serieT
Utilise les lectures batch pour réduire drastiquement les I/O
"""

from app import app
import datetime
from dash import dcc
import plotly.graph_objects as go

from . import read_aida 
from . import read_arome

from config.variables import VARIABLES_PLOT, VARIABLES
from config.models import MODELS, RESEAUX


def selection_data_brut_serieT(start_day, end_day):
    """
    Version optimisée de la récupération des données AIDA/AROME
    
    OPTIMISATIONS:
    1. Lecture batch de tous les paramètres AIDA en une fois par modèle
    2. Lecture batch de tous les paramètres AROME en une fois par réseau
    3. Pré-calcul des statistiques AROME (mean, std, min, max)
    4. Cache à 2 niveaux (mémoire + disque)
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

    # =========================================================================
    # OPTIMISATION 1: Préparer la liste de tous les paramètres à charger
    # =========================================================================
    
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
    
    # Paramètres AROME nouvelle version (NetCDF)
    params_arome = {
        param: VARIABLES[param]['index_model_arome']
        for param in VARIABLES_PLOT
        if VARIABLES[param]['index_model_arome'] is not None
    }

    # =========================================================================
    # OPTIMISATION 2: Lecture batch des observations (1 seul appel)
    # =========================================================================
    
    obs_data_batch = read_aida.donnees_batch(
        start_doy, end_doy,
        str(start_day.year), str(end_day.year),
        params_obs,
        'Tf'
    )
    
    # =========================================================================
    # OPTIMISATION 3: Lecture batch des modèles AIDA
    # =========================================================================
    
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
    
    # =========================================================================
    # OPTIMISATION 4: Lecture batch AROME NetCDF (tous params à la fois)
    # =========================================================================
    
    # Liste des paramètres AROME à charger
    arome_params_to_load = [v for v in params_arome.values() if v is not None]
    
    arome_data_batch = {}
    for reseau in RESEAUX:
        # Une seule lecture de tous les fichiers pour tous les paramètres
        arome_data_batch[reseau] = read_arome.donnees_batch(
            start_day, end_day, reseau, arome_params_to_load
        )
    
    # =========================================================================
    # CONSTRUCTION de la structure de données
    # =========================================================================
    
    for param in VARIABLES_PLOT:
        
        data.setdefault(param, {})
        
        # ---------------------------------------------------------------------
        # Observations (depuis le batch)
        # ---------------------------------------------------------------------
        obs_model = 'Tf'
        data[param][obs_model] = {}
        
        if param in obs_data_batch:
            values_obs, time_obs, _ = obs_data_batch[param]
            data[param][obs_model]['values'] = values_obs
            data[param][obs_model]['time'] = time_obs
        else:
            data[param][obs_model]['values'] = None
            data[param][obs_model]['time'] = None
        
        # ---------------------------------------------------------------------
        # Modèles numériques
        # ---------------------------------------------------------------------
        for model in MODELS:
            
            data[param].setdefault(model, {})
            
            for reseau in RESEAUX:
                
                data[param][model].setdefault(reseau, {})
                
                # -------------------------------------------------------------
                # AROME enveloppes
                # -------------------------------------------------------------
                if model == "Arome":
                    
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
                                'values_P1': {},
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
                            'values_P1': {},
                            #'values_P2': {},
                            #'values_P3': {},
                            #'values_P4': {},
                            'time': {}
                        })
                
                # -------------------------------------------------------------
                # AROME / ARPEGE (AIDA) 
                # -------------------------------------------------------------
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
        
        # ---------------------------------------------------------------------
        # Création des figures (identique)
        # ---------------------------------------------------------------------
        charts[param] = go.Figure()
        graphs[param] = dcc.Graph(
            id=f'graph_{param}',
            figure=charts[param]
        )
    
    return data, charts, graphs