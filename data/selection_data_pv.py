#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from config.variables import VARIABLES_PV_PLOT, VARIABLES
from config.models import MODELS_PV_CONFIG
from data import read_aida


def selection_donnees_PV(start_day, end_day):
    """
    Lecture des données PV pour tous les paramètres et tous les modèles.

    Args:
        start_day (datetime.date): premier jour de la période
        end_day   (datetime.date): dernier jour de la période

    Returns:
        dict: data[param][model] = {'values': array, 'time': list}
    """
    doy1 = datetime.datetime(
        int(start_day.year), int(start_day.month), int(start_day.day)
    ).strftime('%j')

    doy2 = datetime.datetime(
        int(end_day.year), int(end_day.month), int(end_day.day)
    ).strftime('%j')

    annee1 = str(start_day.year)
    annee2 = str(end_day.year)

    parametres_par_plateforme = {}

    for model, cfg in MODELS_PV_CONFIG.items():
        plateforme = cfg["plateforme"]
        param_key  = cfg["param_key"]

        parametres_par_plateforme.setdefault(plateforme, {})

        for param in VARIABLES_PV_PLOT:
            index_aida = VARIABLES[param].get(param_key)
            if index_aida is None:
                continue
            cle = f"{param}__{model}"
            parametres_par_plateforme[plateforme][cle] = index_aida

    # ------------------------------------------------------------------
    # Lecture batch 
    # ------------------------------------------------------------------
    batch_results = {}
    for plateforme, params_dict in parametres_par_plateforme.items():
        batch_results[plateforme] = read_aida.donnees_batch(
            doy1, doy2, annee1, annee2,
            params_dict,
            plateforme
        )

    # ------------------------------------------------------------------
    # Construction de la structure de données finale
    # ------------------------------------------------------------------
    data = {}

    for param in VARIABLES_PV_PLOT:
        data.setdefault(param, {})

        for model, cfg in MODELS_PV_CONFIG.items():
            plateforme = cfg["plateforme"]
            cle        = f"{param}__{model}"

            result = batch_results.get(plateforme, {}).get(cle)

            if result is not None:
                values, time, _ = result
                data[param][model] = {'values': values, 'time': time}
            else:
                data[param][model] = {'values': None, 'time': None}

    return data