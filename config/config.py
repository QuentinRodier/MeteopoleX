import datetime
from datetime import timedelta, date

from config.models import RESEAUX

# Période par défaut
start = 7
end = 1    

today = datetime.date.today()   
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

MODELS = ["Arome", 'Arpege', 'Surfex_Mascot', 'Surfex_Offline_ref', 'Surfex_Offline_physiographie_observée', 'Surfex_Offline_CI_observées']

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
        'default_selection': ['Arpege 00h'],
        'mapping': {
            "Arpege 00h":  (RESEAUX[0], dict(color="red")),
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
        'default_selection': ['Arome 00h'],
        'mapping': {
            "Arome 00h":  (RESEAUX[0], dict(color="blue")),
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
            "Surfex Mascot 00h":  (RESEAUX[0], dict(color="darkorange")),
        },
        'max_forecast_days': 4,
    },
    'Surfex_Offline_ref': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Modélisation',
        'is_climatology': True,
        'callback_param': 'reseau_offline_ref',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Offline_ref',
        'file_prefix':    'offlineref',
        'default_selection': [],
        'mapping': {
            "Surfex Offline référence":  (RESEAUX[0], dict(color="purple", dash='dash')),
        },
        'max_forecast_days': None,
    },
    'Surfex_Offline_physiographie_observée': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Modélisation',
        'is_climatology': True,
        'callback_param': 'reseau_offline_pgd',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Offline_pgd',
        'file_prefix':    'offlinepgd',
        'default_selection': [],
        'mapping': {
            "Surfex Offline physiographie observée":  (RESEAUX[0], dict(color="violet", dash='dash')),
        },
        'max_forecast_days': None,
    },
    'Surfex_Offline_CI_observées': {
        'reader':         'operationnel',
        'param_key':      'index_model',
        'category':       'Modélisation',
        'is_climatology': True,
        'callback_param': 'reseau_offline_prep',
        'dropdown_id':    'multi_select_line_chart_SURFEX_Offline_prep',
        'file_prefix':    'offlineprep',
        'default_selection': [],
        'mapping': {
            "Surfex Offline CI observées":  (RESEAUX[0], dict(color="blueviolet", dash='dash')),
        },
        'max_forecast_days': None,
    },
}


#Opacité des courbes
OPACITY_MIN = 0.1
OPACITY_MAX = 1.0