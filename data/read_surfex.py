import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
import numpy as np
import xarray as xr
from functools import lru_cache
import pickle
from pathlib import Path

filepath = '/home/hennequina/SURFEX/SURF_ATM_DIAGNOSTICS.OUT.nc'

CACHE_DIR = Path("/home/manip/MeteopoleX/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

@lru_cache(maxsize=5)
def _open_surfex_cached(filepath):
    """Ouvre un fichier NetCDF SURFEX et le garde en mémoire"""
    return xr.open_dataset(filepath, decode_times=True)

def donnees_surfex_batch(start_day, end_day, params_list,
                         filepath=filepath):
    """
    Lecture des données SURFEX pour tous les paramètres demandés,
    filtrées sur la période [start_day, end_day].

    Args:
        start_day, end_day : datetime
        params_list        : liste des variables SURFEX à charger
                             ex: ['T2M', 'HU2M', 'H', 'LE', 'SWDC', 'LWDC']
        filepath           : chemin vers le fichier SURFEX

    Returns:
        dict {param: DataFrame avec colonne [param] et index = time}
    """
    # --- Cache disque ---
    cache_key = (
        f"surfex_{start_day.strftime('%Y%m%d')}"
        f"_{end_day.strftime('%Y%m%d')}"
        f"_{'_'.join(p for p in params_list if p)}"
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

    # --- Ouverture du fichier ---
    nc = _open_surfex_cached(filepath)

    # --- Filtrage temporel ---
    start_dt = np.datetime64(dt.datetime(start_day.year, start_day.month, start_day.day))
    end_dt   = np.datetime64(dt.datetime(end_day.year,   end_day.month,   end_day.day, 23, 59, 59))

    nc_slice = nc.sel(time=slice(start_dt, end_dt))
    datevar  = nc_slice['time'].values

    # --- Extraction des paramètres ---
    results = {}

    for param in params_list:
        if param is None:
            results[param] = pd.DataFrame()
            continue

        # Variables calculées
        if param == 'LWu':
            if 'LWDC' in nc_slice and 'LWUC' in nc_slice:
                values = (nc_slice['LWUC'] - nc_slice['LWDC']).squeeze()
            else:
                results[param] = pd.DataFrame()
                continue

        elif param == 'SWu':
            if 'SWDC' in nc_slice and 'SWUC' in nc_slice:
                values = (nc_slice['SWUC'] - nc_slice['SWDC']).squeeze()
            else:
                results[param] = pd.DataFrame()
                continue

        elif param not in nc_slice:
            print(f"Paramètre '{param}' absent du fichier SURFEX")
            results[param] = pd.DataFrame()
            continue

        else:
            # squeeze() supprime les dimensions lat=1 et lon=1 → série 1D
            values = nc_slice[param].squeeze()

        results[param] = pd.DataFrame({param: values.values}, index=datevar)

    # --- Conversions d'unités ---
    for param in params_list:
        if param is None or param not in results or results[param].empty:
            continue

        if param in ('T2M', 'T2M_NAT'):
            # Conversion K → °C seulement si nécessaire
            if results[param][param].median() > 100:
                results[param][param] -= 273.15

        elif param == 'HU2M':
            # Conversion fraction → % seulement si nécessaire
            if results[param][param].median() <= 1.0:
                results[param][param] *= 100

    # --- Sauvegarde cache ---
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"Erreur sauvegarde cache SURFEX: {e}")

    return results


def donnees_surfex(start_day, end_day, param,
                   filepath=filepath):
    """Wrapper simple pour un seul paramètre SURFEX."""
    results = donnees_surfex_batch(start_day, end_day, [param], filepath=filepath)
    return results.get(param, pd.DataFrame())

def compute_statistics_surfex(data_df, param):
    if data_df is None or data_df.empty or param not in data_df.columns:
        return {'runs': {}, 'time': {}}

    series = data_df[param].copy()

    return {
        'runs': {'offline': series},
        'time': {'offline': series.index},
    }
