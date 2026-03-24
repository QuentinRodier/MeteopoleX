from app import app

from dash import dcc
import plotly.graph_objects as go

#from . import read_aida
#from . import read_arome
#import lecture_mesoNH

from config.variables import VARIABLES_PLOT, VARIABLES
from config.config import MODELS_CONFIG, RESEAUX
from data.data_loader import data_loader

import numpy as np
import pandas as pd

import datetime
from datetime import date, timedelta
import matplotlib.dates as mdates


def calcul_biais(start_day, end_day):

    doy1 = datetime.datetime(int(start_day.year), int(
        start_day.month), int(start_day.day)).strftime('%j')
    doy2 = datetime.datetime(int(end_day.year), int(end_day.month), int(end_day.day)).strftime('%j')

    biais = {}
    #biais_mnh = {}

    # création d'un dataframe vide avec les valeurs des dates de la période
    # (start_day,end_day), toutes les heures car modele OPER = sorties
    # horaires.
    dt = mdates.num2date(mdates.drange(datetime.datetime(int(start_day.year),
                                                         int(start_day.month),
                                                         int(start_day.day)),
                                       datetime.datetime(int(end_day.year),
                                                         int(end_day.month),
                                                         int(end_day.day)),
                                       datetime.timedelta(minutes=30)))

    dataallyear = [i.replace(tzinfo=None) for i in dt]
    dataframe_sanstrou = pd.DataFrame(index=dataallyear)

    # Chargement des données
    #data_mnh = lecture_mesoNH.mesoNH(start_day, end_day, MODELS_BIAIS, VARIABLES_PLOT)
    loader = data_loader.load_series(start_day, end_day)
    base = loader["base"]

    for param in VARIABLES_PLOT:
            biais.setdefault(param, {})

            # --- OBS ---
            obs_pack = base.get(param, {}).get("Tf", {})
            values_obs = obs_pack.get("values", None)
            time_obs = obs_pack.get("time", None)

            if values_obs is None or time_obs is None:
                # pas d'obs => NaN partout
                for model in MODELS_CONFIG.keys():
                    biais[param].setdefault(model, {})
                    for reseau in RESEAUX:
                        biais[param][model][reseau] = {"values": np.nan}
                continue

            df_obs = pd.DataFrame(list(values_obs), index=time_obs)
            df_obs = dataframe_sanstrou.join(df_obs).dropna()
            df_obs.index = pd.to_datetime(df_obs.index)

            # --- MODELES ---
            for model in MODELS_CONFIG.keys():  
                biais[param].setdefault(model, {})

                for reseau in RESEAUX:
                    biais[param][model].setdefault(reseau, {})

                    mod_pack = base.get(param, {}).get(model, {}).get(reseau, {})
                    runs = mod_pack.get("runs", {}) 
                    if not runs: 
                        biais[param][model][reseau]["values"] = np.nan 
                        continue 
                        
            
                    # Biais global (concaténé) — conservé si besoin ailleurs
                    s_all = pd.concat(list(runs.values()))
                    s_all = s_all[~s_all.index.duplicated(keep='last')].sort_index()
                    s_all.index = pd.to_datetime(s_all.index)
                    df_mod_all = dataframe_sanstrou.join(pd.DataFrame(s_all)).dropna()
                    df_mod_all.index = pd.to_datetime(df_mod_all.index)
                    joined_all = df_mod_all.join(df_obs, how="inner", lsuffix="_mod", rsuffix="_obs").dropna()
                    if not joined_all.empty:
                        b_all = joined_all.iloc[:, 0] - joined_all.iloc[:, 1]
                        biais[param][model][reseau]["values"] = list(b_all.values)
                        biais[param][model][reseau]["time"]   = list(b_all.index)
                    else:
                        biais[param][model][reseau]["values"] = np.nan


                    # ---- biais par run (day_str) ----
                    biais[param][model][reseau]["runs"] = {}

                    for day_str, series in runs.items():
                        if not isinstance(series, pd.Series) or series.empty:
                            continue

                        s_run = series.copy()
                        s_run.index = pd.to_datetime(s_run.index)
                        s_run = s_run.sort_index().dropna()

                        df_mod_run = pd.DataFrame({"mod": s_run.values}, index=s_run.index)
                        df_obs_local = df_obs.copy()
                        df_obs_local.columns = ["obs"]

                        tolerance = pd.Timedelta(minutes=15) 

                        merged = pd.merge_asof(
                            df_mod_run.reset_index().rename(columns={"index": "time"}),
                            df_obs_local.reset_index().rename(columns={"index": "time"}),
                            on="time",
                            tolerance=tolerance,
                            direction="nearest"
                        ).set_index("time").dropna()

                        if merged.empty:
                            continue

                        b_run = merged["mod"] - merged["obs"]
                        biais[param][model][reseau]["runs"][day_str] = b_run

    return biais
