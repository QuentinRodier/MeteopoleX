import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
import xarray as xr
from functools import lru_cache
import pickle
from pathlib import Path
from config.config import today, yesterday

OPERATIONNEL_DIR = Path("/cnrm/proc/projet_emi/sample_netcdf")
CACHE_DIR = Path("/home/manip/MeteopoleX/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Mapping model → préfixe dans le nom de fichier
MODEL_FILE_PREFIX = {
    'Arpege': 'arpege',   # ex: arpege_date_reseau.nc
    'Arome':  'arome',    # ex: arome_date_reseau.nc
    'Surfex_Mascot': 'surfex_mascot'
}


def _build_filepath(model, date, reseau):
    """
    Construit le chemin vers le fichier opérationnel selon le modèle et le réseau.
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
    Lecture des données opérationnelles pour tous les paramètres demandés.
    Chaque fichier (une date x un réseau) est lu en entier et conservé séparément
    pour permettre la superposition des courbes dans la figure.

    Args:
        start_day, end_day : datetime
        params_list        : liste des variables à charger
        model              : nom du modèle (ex: 'Arpege', 'Arome')
        reseau             : ex 'J0:00_%3600', 'J-1:12_%3600'

    Returns:
        dict {param: {date_str: DataFrame}}
        ex: {'tmp_2m': {'20251231': DataFrame, '20260101': DataFrame}}
    """

    # --- Date du fichier à lire selon le réseau ---
    if reseau.startswith("J0"):
        run_date = today
    elif reseau.startswith("J-1"):
        run_date = yesterday
    else:
        print(f"[{model}] Réseau inconnu : {reseau}")
        return {p: {} for p in params_list if p is not None}

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

    # --- Lecture du fichier unique ---
    results = {p: {} for p in params_list if p is not None}

    date_str = run_date.strftime('%Y%m%d')
    filepath = _build_filepath(model, run_date, reseau)

    if not filepath.exists():
        print(f"[{model}] Fichier non trouvé : {filepath}")
        return results

    try:
        nc = _open_operationnel_cached(str(filepath))
    except Exception as e:
        print(f"[{model}] Erreur ouverture {filepath}: {e}")
        return results

    datevar = nc['time'].values

    for param in params_list:
        if param is None or param not in nc:
            continue
        try:
            values  = nc[param].squeeze().values
            temp_df = pd.DataFrame({param: values}, index=datevar)
            results[param][date_str] = temp_df
        except Exception as e:
            print(f"[{model}] Erreur lecture '{param}' ({filepath.name}): {e}")

    # --- Conversions d'unités ---
    for param in params_list:
        if param is None or param not in results or not results[param]:
            continue
        for date_str, df in results[param].items():
            if df.empty:
                continue
            try:
                if param in ('tmp_2m', 'temperature_ground_1', 'temperature_ground_2', 'TG0_5cm', 'TG2_5cm', 'TG70cm', 'TG15cm', 'TG30cm', 'TG50cm', 'TG70cm', 'TG90cm'):
                    if df[param].median() > 100:
                        results[param][date_str][param] -= 273.15
                elif param in ('hum_rel',):
                    if df[param].median() <= 1.0:
                        results[param][date_str][param] *= 100
            except Exception as e:
                print(f"[{model}] Erreur conversion '{param}' ({date_str}): {e}")

    # --- Sauvegarde cache ---
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"[{model}] Erreur sauvegarde cache: {e}")

    return results


def compute_statistics_operationnel(data_dict, param):
    """
    Prépare les données pour l'affichage : une série par run (fichier lu).

    Args:
        data_dict : {date_str: DataFrame}  — un DataFrame par fichier
        param     : nom de la variable

    Returns:
        {'runs': {date_str: Series}, 'time': {date_str: Index}}
    """
    if not data_dict or not isinstance(data_dict, dict):
        return {'runs': {}, 'time': {}}

    runs  = {}
    times = {}

    for date_str, df in data_dict.items():
        if df is None or not isinstance(df, pd.DataFrame) or df.empty or param not in df.columns:
            continue
        runs[date_str]  = df[param].copy()
        times[date_str] = df.index

    return {'runs': runs, 'time': times}


