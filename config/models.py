#!/usr/bin/env python3

# Tf = observations AIDA
# Rt = AROME AIDA
# Gt = ARPEGE AIDA
# AROME = AROME NetCDF

# Liste des modèles 
MODELS = ["Tf", "Rt", 'Gt']

# Liste des réseaux pour les modèles
RESEAUX = ["J0:00_%3600", "J0:12_%3600", "J-1:00_%3600", "J-1:12_%3600"]

#Sélection des modèles et réseaux affichés par défaut 
selection_obs = ["Obs"]
selection_arpege = ["Arpège_J0_00h"]
selection_arome = ["Arome_J0_00h"]


# Couleur et légendes par modèles sur Profils Verticaux
MODELS_PLOT_RS = {
    "ARP": {
    "name": "ARP-OPER",
    "line": "dashdot"},
    "ARO": {
    "name": "ARO-OPER",
    "line": "dot"},
    "Ab": {
    "name": "OBS-AMDAR",
    "line": "solid"}
    }

'''"Gt": {
    "name": "MNH-ARPEGE",
    "line": "dash"},
    "Rt": {
    "name": "MNH-AROME",
    "line": "longdash"},
    "Tf": {
    "name": "MNH-OBS",
    "line": "solid"},'''

# Liste des modèles (courbes) pour la vue Panneaux photovoltaïques
MODELS_PV = ["Obs_moy", "Obs_1", "Obs_2", "Obs_3", "Obs_cnr4", "Obs_bf5", "arome_J0", "arome_J-1"]

MODELS_PV_CONFIG = {
    "Obs_moy": {
        "param_key":  "index_obs_moy",   # clé dans VARIABLES[param]
        "color":      "black",
        "dash":       None,              
        "label":      "Obs moyenne",
        "plateforme": "Tf",
    },
    "Obs_1": {
        "param_key":  "index_obs_1",
        "color":      "red",
        "dash":       None,
        "label":      "Obs capteur 1",
        "plateforme": "Tf",
    },
    "Obs_2": {
        "param_key":  "index_obs_2",
        "color":      "green",
        "dash":       None,
        "label":      "Obs capteur 2",
        "plateforme": "Tf",
    },
    "Obs_3": {
        "param_key":  "index_obs_3",
        "color":      "purple",
        "dash":       None,
        "label":      "Obs capteur 3",
        "plateforme": "Tf",
    },
    "Obs_cnr4": {
        "param_key":  "index_cnr4",
        "color":      "orange",
        "dash":       None,
        "label":      "Obs CNR4",
        "plateforme": "Tf",
    },
    "Obs_bf5": {
        "param_key":  "index_bf5",
        "color":      "brown",
        "dash":       None,
        "label":      "Obs BF5",
        "plateforme": "Tf",
    },
    "arome_J0": {
        "param_key":  "index_arome_J0",
        "color":      "blue",
        "dash":       None,
        "label":      "Arome J0",
        "plateforme": "Tf",
    },
    "arome_J-1": {
        "param_key":  "index_arome_J-1",
        "color":      "blue",
        "dash":       "dot",
        "label":      "Arome J-1",
        "plateforme": "Tf",
    },
}


LEGENDE_HEURES_PROFILS = {"00h": {
    "value": "00h",
    "num_val": 0,
    "color": "black"},
    "3h": {
    "value": "3h",
    "num_val": 12,
    "color": "brown"},
    "6h": {
    "value": "6h",
    "num_val": 24,
    "color": "red"},
    "9h": {
    "value": "9h",
    "num_val": 36,
    "color": "orange"},
    "12h": {
    "value": "12h",
    "num_val": 48,
    "color": "green"},
    "15h": {
    "value": "15h",
    "num_val": 60,
    "color": "blue"},
    "18h": {
    "value": "18h",
    "num_val": 72,
    "color": "purple"},
    "21h": {
    "value": "21h",
    "num_val": 84,
    "color": "fuchsia"}}

# "num_val" est le rang de la valeur correspondant à l'heure, par exemple : 
# puisqu'il y a une valeur tous les quarts d'heure (4 valeurs par heure), 
# pour 9h on prend la 9x4=36ème valeur du paramètre.
LEGENDE_HEURES_PROFILS_AROARP = {"00h": {
    "value": "00h",
    "num_val": 0,
    "color": "black"},
    "3h": {
    "value": "3h",
    "num_val": 3,
    "color": "brown"},
    "6h": {
    "value": "6h",
    "num_val": 6,
    "color": "red"},
    "9h": {
    "value": "9h",
    "num_val": 9,
    "color": "orange"},
    "12h": {
    "value": "12h",
    "num_val": 12,
    "color": "green"},
    "15h": {
    "value": "15h",
    "num_val": 15,
    "color": "blue"},
    "18h": {
    "value": "18h",
    "num_val": 18,
    "color": "purple"},
    "21h": {
    "value": "21h",
    "num_val": 21,
    "color": "fuchsia"}}
