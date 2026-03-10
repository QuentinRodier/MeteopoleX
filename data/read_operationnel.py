import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
import numpy as np
import xarray as xr
from functools import lru_cache
import pickle
from pathlib import Path
import datetime
from datetime import timedelta, date
from config.config import today, yesterday


OPERATIONNEL_DIR = Path("/cnrm/proc/projet_emi/sample_netcdf")
CACHE_DIR = Path("/home/manip/MeteopoleX/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Mapping model → préfixe dans le nom de fichier
MODEL_FILE_PREFIX = {
    'Arpege': 'arpege',   # ex: arpege_date_reseau.nc
    'Arome':  'arome',    # ex: arome_date_reseau.nc
}


def _build_filepath(model, date, reseau):
    """
    Construit le chemin vers le fichier opérationnel
    selon le modèle et le réseau.
    """
    
    reseau_hr = reseau[-8:-6]   # '00' ou '12'

    prefix = MODEL_FILE_PREFIX.get(model, model.lower())
    filename = f"{prefix}_{date.strftime('%Y%m%d')}_{reseau_hr}.nc"
    return OPERATIONNEL_DIR / filename


@lru_cache(maxsize=5)
def _open_operationnel_cached(filepath):
    """Ouvre un fichier NetCDF opérationnel et le garde en mémoire"""
    return xr.open_dataset(filepath, decode_times=True)

def donnees_operationnel_batch(start_day, end_day, params_list,
                               model, reseau):
    """
    Lecture des données opérationnelles pour tous les paramètres demandés,
    en itérant sur chaque jour de la période [start_day, end_day]
    (un fichier par jour, comme AROME).

    Args:
        start_day, end_day : datetime
        params_list        : liste des variables à charger
        model              : 'Arpege' ou 'Arome'
        reseau             : ex 'J0:00_%3600', 'J0:12_%3600'

    Returns:
        dict {param: DataFrame avec colonne [param] et index = time}
    """

    # --- Cache disque ---
    cache_key = (
        f"operationnel_{model}_{reseau.replace(':', '-').replace('%', '')}"
        f"_{start_day.strftime('%Y%m%d')}"
        f"_{end_day.strftime('%Y%m%d')}"
    )
    cache_path = CACHE_DIR / f"{cache_key}.pkl"

    if cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                cached = pickle.load(f)
                if all(p in cached for p in params_list if p is not None):
                    return cached
        except Exception:
            pass

    # --- Préparation des délais ---
    start_day = dt.datetime(start_day.year, start_day.month, start_day.day)
    end_day   = dt.datetime(end_day.year,   end_day.month,   end_day.day)

    reseau_hr = reseau[-8:-6]   # '00' ou '12'
    reseau_j  = reseau[0:2]     # 'J-' ou 'J0'

    if reseau_j == 'J-':
        day_delay  = 1
        hour_delay = 24 if reseau_hr == '00' else 12
    else:
        day_delay  = 0
        hour_delay = 0

    # --- Initialisation des résultats ---
    results = {p: pd.DataFrame() for p in params_list if p is not None}

    # --- Itération sur les jours ---
    dates_list = mdates.num2date(
        mdates.drange(start_day, end_day, dt.timedelta(days=1)),
        tz=None
    )
    days_nr = len(dates_list)

    if model=='Arome':
        dates_list_aro = dates_list[:2] #(J et J+1 seulement)
        days_nr_aro = len(dates_list_aro)

    for day_idx, current_date in enumerate(dates_list, 1):

        current_date -= dt.timedelta(days=day_delay)

        filepath = _build_filepath(model, current_date, reseau)

        if not filepath.exists():
            print(f"Fichier opérationnel non trouvé : {filepath}")
            continue

        try:
            nc = _open_operationnel_cached(str(filepath))
        except Exception as e:
            print(f"Erreur ouverture {filepath}: {e}")
            continue

        # Nombre d'heures à extraire (102/48 pour le dernier jour (échéance max arpège/arome), 24 sinon)
        if model=='Arome' :
            hours=48 if day_idx == days_nr_aro else 24
        elif model=='Arpege':
            hours=102 if day_idx == days_nr else 24

        datevar = nc['time'].values

        for param in params_list:
            if param is None:
                continue
            if param not in nc:
                continue

            try:
                values = nc[param].squeeze().values
                temp_df = pd.DataFrame({param: values}, index=datevar)

                selected_df = temp_df.iloc[hour_delay:hours + hour_delay].copy()
                results[param] = pd.concat([results[param], selected_df])

            except Exception as e:
                print(f"Erreur lecture '{param}' ({filepath.name}): {e}")

    # --- Conversions d'unités ---
    for param in params_list:
        if param is None or param not in results or results[param].empty:
            continue

        try:
            if param in ('tmp_2m', 'temperature_ground_1', 'temperature_ground_2'):
                if results[param][param].median() > 100:
                    results[param][param] -= 273.15

            elif param in ('hum_rel'):
                if results[param][param].median() <= 1.0:
                    results[param][param] *= 100
        except Exception as e:
            print(f"Erreur conversion d'unités pour '{param}': {e}")

    # --- Sauvegarde cache ---
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"Erreur sauvegarde cache opérationnel: {e}")

    return results


def compute_statistics_operationnel(data_df, param):
    """
    Statistiques pour un paramètre opérationnel (point unique, pas de groupby).
    Retourne le même format que compute_statistics() AROME pour compatibilité.
    """
    if data_df.empty or param not in data_df.columns:
        return {'values_P': pd.Series(), 'time': pd.Series()}

    series = data_df[param].copy()

    return {
        'values_P': series,
        'time':      series.index,
    }


