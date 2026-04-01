import datetime
from datetime import timedelta, date

from config.models import RESEAUX

# Période par défaut
start = 7
end = 1    

today = datetime.date.today()   #date(2026, 3, 15)
yesterday = today - datetime.timedelta(days=1)

end_day = today + timedelta(days=end)
start_day = today - timedelta(days=start)


# Observations 

CONFIG_OBS = {
    'Obs' : {
        'category': 'Observations',
        'mapping': dict(color='#252525'),
        'default_selection' : ["Obs"],
        'in_dropdown': True,
    },
    'Obs_corr' : {
        'category': 'Observations',
        'mapping': dict(color='grey'),
        'opacity': 0.3,
        'in_dropdown': False,
    }
}


# Modèles

MODELS = ["Arome", 'Arpege', 'Surfex_Mascot', 'Surfex_Offline_xp1', 'Surfex_Offline_xp2', 'Surfex_Offline_xp3']

RESEAUX = ["J0:00_%3600"] 

# Ajouter un nouveau modèle = ajouter une entrée ici
MODELS_CONFIG = {
    'Arpege': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Opérationnel',
        'is_climatology': False,
        'callback_param': 'reseau_arpege',
        'dropdown_id':    'multi_select_line_chart_ARPEGE',
        'file_prefix':    'arpege',
        'default_selection': ['Arpege_00h'],
        'mapping': {
            "Arpege_00h":  (RESEAUX[0], dict(color="red")),
        },
        'max_forecast_days': 4,
    },
    'Arome': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Opérationnel',
        'is_climatology': False,
        'callback_param': 'reseau_arome',
        'dropdown_id':    'multi_select_line_chart_AROME',
        'file_prefix':    'arome',
        'default_selection': ['Arome_00h'],
        'mapping': {
            "Arome_00h":  (RESEAUX[0], dict(color="blue")),
        },
        'max_forecast_days': 2,
    },
    'Surfex_Mascot': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Modélisation',
        'is_climatology': False,
        'callback_param': 'reseau_mascot',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Mascot',
        'file_prefix':    'mascot',
        'default_selection': [],
        'mapping': {
            "Surfex_Mascot_00h":  (RESEAUX[0], dict(color="darkorange")),
        },
        'max_forecast_days': 4,
    },
    'Surfex_Offline_xp1': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Modélisation',
        'is_climatology': True,
        'callback_param': 'reseau_offline_xp1',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Offline_xp1',
        'file_prefix':    'offlinerefontexp1',
        'default_selection': [],
        'mapping': {
            "Surfex_Offline_xp1":  (RESEAUX[0], dict(color="purple", dash='dash')),
        },
        'max_forecast_days': None,
    },
    'Surfex_Offline_xp2': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Modélisation',
        'is_climatology': True,
        'callback_param': 'reseau_offline_xp2',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Offline_xp2',
        'file_prefix':    'offlinerefontexp2',
        'default_selection': [],
        'mapping': {
            "Surfex_Offline_xp2":  (RESEAUX[0], dict(color="violet", dash='dash')),
        },
        'max_forecast_days': None,
    },
    'Surfex_Offline_xp3': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Modélisation',
        'is_climatology': True,
        'callback_param': 'reseau_offline_xp3',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Offline_xp3',
        'file_prefix':    'offlinerefontexp3',
        'default_selection': [],
        'mapping': {
            "Surfex_Offline_xp3":  (RESEAUX[0], dict(color="blueviolet", dash='dash')),
        },
        'max_forecast_days': None,
    },
}


#Opacité des courbes
OPACITY_MIN = 0.1
OPACITY_MAX = 1.0