from app import app
import datetime
from config.variables import VARIABLES_PV_PLOT, VARIABLES
from config.models import MODELS_PV
from dash import dcc
from . import read_aida
import plotly.graph_objects as go

def selection_donnees_PV(start_day, end_day):
    
    data_PV = {}
    chart_PV = {}
    graph_PV = {}
    
    doy1 = datetime.datetime(int(start_day.year), int(start_day.month), int(start_day.day)). strftime('%j')
    doy2 = datetime.datetime(int(end_day.year), int(end_day.month), int(end_day.day)). strftime('%j')
    
    for param in VARIABLES_PV_PLOT:
        if param not in data_PV:
            data_PV[param] = {}
        for model in MODELS_PV:
            if model not in data_PV[param]:
                data_PV[param][model] = {}
                
                if model == "Obs_moy":
                    id_aida = VARIABLES[param]["index_obs_moy"]
                    # Read AIDA : lit tous les paramètres alors que selection de données va
                    # lire uniquement un parametre specifique
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year),id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
                
                elif model == "Obs_1":
                    id_aida = VARIABLES[param]["index_obs_1"]
                    # Read AIDA : lit tous les paramètres alors que selection de données va
                    # lire uniquement un parametre specifique
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year),id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
                    
                elif model == "Obs_2":
                    id_aida = VARIABLES[param]["index_obs_2"]
                    # Read AIDA : lit tous les paramètres alors que selection de données va
                    # lire uniquement un parametre specifique
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year),id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
                    
                elif model == "Obs_3":
                    id_aida = VARIABLES[param]["index_obs_3"]
                    # Read AIDA : lit tous les paramètres alors que selection de données va
                    # lire uniquement un parametre specifique
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year),id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
                    
                elif model == "Obs_cnr4":
                    id_aida = VARIABLES[param]["index_cnr4"]
                    # Read AIDA : lit tous les paramètres alors que selection de données va
                    # lire uniquement un parametre specifique
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year),id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
                
                elif model == "Obs_bf5":
                    id_aida = VARIABLES[param]["index_bf5"]
                    # Read AIDA : lit tous les paramètres alors que selection de données va
                    # lire uniquement un parametre specifique
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year),id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
                
                elif model == "arome_J0":
#                        if param == "RGD":
#                            param_arome = VARIABLES[param]['index_arome_J0']
#                            donnee_arome = read_arome.donnees(start_day, end_day, 0, param_arome)
#                            mean_arome= donnee_arome.groupby(donnee_arome.index).mean()[param_arome]
#                            data_PV[param][model]['values'] = mean_arome[param_arome]
#                            data_PV[param][model]['time'] = [datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S") for ts_str in mean_arome.index]
#                        else:
                    id_aida = VARIABLES[param]["index_arome_J0"] 
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year), id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
                        
                elif model == "arome_J-1":
#                            if param == "RGD":
#                            param_arome = VARIABLES[param]['index_arome_J-1']
#                            donnee_arome = read_arome.donnees(start_day, end_day, 12, param_arome)
#                            mean_arome= donnee_arome.groupby(donnee_arome.index).mean()[param_arome]
#                            data_PV[param][model]['values'] = mean_arome[param_arome]
#                            data_PV[param][model]['time'] = [datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S") for ts_str in mean_arome.index]
#                        else:
                    id_aida = VARIABLES[param]["index_arome_J-1"] 
                    (values, time, header) = read_aida.donnees(doy1, doy2, str(start_day.year), str(end_day.year), id_aida, "Tf")
                    data_PV[param][model]['values'] = values
                    data_PV[param][model]['time'] = time
         
        chart_PV[param] = go.Figure()
        graph_PV[param] = dcc.Graph(id='graph_PV_'+param, figure=chart_PV[param])

    return data_PV, chart_PV, graph_PV
