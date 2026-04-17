#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  23 09:05:41 2026
@author: Renaud Lestringant
"""
import matplotlib.dates as mdates
import datetime  as dt
import pandas as pd
import glob
import numpy as np
import xarray as xr

import os.path

from config.models import Npts, POINTS_mnhsfx16pts, init_POINTS

from functools import lru_cache

#--------------------------------------------------------------
def cal_VAR(nc,param):

   if param == 'formule_tmp10m':
     T2 = nc.variables['THT'][:,2,:,:]  
     T1 = nc.variables['THT'][:,1,:,:]  
     P2 = nc.variables['PABST'][:,2,:,:]  
     P1 = nc.variables['PABST'][:,1,:,:]  
     meanT = 0.5 * (T2+T1)
     meanP_norm = 0.5 * (P2+P1) / 100000.
     VAR = meanT * (meanP_norm)**(2./7.)   

   if param == 'formule_ff10m':
     U10 = nc.variables['MER10M']
     V10 = nc.variables['ZON10M']
     VAR = np.sqrt(U10**2 + V10**2)

   if param == 'TKET':
     #nc = nc.sel(level=1)
     level = 1
     VAR = nc.variables[param][:,level,:,:] 

   if param not in ['formule_tmp10m','formule_ff10m','TKET']:
     VAR = nc.variables[param] 
 
   return VAR
#--------------------------------------------------------------
#--------------------------------------------------------------
def cal_reseau_data(reseau):
    hours     = 24
    Ntime_max = 24
    if reseau == "00h":
      srep = '/'
    if reseau == "12h":
      srep = '/12/'

    return hours, Ntime_max, srep
#--------------------------------------------------------------
#--------------------------------------------------------------
def create_datevar(date , srep):
  ext = ':00:00.000000000'
  amj  = str(date.year)+'-'+f"{int(date.month):02}"+'-'+f"{int(date.day):02}"
  date += dt.timedelta(days=1)
  amj1 = str(date.year)+'-'+f"{int(date.month):02}"+'-'+f"{int(date.day):02}"

  if srep == '/': 
    liste_amj  = [amj +'T'+f"{int(k):02}"+ext for k in range(1,24+1)] 
    liste_amj1 = [] 

  if srep == '/12/': 
    liste_amj  = [amj +'T'+f"{int(k):02}"+ext for k in range(12+1,24+1)] 
    liste_amj1 = [amj1+'T'+f"{int(k):02}"+ext for k in range(1,12+1)] 

  return np.array(liste_amj+liste_amj1)
#--------------------------------------------------------------


@lru_cache(maxsize=15)
def _open_mnhsfx16pts_cached(filepath):
    """Ouvre un fichier extract-16 et le garde en mémoire"""
    return xr.open_dataset(filepath, decode_times=True)


#--------------------------------------------------------------
def donnees(start_day, end_day, reseau, param_mnhsfx16pts):

    ni = nj = int(np.sqrt(Npts))

    param = param_mnhsfx16pts
    
    start_day = dt.datetime(start_day.year, start_day.month, start_day.day) 
    end_day   = dt.datetime(  end_day.year,   end_day.month,   end_day.day)

    # Ensemble des jours de la période
    dates_list = mdates.num2date(mdates.drange(start_day,end_day,dt.timedelta(days=1)), tz=None)

    hours, Ntime_max, srep = cal_reseau_data(reseau)
    
    foldername = '/cnrm/ktrm/manip/METEOPOLEX/MESONH-3D/Toulouse/'

    # Dataset qui contiendra les données du paramètre d'entrée
    data_var_alldomain = pd.DataFrame([])
    
    day = 1
    for date in dates_list:
        if day == len(dates_list) and srep == '/12/': hours = 12

        extract_filename = "extract-16.mesonh-surfex.nc"
        anneemoisjour = str(date.year)+f"{int(date.month):02}"+f"{int(date.day):02}"
        filename = foldername + anneemoisjour + srep + extract_filename

        if os.path.isfile(filename):
          #nc = xr.open_dataset(filename,decode_times=True)
          nc = _open_mnhsfx16pts_cached(filename)
          datevar = create_datevar(date, srep)

          VAR = cal_VAR(nc, param)

          for i in range(ni):
           for j in range(nj):  
            # Données aux heures choisies
            var_allhours = pd.DataFrame([])
            # Toutes les données
            temp_var_allhours = pd.DataFrame([])

            point = 1 + j + i*nj

            valeurs = np.nan * np.ones(Ntime_max)
            Ntime_effectif = VAR[:,i,j].values.size
            if Ntime_effectif > 24: Ntime_effectif = 24
            valeurs[0:Ntime_effectif] = VAR[0:Ntime_effectif,i,j].values

            # Toutes les heures
            #temp_var_allhours[param] = pd.Series(valeurs[0:Ntime_effectif], index=datevar)
            temp_var_allhours[param] = pd.Series(valeurs[:], index=datevar)
            # On garde 24 heures, sauf pour le dernier jour de la période (12 heures si '/12/')
            var_allhours[param] = temp_var_allhours[param].iloc[0:hours]
            var_allhours['Point'] = point
            # Toutes les données dans un seul dataframe
            data_var_alldomain = pd.concat([data_var_alldomain, var_allhours])
        else:
          for i in range(ni):
           for j in range(nj):
            datevar = create_datevar(date, srep)
            var_allhours = pd.DataFrame([])
            temp_var_allhours = pd.DataFrame([])
            point = 1 + j + i*nj
            valeurs = np.nan * np.ones(Ntime_max)
            temp_var_allhours[param] = pd.Series(valeurs[:], index=datevar)
            var_allhours[param] = temp_var_allhours[param].iloc[0:hours]
            var_allhours['Point'] = point
            data_var_alldomain = pd.concat([data_var_alldomain, var_allhours])

        day += 1
        #break #day

    ###Quelques conversions
    if not data_var_alldomain.empty:
        temp_to_offset = ['T2M','formule_tmp10m','TSRAD','TG1P1']
        if param in temp_to_offset:
          data_var_alldomain[param] -= 273.15
        #if param in ['H', 'LE']:
        #  data_var_alldomain[param] = - data_var_alldomain[param]
        if param == 'HU2M':
          data_var_alldomain[param] *= 100
       
   # renvoie un dataframe pandas
    return data_var_alldomain

