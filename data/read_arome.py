#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 17:05:41 2023
@author: nicolasc
"""
'''import matplotlib.dates as mdates
import datetime  as dt
import pandas as pd
import glob
import numpy as np
import xarray as xr


def donnees(start_day, end_day, reseau, param):
    
    start_day = dt.datetime(start_day.year, start_day.month, start_day.day) 
    end_day = dt.datetime(end_day.year, end_day.month, end_day.day)
    
    foldername = '/cnrm/ktrm/manip/METEOPOLEX/AROME/Toulouse/'
    #foldername = '/home/manip/data/aro_toulouse/'

    #reseau = '00'
    reseau_hr = reseau[-8:-6] # 00 ou 12
    reseau_j = reseau[0:2]    # J- ou J0
    
    # Si réseau J-1 on prend le modèle de la veille
    if reseau_j == 'J-':
        day_delay = 1
        # Heures à afficher
        if reseau_hr == '00':
            hour_delay = 24
        else:
            hour_delay = 12
    else:
        hour_delay = 0
        day_delay = 0
        
    # Si réseau de 12UTC, on se place dans le bon repertoire
    if reseau_hr == '12':
        srep = '/12/'
    else:
        srep = '/'
       
    # Dataset qui contiendra les données du paramètre d'entrée
    data_var_alldomain = pd.DataFrame([])
    
    # Ensemble des jours de la période
    dates_list = mdates.num2date(mdates.drange(start_day,end_day,dt.timedelta(days=1)), tz=None)
    #dates_list = mdates.num2date(mdates.drange(start_day,end_day+dt.timedelta(1),dt.timedelta(days=1)), tz=None)
    # Nombre de jours
    days_nr = len(dates_list)
    #print(dates_list)
    day = 1
    
    for date in dates_list:
        
        # Si réseau J-1 on prend la veille
        date -= dt.timedelta(days=day_delay)
           
        # AAAAMM
        anneemois = str(date.year)+f"{int(date.month):02}"
        
        # Nombre d'heures à afficher : 36 pour le dernier jour
        if day == days_nr:
            hours = 36
        else:
            hours = 24
        
        # 16 premiers points = Météopole
        files_list = np.sort(glob.glob(foldername + anneemois + srep + 'miniAROME-L90_point_*_' +
                             date.strftime('%Y%m%d') + reseau_hr +'.nc'))[:16]

        for j,fichier in enumerate(files_list):
            
            # Extraction du point sur le nom du fichier
            point = int(fichier[-16:-14])
                         
            # Les fichiers de chaque point sont ouverts au format xarray
            nc = xr.open_dataset(fichier,decode_times=True)
            
            # Données aux heures choisies
            var_allhours = pd.DataFrame([])
            # Toutes les données
            temp_var_allhours = pd.DataFrame([])

            # LWu n'existe pas encore et doit être calculé
            if param == 'LWu' : 
                nc['LWu'] = nc['LWd'] - nc['LWn']
            # Car SWu n'existe pas encore et doit être calculé    
            if param == 'SWu' : 
                nc['SWu'] = nc['SWd'] - nc['SWn']
            # On ne prend que la tke au niveau vertical le plus bas 
            if param == 'tke':
                nc = nc.sel(nlev=90)           
            
            valeurs = nc.variables[param]

            # Les variables'f' (flux) sont prises aux heures et demie
            # il y a donc une valeur de moins que pour les autres variables
            if nc.variables[param].shape[0] == 36:
                datevar = nc['time_f'].values
            # Autres variables = 37 valeurs
            else:
                datevar = nc['time'].values
                
            # Toutes les heures
            temp_var_allhours[param] = pd.Series(valeurs[:], index=datevar)

            #print(list_date, fichier, temp_var_allhours[param])
            # On garde 24 heures, sauf pour le dernier jour de la période (36 heures)
            var_allhours[param] = temp_var_allhours[param][hour_delay:hours+hour_delay]
            var_allhours['Point'] = point
            # Toutes les données dans un seul dataframe
            data_var_alldomain = pd.concat([data_var_alldomain, var_allhours])

        day += 1
        
    ###Quelques conversions
    if not data_var_alldomain.empty:
        
        if param == 't2m':
            data_var_alldomain[param] -= 273.15
        
        if param == 'sfc_sens_flx' or param == 'sfc_lat_flx':
            data_var_alldomain[param] = -data_var_alldomain[param]
            
        if param == 'hu2m':
            data_var_alldomain[param] *= 100
       
   # renvoie un dataframe pandas
    return data_var_alldomain

#datatest = donnees(dt.datetime(2026, 1, 6),dt.datetime(2026, 1, 7), 'J0:12_%3600', 't2m')
#print(datatest)
#print(datatest.loc[datatest['Point']==15])'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
import glob
import numpy as np
import xarray as xr
from functools import lru_cache
import pickle
from pathlib import Path


# Cache disque pour les données AROME pré-calculées
CACHE_DIR = Path("/home/manip/MeteopoleX/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _make_arome_cache_key(start_day, end_day, reseau):
    """Clé unique pour le cache AROME"""
    return f"arome_{start_day.strftime('%Y%m%d')}_{end_day.strftime('%Y%m%d')}_{reseau}"


def _get_arome_cache_path(cache_key):
    """Chemin du fichier cache"""
    return CACHE_DIR / f"{cache_key}.pkl"


@lru_cache(maxsize=20)
def _open_netcdf_cached(filepath):
    """
    Ouvre un fichier NetCDF et le garde en mémoire
    Evite de ré-ouvrir le même fichier plusieurs fois
    """
    return xr.open_dataset(filepath, decode_times=True)


def donnees_batch(start_day, end_day, reseau, params_list):
    """
    Lecture optimisée de AROME pour tous les paramètres en une seule passe
    
    Args:
        start_day, end_day
        reseau
        params_list: liste des paramètres AROME à charger
            
    Returns:
        dict {param: DataFrame avec colonnes [param, 'Point']}
              avec index = time
    """
    # Vérifier le cache d'abord
    cache_key = _make_arome_cache_key(start_day, end_day, reseau)
    cache_path = _get_arome_cache_path(cache_key)
    
    if cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                cached = pickle.load(f)
                # Vérifier que tous les params sont présents
                if all(p in cached for p in params_list if p is not None):
                    return cached
        except:
            pass
    
    # Préparer les paramètres
    start_day = dt.datetime(start_day.year, start_day.month, start_day.day) 
    end_day = dt.datetime(end_day.year, end_day.month, end_day.day)
    
    foldername = '/cnrm/ktrm/manip/METEOPOLEX/AROME/Toulouse/'
    
    reseau_hr = reseau[-8:-6]  # 00 ou 12
    reseau_j = reseau[0:2]     # J- ou J0
    
    # Délais selon le réseau
    if reseau_j == 'J-':
        day_delay = 1
        hour_delay = 24 if reseau_hr == '00' else 12
    else:
        hour_delay = 0
        day_delay = 0
    
    # Répertoire selon l'heure
    srep = '/12/' if reseau_hr == '12' else '/'
    
    # Dictionnaire de résultats par paramètre
    results = {param: pd.DataFrame([]) for param in params_list if param is not None}
    
    # Liste des jours
    dates_list = mdates.num2date(
        mdates.drange(start_day, end_day, dt.timedelta(days=1)), 
        tz=None
    )
    days_nr = len(dates_list)
    
    for day_idx, date in enumerate(dates_list, 1):
        
        date -= dt.timedelta(days=day_delay)
        anneemois = str(date.year) + f"{int(date.month):02}"
        
        # Heures à extraire
        hours = 36 if day_idx == days_nr else 24
        
        # Fichiers des 16 points Méteopole
        files_pattern = (
            foldername + anneemois + srep + 
            'miniAROME-L90_point_*_' + 
            date.strftime('%Y%m%d') + reseau_hr + '.nc'
        )
        files_list = np.sort(glob.glob(files_pattern))[:16]
        
        # Ouverture du fichier une fois et extraction de tous les paramètres
        for fichier in files_list:
            
            point = int(fichier[-16:-14])
            
            # Ouvrir le fichier une seule fois
            nc = _open_netcdf_cached(fichier)
            
            # Boucle sur tous les paramètres demandés
            for param in params_list:
                
                if param is None:
                    continue
                
                # Variables calculées
                if param == 'LWu':
                    if 'LWd' in nc and 'LWn' in nc:
                        values = nc['LWd'] - nc['LWn']
                    else:
                        continue
                        
                elif param == 'SWu':
                    if 'SWd' in nc and 'SWn' in nc:
                        values = nc['SWd'] - nc['SWn']
                    else:
                        continue
                        
                elif param == 'tke':
                    if param in nc:
                        values = nc[param].sel(nlev=90)
                    else:
                        continue
                        
                else:
                    # Variable standard
                    if param not in nc:
                        continue
                    values = nc[param]
                
                # Déterminer l'index temporel
                if values.shape[0] == 36:  # Flux
                    datevar = nc['time_f'].values
                else:
                    datevar = nc['time'].values
                
                # Extraire les données
                temp_df = pd.DataFrame({param: values[:]}, index=datevar)
                
                # Ne garder que les heures voulues
                selected_df = temp_df.iloc[hour_delay:hours+hour_delay].copy()
                selected_df['Point'] = point
                
                # Ajouter au résultat
                results[param] = pd.concat([results[param], selected_df])
    
    # Conversions d'unités
    for param in params_list:
        if param is None or results[param].empty:
            continue
            
        if param == 't2m':
            results[param][param] -= 273.15
            
        elif param in ['sfc_sens_flx', 'sfc_lat_flx']:
            results[param][param] = -results[param][param]
            
        elif param == 'hu2m':
            results[param][param] *= 100
    
    # Sauvegarder dans le cache
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"Erreur sauvegarde cache AROME: {e}")
    
    return results


def compute_statistics(data_df, param):
    """
    Calcule les statistiques (mean, std, min, max) pour un paramètre AROME
    
    Args:
        data_df: DataFrame avec colonnes [param, 'Point'] et index=time
        param: nom du paramètre
        
    Returns:
        dict avec clés:
            - 'values_mean', 'values_mean_plus_std', 'values_mean_moins_std'
            - 'values_max', 'values_min'
            - 'values_P1', 'values_P2', 'values_P3', 'values_P4' (points spécifiques)
            - 'time'
        Version triée :
            - 'value_P1' 
            - 'time'
    """
    if data_df.empty:
        return {
            #'values_mean': pd.Series(),
            #'values_mean_plus_std': pd.Series(),
            #'values_mean_moins_std': pd.Series(),
            #'values_max': pd.Series(),
            #'values_min': pd.Series(),
            'values_P': pd.Series(),
            #'values_P2': pd.Series(),
            #'values_P3': pd.Series(),
            #'values_P4': pd.Series(),
            'time': pd.Series()
        }
    
    time_index = data_df.index
    
    # Statistiques groupées par temps
    grouped = data_df.groupby(time_index)
    
    mean_vals = grouped[param].mean()
    std_vals = grouped[param].std()
    
    result = {
        #'values_mean': mean_vals,
        #'values_mean_plus_std': mean_vals + std_vals,
        #'values_mean_moins_std': mean_vals - std_vals,
        #'values_max': grouped[param].max(),
        #'values_min': grouped[param].min(),
    }
    
    # Points spécifiques
    point_map = {
        'values_P': 11,  # Point proche
        #'values_P2': 15,  # 100% urbain
        #'values_P3': 6,   # 100% champs
        #'values_P4': 1,   # 50/50
    }
    
    for key, point_id in point_map.items():
        mask = data_df['Point'] == point_id
        if mask.any():
            result[key] = data_df.loc[mask, param]
        else:
            result[key] = pd.Series()
    
    # Index temporel depuis P1
    if not result['values_P'].empty:
        result['time'] = result['values_P'].index
    #elif not result['values_mean'].empty:
    #    result['time'] = result['values_mean'].index
    else:
        result['time'] = pd.Series()
    
    return result


def donnees(start_day, end_day, reseau, param):
    """
    Returns:
        DataFrame avec colonnes [param, 'Point'] et statistiques déjà calculées
    """
    # Charger via batch (plus efficace même pour 1 param)
    results = donnees_batch(start_day, end_day, reseau, [param])
    return results.get(param, pd.DataFrame())


def clear_cache(older_than_days=30):
    """Nettoie le cache AROME"""
    import time
    
    now = time.time()
    cutoff = now - (older_than_days * 86400)
    
    deleted = 0
    for cache_file in CACHE_DIR.glob("arome_*.pkl"):
        if cache_file.stat().st_mtime < cutoff:
            cache_file.unlink()
            deleted += 1
    
    print(f"Cache AROME nettoyé: {deleted} fichiers supprimés")