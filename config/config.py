import datetime
from datetime import timedelta, date

from config.models import RESEAUX

# Période par défaut
start = 7
end = 1    

today = datetime.date(2026, 3, 15) #.date.today()
yesterday = today - datetime.timedelta(days=1)

end_day = today + timedelta(days=end)
start_day = today - timedelta(days=start)


# Observations 

CONFIG_OBS = {
    'Obs' : {
        'mapping': dict(color='#252525'),
        'default_selection' : ["Obs"],
    },
    'Obs_corr' : {
        'mapping': dict(color='grey'),
        'opacity': 0.3,
    }
}


# Modèles

MODELS = ["Arome", 'Arpege', 'Surfex_Mascot', 'Surfex_Offline']

RESEAUX = ["J0:00_%3600"] 

# Ajouter un nouveau modèle = ajouter une entrée ici
MODELS_CONFIG = {
    'Arpege': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'has_analysis':    True,
        'callback_param': 'reseau_arpege',
        'dropdown_id':    'multi_select_line_chart_ARPEGE',
        'file_prefix':    'arpege',
        'default_selection': ['Arpege_00h'],
        'mapping': {
            "Arpege_00h":  (RESEAUX[0], dict(color="red")),
        },
    },
    'Arome': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'has_analysis':    True,
        'callback_param': 'reseau_arome',
        'dropdown_id':    'multi_select_line_chart_AROME',
        'file_prefix':    'arome',
        'default_selection': ['Arome_00h'],
        'mapping': {
            "Arome_00h":  (RESEAUX[0], dict(color="blue")),
        },
    },
    'Surfex_Mascot': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'has_analysis':    True,
        'callback_param': 'reseau_mascot',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Mascot',
        'file_prefix':    'mascot',
        'default_selection': [],
        'mapping': {
            "Surfex_Mascot_00h":  (RESEAUX[0], dict(color="darkorange", mode='markers', marker_size=4)),
        },
    },
    'Surfex_Offline': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'has_analysis':    False,
        'callback_param': 'reseau_offline',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Offline',
        'file_prefix':    'offline',
        'default_selection': [],
        'mapping': {
            "Surfex_Offline":  (RESEAUX[0], dict(color="purple", dash='dash', constant_opacity=True)),
        },
    },
}


#Opacité des courbes
OPACITY_MIN = 0.1
OPACITY_MAX = 1.0