from app import app
from datetime import date, timedelta
import datetime

from dash import Input, Output
import plotly.graph_objects as go

from data.selection_data_pv import selection_donnees_PV
from config.variables import VARIABLES_PV_PLOT, VARIABLES
from config.models import MODELS_PV

# Période par défaut
today = datetime.date.today()
yesterday = today - timedelta(days=1)
start_day = yesterday
end_day = today

# Extraction des données PV
data_PV, chart_PV, graph_PV = selection_donnees_PV(start_day, end_day)

# Callbacks
output_PV = []

for param in VARIABLES_PV_PLOT:
    # Définition des Outputs c-à-d des graphs qui seront mis à jour
    output_PV.append(Output('graph_PV_'+param, 'figure'))


# Chaque Input prend en argument l'id d'une dcc.Input et la valeur qu'elle récupère
@app.callback(output_PV, [Input('my-date-picker-range', 'start_date'),
                          Input('my-date-picker-range', 'end_date') ])
def update_linePV(start_day, end_day):
    if start_day is not None:
        start_day = date.fromisoformat(start_day)
    if end_day is not None:
        end_day = date.fromisoformat(end_day)

    # UPDATE DES DATES APRES LE CALLBACK
    data_PV, chart_PV, graph_PV = selection_donnees_PV(start_day, end_day)
    
    list_charts_PV = []
    
    for param in VARIABLES_PV_PLOT:
        #chart = go.Figure()  # Créez un nouveau graphique pour chaque paramètre
        chart_PV[param] = go.Figure()
        
        for model in MODELS_PV:
            if model == "Obs_moy":
                line_param = dict(color='black')
            elif model == "Obs_1":
                line_param = dict(color='red')
            elif model == "Obs_2":
                line_param = dict(color='green')
            elif model == "Obs_3":
                line_param = dict(color='purple')
            elif model == "Obs_cnr4":
                line_param = dict(color='orange')
            elif model == "Obs_bf5":
                line_param = dict(color='brown')
            elif model == "arome_J0":
                line_param = dict(color='blue')
            else:
                line_param = dict(color='blue', dash='dot')
                
            # Ajouter une trace au graphique actuel pour chaque modèle
            chart_PV[param].add_trace(go.Scatter(x=data_PV[param][model]['time'],
                                                 y=data_PV[param][model]['values'], 
                                                 line=line_param,
                                                 name=model,
                                                 showlegend=True)
                                      )

        
        # Mettre à jour le layout du graphique avec les titres et les axes appropriés
        chart_PV[param].update_layout(height=450, width=800,
                                      xaxis_title="Date et heure",
                                      yaxis_title=str(VARIABLES[param]['unit']),
                                      title=VARIABLES[param]['title'])

        list_charts_PV.append(chart_PV[param])  # Ajouter le graphique actuel à la liste

    return list_charts_PV  # Retourner la liste de graphiques à la fin de la fonction
