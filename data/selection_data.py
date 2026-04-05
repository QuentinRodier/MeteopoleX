#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
import datetime
from dash import dcc
import plotly.graph_objects as go

from . import read_aida 
from . import read_operationnel

from . import read_mnhsfx16pts_miniAROME

from config.variables import VARIABLES_PLOT, VARIABLES
from config.config import MODELS, RESEAUX, MODELS_CONFIG

from config.models import RESEAUX_mnhsfx16pts

EMPTY_BLOCK = {'runs': {}, 'time': {}}


def selection_data(start_day, end_day):
    """
    Récupération des données pour tous les modèles et paramètres.
    Aucune condition sur le nom du modèle : tout est piloté par MODELS_CONFIG.
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

    # Regrouper les paramètres par reader pour éviter les doublons de lecture
    params_by_reader = {}
    for model, cfg in MODELS_CONFIG.items():
        reader    = cfg['reader']
        param_key = cfg['param_key']

        params_by_reader.setdefault(reader, set())
        for param in VARIABLES_PLOT:
            p = VARIABLES[param].get(param_key)
            if p is not None:
                params_by_reader[reader].add(p)

    params_by_reader = {r: list(v) for r, v in params_by_reader.items()}


    #----------------------------------------------------------------------------------
    # Lecture batch des observations 
    obs_data_batch = read_aida.donnees_batch(
        start_doy, end_doy,
        str(start_day.year), str(end_day.year),
        params_obs,
        'Tf'
    )
    
    # Lecture batch des : Modèle × réseau
    ope_params = params_by_reader.get('operationnel', [])
    model_data_batch = {}

    for model, cfg in MODELS_CONFIG.items():
        if cfg['reader'] != 'operationnel':
            continue

        model_data_batch[model] = {}

        if cfg.get('is_climatology', False):
            result = read_operationnel.donnees_climato_batch(
                ope_params, model=model
            )
            for reseau in RESEAUX:
                model_data_batch[model][reseau] = result

        else:
            for reseau in RESEAUX:
                model_data_batch[model][reseau] = read_operationnel.donnees_operationnel_batch(
                    start_day, end_day, ope_params,
                    model=model, reseau=reseau
                )

    #----------------------------------------------------------------------------------
    # Structure données
    for param in VARIABLES_PLOT:
        
        data.setdefault(param, {})
        
        # --- Observations ---
        obs_model = 'Tf'
        data[param][obs_model] = {}
        
        if param in obs_data_batch:
            values_obs, time_obs, _ = obs_data_batch[param]
            data[param][obs_model]['values'] = values_obs
            data[param][obs_model]['time'] = time_obs
        else:
            data[param][obs_model]['values'] = None
            data[param][obs_model]['time'] = None

        # -------------------------------------------------------------
        # MNH-SFX extraction des 16 points miniAROME (enveloppes)
        # -------------------------------------------------------------
        model = "MNH-SFX-16pts"
        data[param].setdefault(model, {})
        for reseau in RESEAUX_mnhsfx16pts:
                    data[param][model].setdefault(reseau, {})

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

                    param_mnhsfx16pts = VARIABLES[param]['index_model_mnhsfx16pts']
                    if param_mnhsfx16pts is not None:

                        mnhsfx16pts_data = read_mnhsfx16pts_miniAROME.donnees(
                            start_day, end_day, reseau, param_mnhsfx16pts
                        )

                        if not mnhsfx16pts_data.empty:

                            time_index = mnhsfx16pts_data.index

                            model_data['values_mean'] = (
                                mnhsfx16pts_data.groupby(time_index).mean()[param_mnhsfx16pts]
                            )
                            std = mnhsfx16pts_data.groupby(time_index).std()[param_mnhsfx16pts]
                            model_data['values_mean_plus_std'] = (
                                model_data['values_mean'] + std
                            )
                            model_data['values_mean_moins_std'] = (
                                model_data['values_mean'] - std
                            )
                            model_data['values_max'] = (
                                mnhsfx16pts_data.groupby(time_index).max()[param_mnhsfx16pts]
                            )
                            model_data['values_min'] = (
                                mnhsfx16pts_data.groupby(time_index).min()[param_mnhsfx16pts]
                            )
                            model_data['values_P1'] = mnhsfx16pts_data.loc[
                                mnhsfx16pts_data['Point'] == 11, param_mnhsfx16pts
                            ]
                            model_data['values_P2'] = mnhsfx16pts_data.loc[
                                mnhsfx16pts_data['Point'] == 15, param_mnhsfx16pts
                            ]
                            model_data['values_P3'] = mnhsfx16pts_data.loc[
                                mnhsfx16pts_data['Point'] == 6, param_mnhsfx16pts
                            ]
                            model_data['values_P4'] = mnhsfx16pts_data.loc[
                                mnhsfx16pts_data['Point'] == 1, param_mnhsfx16pts
                            ]
                            model_data['time'] = model_data['values_P4'].index
        # -------------------------------------------------------------


        # --- Modèles ---
        for model, cfg in MODELS_CONFIG.items():

            data[param].setdefault(model, {})

            reader    = cfg['reader']
            param_key = cfg['param_key']
            p         = VARIABLES[param].get(param_key)

            for reseau in RESEAUX:

                data[param][model].setdefault(reseau, {})

                if p is None:
                    data[param][model][reseau].update({'values_P': {}, 'time': {}})
                    continue

                # ---------------------------------------------------------
                # Reader opérationnel : {param: {date_str: DataFrame}}
                # compute_statistics_operationnel retourne {'runs': ..., 'time': ...}
                # ---------------------------------------------------------
                if reader == 'operationnel':
                    data_dict = model_data_batch.get(model, {}).get(reseau, {}).get(p, {})

                    if isinstance(data_dict, dict) and data_dict:
                        stats = read_operationnel.compute_statistics_operationnel(data_dict, p)
                        data[param][model][reseau].update(stats)
                    else:
                        data[param][model][reseau].update(EMPTY_BLOCK.copy())

    return data
