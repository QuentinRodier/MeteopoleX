#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de calcul des biais moyens horaires (cycle diurne).
"""

import numpy as np
import pandas as pd
from datetime import timedelta

from config.variables import VARIABLES_PLOT
from config.config import RESEAUX, MODELS_CONFIG

from data.biais import calcul_biais


def biais_moyen(start_day, end_day):

    biais = calcul_biais(start_day, end_day)
    biais_moy = {}

    for param in VARIABLES_PLOT:
        biais_moy.setdefault(param, {})

        for model in MODELS_CONFIG.keys():

            if MODELS_CONFIG[model].get('is_climatology', False):
                continue

            biais_moy[param].setdefault(model, {})

            for reseau in RESEAUX:
                biais_moy[param][model].setdefault(reseau, {})

                block = biais.get(param, {}).get(model, {}).get(reseau, {})
                runs = block.get("runs", {})

                if not runs:
                    biais_moy[param][model][reseau]["values"] = []
                    biais_moy[param][model][reseau]["time"] = []
                    continue

                # Séparation par échéance
                lead_data = {}  # lead_data[age_days][hour] = [valeurs]

                for day_str, series in runs.items():
                    if not isinstance(series, pd.Series) or series.empty:
                        continue

                    series.index = pd.to_datetime(series.index)
                    run_date = pd.to_datetime(day_str, format="%Y%m%d").date()

                    for timestamp, value in series.items():
                        age_days = max(0, (timestamp.date() - run_date).days)
                        hour = timestamp.hour

                        lead_data.setdefault(age_days, {}).setdefault(hour, []).append(value)

                # Construire la courbe continue : 4 jours x 24h
                all_values = []
                all_times = []  # en heures depuis le début (0, 1, ..., 102)

                for age_days in sorted(lead_data.keys()):
                    hours_dict = lead_data[age_days]
                    for hour in range(24):
                        vals = hours_dict.get(hour, [])
                        mean_val = np.nanmean(vals) if vals else np.nan
                        all_values.append(mean_val)
                        all_times.append(age_days * 24 + hour)

                biais_moy[param][model][reseau]["values"] = all_values
                biais_moy[param][model][reseau]["time"] = all_times

    return biais_moy

