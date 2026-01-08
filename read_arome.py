#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 17:05:41 2023
@author: nicolasc
"""
import matplotlib.dates as mdates
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
#print(datatest.loc[datatest['Point']==15])
