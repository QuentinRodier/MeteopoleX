#!/usr/bin/env python3

# Tf = observations AIDA
# Rt = AROME AIDA
# Gt = ARPEGE AIDA
# AROME = AROME NetCDF

# Liste des modèles (et observations) dans les séries temporelles
MODELS = ["Gt", "Rt", "Arome"]
#MODELS = ["Gt", "Rt", "Tf"]

# Liste des modèles sur lesquels les biais et biais moyens sont calculés
MODELS_BIAIS=['Tf', 'Rt', 'Gt'] #Avec ancienne version de Arome #!# Ajout enveloppe

# Liste des réseaux pour les modèles
RESEAUX = ["J-1:00_%3600", "J-1:12_%3600", "J0:00_%3600", "J0:12_%3600"]

# Couleur et légendes par modèles sur Série temporelle
MODELS_PLOT = {"MésoNH_Arp":
              {'name': 'Gt',
               'color': 'purple'},
              "MésoNH_Aro":
              {'name': 'Rt',
               'color': "limegreen"},
              "MésoNH_Obs":
              {'name': 'Tf',
               'color': 'orange'},
              "SURFEX_Arp":
              {'name': 'Gt',
               'color': 'darkgreen'},
              "SURFEX_Aro":
              {'name': 'Rt',
               'color': 'pink'},
              "SURFEX_Obs":
              {'name': 'Tf',
               'color': 'gold'}}

# Couleur et légendes par modèles sur Profils Verticaux
MODELS_PLOT_RS = {"Gt": {
    "name": "MNH-ARPEGE",
    "line": "dash"},
    "Rt": {
    "name": "MNH-AROME",
    "line": "longdash"},
    "Tf": {
    "name": "MNH-OBS",
    "line": "solid"},
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

# Liste des modèles (courbes) pour la vue Panneaux photovoltaïques
MODELS_PV = ["Obs_moy", "Obs_1", "Obs_2", "Obs_3", "Obs_cnr4", "Obs_bf5", "arome_J0", "arome_J-1"]



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
