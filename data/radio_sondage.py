#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 09:21:41 2021

@author: avrillauds
"""
import netCDF4 as nc
import datetime
from datetime import timedelta, date
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
# Lecture obs AMDAR
from . import read_aida
import pandas as pd

def radio_sondage(day, models, params_rs, heures, heures_aroarp):
    data_rs = {}
    today = day
    today_str = str(day.year)
    if len(str(day.month)) == 1:
        today_str = today_str + '0' + str(day.month)
    else:
        today_str = today_str + str(day.month)

    yyyymm = today_str

    if len(str(day.day)) == 1:
        today_str = today_str + '0' + str(day.day)
    else:
        today_str = today_str + str(day.day)

    for model in models:
        try:
            f = nc.Dataset('/home/manip/MeteopoleX/models/runs/OUTPUT/MESONH/OPER/' +
                           today_str + '00/MESONH_' + model + '_' + today_str + '00.000.nc')

            groupMEAN = '/LES_budgets/Mean/Cartesian/Not_time_averaged/Not_normalized/cart/'

            # ou bien /home/models/OUTPUT/MESONH

            if model not in data_rs:
                data_rs[model] = {}

                #print("CLEFS DICO MODELS : ", data_rs.keys())

            if 'level' not in data_rs[model]:
                data_rs[model]['level'] = f.variables['level'][:]

                for heure in heures:
                    if heure not in data_rs[model]:
                        data_rs[model][heure] = {}

                        for param in params_rs:
                            if param not in data_rs[model][heure]:
                                data_rs[model][heure][param] = {}
                                if param == "Température":
                                    P = f[groupMEAN].variables['MEAN_PRE'][heures[heure]['num_val'], :]
                                    D = (100000 / P)**(2 / 7)
                                    data_rs[model][heure][param] = (
                                        f[groupMEAN].variables['MEAN_TH'][heures[heure]['num_val'], :] / D) - 273.15

                                if param == "Humidité relative":
                                    data_rs[model][heure][param] = f[groupMEAN].variables['MEAN_REHU'][heures[heure]['num_val'], :]

                                if param == "Vent":
                                    # U=f['MEAN_U___PROC1'][0,heures[heure]['num_val'],:,0,0].data[:]
                                    # V=f['MEAN_V___PROC1'][0,heures[heure]['num_val'],:,0,0].data[:]
                                    data_rs[model][heure][param] = f[groupMEAN].variables['MEANWIND'][heures[heure]['num_val'], :]
        except FileNotFoundError:
            pass

    for model in ['ARP', 'ARO']:
        
        if model == 'ARP':
            try:
                f = nc.Dataset('/cnrm/proc/bazile/NetCdf/Toulouse/' + yyyymm +
                           '/Arpege-oper-L105_Toulouse_' + today_str + '00.nc')
            except:
                print("Fichier NC ARP manquant ou incorrect")
                continue 

        elif model == 'ARO':
            
            try:
                f = nc.Dataset('/cnrm/ktrm/manip/METEOPOLEX/AROME/Toulouse/' +
                           yyyymm + '/netcdf_tlse.tar.arome_' + today_str + '.netcdf')
            except:
                print("Fichier NC ARO manquant ou incorrect")
                continue 

        if model not in data_rs:
            data_rs[model] = {}

        if 'level' not in data_rs[model]:
            data_rs[model]['level'] = f['height_h'][1, ::-1]
            
            for heure in heures_aroarp:
                
                if heure not in data_rs[model]:
                    data_rs[model][heure] = {}
                
                for param in params_rs:
                    if param not in data_rs[model][heure]:
                        data_rs[model][heure][param] = {}
                    if param == "Température":
                        data_rs[model][heure][param] = (f['t'][heures_aroarp[heure]['num_val'], ::-1] - 273.15)
                    if param == "Humidité relative":
                        data_rs[model][heure][param] = (f['hr'][heures_aroarp[heure]['num_val'], ::-1] * 100)
                    if param == "Vent":
                        data_rs[model][heure][param] = f['Vamp'][heures_aroarp[heure]['num_val'], ::-1]


# Observations AMDAR

    model = 'Ab'

    yesterday = today - timedelta(days=1)

    doy = datetime.datetime(int(yesterday.year), int(
        yesterday.month), int(yesterday.day)).strftime('%j')

    if model not in data_rs:

        data_rs[model] = {}

        # Extraction des données AMDAR sous AIDA
        (z_val, time, header) = read_aida.donnees(
            doy, doy, str(today.year), str(today.year), 'alt_pre_amdar_cal_%60', model)
#        (z_val, time, header) = read_aida.donnees(
#            doy, doy, str(today.year), 'alt_pre_amdar_cal_%60', model)
        (t_val, time, header) = read_aida.donnees(
            doy, doy, str(today.year), str(today.year), 'tpr_air_amdar_cal_%60', model)
        (ff_val, time, header) = read_aida.donnees(
            doy, doy, str(today.year), str(today.year), 'ven_ffmoy_amdar_cal_%60', model)

        # Récupération des séries temporelles Météopôle-Flux pour avoir un point à Z=10m
        (t10, time2, header2) = read_aida.donnees(doy, doy, str(today.year), str(today.year),
                "tpr_air_ht_c1_%60_Met_%1800", 'Tf')
        (ff10, time2, header2) = read_aida.donnees(
            doy, doy, str(today.year), str(today.year), "ven_ff_10mn_c1_UV_%1800", 'Tf')

        # Impossible de boucler sur des 'None' : on ne prend les profils seulement
        # lorsque les valeurs existent
        if z_val is not None and t_val is not None and ff_val is not None and t10 is not None and ff10 is not None:

            # Construction du dataframe regrouypant Z, T et FF
            df_z = pd.DataFrame(list(z_val), index=(time))
            df_t = pd.DataFrame(list(t_val), index=(time))
            df_ff = pd.DataFrame(list(ff_val), index=(time))

            df_amdar = pd.concat([df_z, df_t], axis=1)
            df_amdar = pd.concat([df_amdar, df_ff], axis=1)

            # Nomination des colonnes
            df_amdar.columns = ['altitude', 'temperature', 'vent']

            # Conversion K -> degC
            df_amdar['temperature'] = df_amdar['temperature'] - 273.15

            ih = 0

            for heure in heures_aroarp:

                heure_num = heures_aroarp[heure]['num_val']

                ih = ih + 1

                if heure not in data_rs[model]:
                    data_rs[model][heure] = {}

                # Construction d'une plage horaire dont on va prendre les données
                if ih < 5:

                    date_profil = yesterday.strftime('%Y-%m-%d 0' + heure[0:1] + ':%M:%S')

                    if ih == 1:

                        date_start = datetime.datetime.strptime(date_profil, "%Y-%m-%d %H:%M:%S")
                        date_end = datetime.datetime.strptime(
                            date_profil, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)

                    else:

                        date_start = datetime.datetime.strptime(
                            date_profil, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
                        date_end = datetime.datetime.strptime(
                            date_profil, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)

                else:

                    date_profil = yesterday.strftime('%Y-%m-%d ' + heure[0:2] + ':%M:%S')

                    date_start = datetime.datetime.strptime(
                        date_profil, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
                    date_end = datetime.datetime.strptime(
                        date_profil, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)

                # Sélection de la plage horaire dans le dataframe
                mask = (df_amdar.index > date_start) & (df_amdar.index < date_end)

                # Observations à z=10m : toutes les 30min, on prend (H*2)-1 pour les avoir
                # aux heures H
                T_10m = t10[(heure_num * 2) - 1]
                FF_10m = ff10[(heure_num * 2) - 1]
                TIME = time2[(heure_num * 2) - 1]

                # Ajout des valeurs à 10m au DataFrame correspondant
                dict_10m = {'altitude': 10, 'temperature': [T_10m], 'vent': [FF_10m]}

                df_10m = pd.DataFrame(dict_10m, index=[TIME])
                df_amdar = df_amdar._append(df_10m)

                # Sélection de la plage horaire dans le dataframe
                mask = (df_amdar.index > date_start) & (df_amdar.index < date_end)

                if 'level' not in data_rs[model][heure]:

                    data_rs[model][heure]['level'] = list(df_amdar['altitude'].loc[mask])

                for param in params_rs:

                    if param not in data_rs[model][heure]:
                        data_rs[model][heure][param] = {}

                    if param == "Température":

                        data_rs[model][heure][param] = list(df_amdar['temperature'].loc[mask])

                    if param == "Vent":

                        data_rs[model][heure][param] = list(df_amdar['vent'].loc[mask])

    return data_rs
