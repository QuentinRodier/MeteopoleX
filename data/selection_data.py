#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
import datetime
from dash import dcc
import plotly.graph_objects as go

from . import read_aida 
from . import read_operationnel

from config.variables import VARIABLES_PLOT, VARIABLES
from config.config import MODELS, RESEAUX, MODELS_CONFIG


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
