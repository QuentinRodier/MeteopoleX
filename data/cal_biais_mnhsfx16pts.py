#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  12 08:25:41 2026
@author: Renaud Lestringant
"""
import matplotlib.dates as mdates
import datetime  as dt
import pandas as pd
import numpy as np
import xarray as xr
import sys
import os.path
from time import time

from config.models import Npts

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
     level = 1
     VAR = nc.variables[param][:,level,:,:] 
   if param not in ['formule_tmp10m','formule_ff10m','TKET']:
     VAR = nc.variables[param] 
   return VAR
#--------------------------------------------------------------

#--------------------------------------------------------------
def biais(start_day, end_day, param_mnhsfx16pts, v_obs, t_obs):
    biais_param = {}

    ni = nj = int(np.sqrt(Npts))

    if v_obs is None:
      for i in range(ni):
        for j in range(nj):
          point = 1 + j + i*nj
          str_point = f"{point:02}"
          biais_param[str_point]={}
          biais_param[str_point]['values'] = np.nan
    else: 
      #tic=time()
      srep = '/'   # ou '/12/' quand cela existera !!!!!
      # il faudra faire calculer les biais pour tous les choix de réseaux
      # de RESEAUX_mnhsfx16pts et imiter ce qui est fait pour les
      #série temporelles (data/ et callback/ !)
      param = param_mnhsfx16pts
      foldername = '/cnrm/ktrm/manip/METEOPOLEX/MESONH-3D/Toulouse/'
    
      start_day = dt.datetime(start_day.year, start_day.month, start_day.day) 
      end_day   = dt.datetime(  end_day.year,   end_day.month,   end_day.day)
      end_day -= dt.timedelta(days=1) # conformité avec EMI !!!

      # Ensemble des jours de la période
      dates_list = mdates.num2date(mdates.drange(start_day,end_day,dt.timedelta(days=1)), tz=None)
      dates_list = [i.replace(tzinfo=None) for i in dates_list]
      Ndays = len(dates_list)

      if param in ['GFLUX' , 'TSRAD']:
        T = [30*n-1 for n in range(1,Ndays*48+1)]
        v_obs = v_obs[T]
        t_obs = t_obs[T]

      #biais_points = np.full((len(t_obs), ni*nj) , np.nan)
      biais_points = np.full((Ndays*48, ni*nj) , np.nan)
      day = 1
      for date in dates_list:
        i1 = 1 + (day-1)*(2*24)
        i2 = i1 + 2*(24-1)
        liste_indices = np.arange(i1,i2+1,2) 

        extract_filename = "extract-16.mesonh-surfex.nc"
        anneemoisjour = str(date.year)+f"{int(date.month):02}"+f"{int(date.day):02}"
        filename = foldername + anneemoisjour + srep + extract_filename

        if os.path.isfile(filename):
          nc = xr.open_dataset(filename,decode_times=True)
          VAR = cal_VAR(nc, param)
          for i in range(ni):
            for j in range(nj):  
              point = 1 + j + i*nj
              str_point = f"{point:02}"
              Ntime_effectif = VAR[:,i,j].values.size
              dummy = VAR[0:Ntime_effectif,i,j].values
              if Ntime_effectif > 24: Ntime_effectif = 24
              biais_points[liste_indices[0:Ntime_effectif] , point-1] = VAR[0:Ntime_effectif,i,j].values
              interp_vals = 0.5 * (dummy[0:Ntime_effectif-1]+dummy[1:Ntime_effectif]) 
              biais_points[1+liste_indices[0:Ntime_effectif-1] , point-1] = interp_vals
              #break #j
            #break #i
        day += 1
        #break #day

      for i in range(ni):
        for j in range(nj):
          point = 1 + j + i*nj
          str_point = f"{point:02}"
          biais_param[str_point]={}
          biais_param[str_point]['values'] = biais_points[:,point-1]
          biais_param[str_point]['time']   = t_obs[0:Ndays*48]
          biais_param[str_point]['ndays']  = Ndays
          temp_to_offset = ['T2M','formule_tmp10m','TSRAD','TG1P1']
          if param in temp_to_offset:
            biais_param[str_point]['values'] -= 273.15
          #if param in ['H', 'LE']:
          #  biais_param[str_point]['values'] = -biais_param[str_point]['values']
          if param == 'HU2M':
            biais_param[str_point]['values'] *= 100
          biais_param[str_point]['values'] -= v_obs[0:Ndays*48]  

    #toc = time()
    #print('durée = '+str(toc-tic))

    # renvoie un dictionnaire dont les keys sont les "points". Chaque point
    # a une 'values' et un 'time'
    return biais_param
