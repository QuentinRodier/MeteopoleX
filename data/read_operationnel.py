import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
import xarray as xr
from functools import lru_cache
import pickle
from pathlib import Path
from config.config import today, yesterday, MODELS_CONFIG

OPERATIONNEL_DIR = Path("/cnrm/proc/projet_emi/sample_netcdf")
CACHE_DIR = Path("/home/manip/MeteopoleX/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _build_filepath(model, date, reseau):
    """
    Construit le chemin vers le fichier opérationnel selon le modèle et le réseau.
    """
    
    reseau_hr = reseau[-8:-6]   # '00' ou '12'

    prefix = MODELS_CONFIG[model]['file_prefix']
    filename = f"{prefix}_{date.strftime('%Y%m%d')}_{reseau_hr}.nc"
    return OPERATIONNEL_DIR / filename


@lru_cache(maxsize=5)
def _open_operationnel_cached(filepath):
    """Ouvre un fichier NetCDF opérationnel et le garde en mémoire"""
    return xr.open_dataset(filepath, decode_times=True)

def donnees_operationnel_batch(start_day, end_day, params_list, model, reseau):
    """
    Lecture des données opérationnelles pour tous les paramètres demandés.
    Un fichier est ouvert par jour entre start_day et end_day.
    Toutes les données de chaque fichier sont conservées (pas de sélection temporelle).


    Returns:
        dict {param: {date_str: DataFrame}}
    """

    # --- Génération de la liste des dates à lire ---
    n_days = (end_day - start_day).days + 1
    run_dates = [start_day + dt.timedelta(days=i) for i in range(n_days)]

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

    # --- Lecture d'un fichier par jour ---
    results = {p: {} for p in params_list if p is not None}

    for run_date in run_dates:
        date_str = run_date.strftime('%Y%m%d')
        filepath = _build_filepath(model, run_date, reseau)

        if not filepath.exists():
            print(f"[{model}] Fichier non trouvé : {filepath}")
            continue

        try:
            nc = _open_operationnel_cached(str(filepath))
        except Exception as e:
            print(f"[{model}] Erreur ouverture {filepath}: {e}")
            continue

        datevar = nc['time'].values

        for param in params_list:
            if param is None or param not in nc:
                continue
            try:
                values  = nc[param].squeeze().values
                temp_df = pd.DataFrame({param: values}, index=datevar)
                results[param][date_str] = temp_df   # clé = date du fichier
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
                if param in ('tmp_2m', 'temperature_ground_1', 'temperature_ground_2',
                             'TG0_5cm', 'TG2_5cm', 'TG70cm', 'TG15cm', 'TG30cm',
                             'TG50cm', 'TG70cm', 'TG90cm'):
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


