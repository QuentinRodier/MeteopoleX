import datetime
from datetime import timedelta, date

from config.models import RESEAUX

start = 7
end = 2

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# Période par défaut
end_day = today + timedelta(days=end)
start_day = today - timedelta(days=start)


# Modèles

MODELS = ["Arome", 'Arpege', 'Surfex_Mascot']

RESEAUX = ["J0:00_%3600"] 

# Configuration complète par modèle
# Ajouter un nouveau modèle = ajouter une entrée ici
MODELS_CONFIG = {
    'Arpege': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'callback_param': 'reseau_arpege',
        'dropdown_id':    'multi_select_line_chart_ARPEGE',
        'file_prefix':    'arpege',
        'default_selection': ['Arpege_00h'],
        'mapping': {
            "Arpege_00h":  (RESEAUX[0], dict(color="#33a02c")),
        },
    },
    'Arome': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'callback_param': 'reseau_arome',
        'dropdown_id':    'multi_select_line_chart_AROME',
        'file_prefix':    'arome',
        'default_selection': ['Arome_00h'],
        'mapping': {
            "Arome_00h":  (RESEAUX[0], dict(color="#1f78b4")),
        },
    },
    'Surfex_Mascot': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'callback_param': 'reseau_mascot',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Mascot',
        'file_prefix':    'mascot',
        'default_selection': ['Surfex_Mascot_00h'],
        'mapping': {
            "Surfex_Mascot_00h":  (RESEAUX[0], dict(color="#d95f02")),
        },
    },
}


#Sélection des modèles et réseaux affichés par défaut 
selection_obs = ["Obs"]