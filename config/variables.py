#!/usr/bin/env python3

# Ce dictionnaire rassemble les spécificités de chaque paramètres tracés. Les 2 premiers 'index' sont les noms donnés sur AIDA au paramètre en question, dans les observations et dans les modèles.
 #!# Ajout enveloppe Le 'index_modl_arome' est le dico de la nouvelle recuperation AROME.
# Le 'title' est le titre du graph qui sera affiché, donc c'est l'utilisateur qui choisi, idem pour le unit, c'est à l'utilisateur de rentrer les bonnes unités.
VARIABLES = {
    "tmp_2m": {
        "index_obs": "tpr_air_bs_c1_%60_Met_%1800",
        "index_model": "tmp_2m",
        "index_model_mnhsfx16pts" : "T2M",
        "title": "Température à 2m",
        "unit": "°C"
    },
    "tmp_10m": {
        "index_obs": "tpr_air_ht_c1_%60_Met_%1800",
        "index_model": "tmp_10m",
        "index_model_mnhsfx16pts" : "formule_tmp10m",
        "title": "Température à 10m",
        "unit": "°C"
    },
    "hum_rel": {
        "index_obs": "hum_relcapa_bs_c1_%60_Met_%1800",
        "index_model": "hum_rel",
        "index_model_mnhsfx16pts" : "HU2M",
        "title": "Humidité relative",
        "unit": "%"
    },
    "vent_ff10m": {
        "index_obs": "ven_ff_10mn_c1_UV_%1800",
        "index_model": "vent_ff10m",
        "index_model_mnhsfx16pts" : "formule_ff10m",
        "title": "Vent moyen à 10m",
        "unit": "m/s"
    },
    "SWD": {
        "index_obs": "ray_rgd_cnr1_c2_%60_Met_%1800",
        "index_model": "SWD",
        "index_model_mnhsfx16pts" : "SWD",
        "title": "Rayonnement global descendant (SW down)",
        "unit": "W/m²"
    },
    "SWU": {
        "index_obs": "ray_rgm_cnr1_c2_%60_Met_%1800",
        "index_model": "SWU",
        "index_model_mnhsfx16pts" : "SWU",
        "title": "Rayonnement global montant (SW up)",
        "unit": "W/m²"
    },
    "LWD": {
        "index_obs": "ray_ird_cnr1_c2_%60_Met_%1800",
        "index_model": "LWD",
        "index_model_mnhsfx16pts" : "LWD",
        "title": "Rayonnement IR descendant (LW down)",
        "unit": "W/m²"
    },
    "LWU": {
        "index_obs": "ray_irm_cnr1_c2_%60_Met_%1800",
        "index_model": "LWU",
        "index_model_mnhsfx16pts" : "LWU",
        "title": "Rayonnement IR montant (LW up)",
        "unit": "W/m²"
    },    
    "flx_chaleur_sens": {
        "index_obs": "flx_hs_tson_Chb_%1800",
        "index_model": "flx_chaleur_sens",
        "index_model_mnhsfx16pts" : "H",
        "title": "Flux de chaleur sensible",
        "unit": "W/m²"
    },
    "flx_chaleur_lat": {
        "index_obs": "flx_le_Chb_%1800",
        "index_model": "flx_chaleur_lat",
        "index_model_mnhsfx16pts" : "LE",
        "title": "Flux de chaleur latente",
        "unit": "W/m²"
    },    
    "flx_chaleur_sol": {
        "index_obs": "flx_phi0_moy_c2_%60",
        "index_model": "flx_chaleur_sol",
        "index_model_mnhsfx16pts" : "GFLUX",
        "title": "Flux de conduction dans le sol",
        "unit": "W/m²"
    },
    "t_surface": {
        "index_obs": "tpr_solIR_c1_%60",
        "index_model": "t_surface",
        "index_model_mnhsfx16pts" : "TSRAD",
        "title": "Température de surface",
        "unit": "°C"
    },
    "TG1cm": {
        "index_obs": "tpr_sol1cm_f2_tn1_valid_%900", 
        "index_model": "TG1cm",
        "index_model_mnhsfx16pts" : "TG1P1",
        "title": "Température du sol à -1 cm",
        "unit": "°C"
    },
    "TG3cm": {
        "index_obs": "tpr_sol3cm_f2_tn1_valid_%900", 
        "index_model": "TG3cm",
        "index_model_mnhsfx16pts" : None,
        "title": "Température du sol à -3 cm",
        "unit": "°C"
    },
    "TG10cm": {
        "index_obs": "tpr_sol10cm_f2_tn1_valid_%900",
        "index_model": "TG10cm",
        "index_model_mnhsfx16pts" : None,
        "title": "Température du sol à -10 cm",
        "unit": "°C"
    },
    "TG20cm": {
        "index_obs": "tpr_sol20cm_f2_tn1_valid_%900",
        "index_model": "TG20cm",
        "index_model_mnhsfx16pts" : None,
        "title": "Température du sol à -20 cm",
        "unit": "°C"
    },
    "TG30cm": {
        "index_obs": "tpr_sol30cm_f2_tn1_valid_%900",
        "index_model": "TG30cm",
        "index_model_mnhsfx16pts" : None,
        "title": "Température du sol à -30 cm",
        "unit": "°C"
    },
    "TG50cm": {
        "index_obs": "tpr_sol50cm_f2_tn1_valid_%900",
        "index_model": "TG50cm",
        "index_model_mnhsfx16pts" : None,
        "title": "Température du sol à -50 cm",
        "unit": "°C"
    },
    "TG70cm": {
        "index_obs": "tpr_sol70cm_f2_tn1_valid_%900",
        "index_model": "TG70cm",
        "index_model_mnhsfx16pts" : None,
        "title": "Température du sol à -70 cm",
        "unit": "°C"
    },
    "TG100cm": {
        "index_obs": "tpr_sol100cm_f2_tn1_valid_%900",
        "index_model": "TG100cm",
        "index_model_mnhsfx16pts" : None,
        "title": "Température du sol à -1 m",
        "unit": "°C"
    },
    "WG1cm": {
        "index_obs": "",
        "index_model": 'WG1cm',
        #"index_model_mnhsfx16pts" : "WG1P1",
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -1 cm",
        "unit": "m³/m³"
    },
    "WG5cm": {
        "index_obs": "hum_sol5cm_f2_tpw1_Chs_%900",
        "index_model": 'WG5cm',
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -5 cm",
        "unit": "m³/m³"
    },
    "WG10cm": {
        "index_obs": "hum_sol10cm_f2_tpw1_Chs_%900",
        "index_model": 'WG10cm',
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -10 cm",
        "unit": "m³/m³"
    },
    "WG20cm": {
        "index_obs": "hum_sol20cm_f2_tpw1_Chs_%900",  
        "index_model": 'WG20cm',
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -20 cm",
        "unit": "m³/m³"
    },
    "WG30cm": {
        "index_obs": "hum_sol30cm_f2_tpw1_Chs_%900",
        "index_model": 'WG30cm',
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -30 cm",
        "unit": "m³/m³"
    },
    "WG50cm": {
        "index_obs": "hum_sol50cm_f2_tpw1_Chs_%900",
        "index_model": 'WG50cm',
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -50 cm",
        "unit": "m³/m³"
    },
    "WG70cm": {
        "index_obs": "hum_sol70cm_f2_tpw1_Chs_%900",
        "index_model": 'WG70cm',
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -70 cm",
        "unit": "m³/m³"
    },
    "WG100cm": {
        "index_obs": "hum_sol100cm_f2_tpw1_Chs_%900",
        "index_model": 'WG100cm',
        "index_model_mnhsfx16pts" : None,
        "title": "Humidité du sol à -1 m",
        "unit": "m³/m³"
    },
    "flx_mvt": {
        "index_obs": "flx_mvt_Chb_%1800",
        "index_model": "flx_mvt",
        "index_model_mnhsfx16pts" : None,
        "title": "Vitesse de friction",
        "unit": "m/s"
    },
    "tke": {
        "index_obs": "trb_ect_gill_tke_%1800",
        "index_model": "tke",
        "index_model_mnhsfx16pts" : "TKET",
        "title": "Energie cinétique turbulente",
        "unit": "m²/s²"
        },
    "cumul_RR": {
        "index_obs": "prp_rr_min_c2_%60_Som_%1800",
        "index_model": "cumul_RR",
        "index_model_mnhsfx16pts" : "ACPRR",
        "title": "Cumuls de pluie",
        "unit": "mm"
    },
    "altitude_CL": {
        "index_obs": "",
        "index_model": "altitude_CL",
        "index_model_mnhsfx16pts" : None,
        "title": "Altitude de la couche limite",
        "unit": "m"
    },
    "PV": {"index_obs_moy":"ray_power_pv_Eti_%900_Met_%3600",
        "index_obs_1": "ray_power_pv_Eti_%900",
        "index_obs_2": "ray_power_pv_LG_Eti_%1800",
        "index_obs_3": "ray_power_pv_Voltec_Eti_%1800",
        "index_cnr4":"",
        "index_bf5":"",
        "index_arome_J0": "ray_power_pv_estim_aromeJ0_00_%3600",
        "index_arome_J-1": "ray_power_pv_estim_aromeJ_1_12_%3600",
        "index_model_mnhsfx16pts" : None, 
        "title": "Puissance émise par les panneaux solaires ",
        "unit": "W/m²"
    },
    "RGD": {"index_obs_moy":"",
        "index_obs_1": "",
        "index_obs_2": "",
        "index_obs_3": "",
        "index_cnr4": "ray_rgd_cnr4_c7_Eti_%10",
        "index_bf5": "ray_rgd_bf5_c7_Eti_%10",
        "index_arome_J0": 'SWd',
        "index_arome_J-1": 'SWd',
        "index_model_mnhsfx16pts" : None, 
        "title": "Rayonnement global descendant ",
        "unit": "W/m²"
        },
    "RD": {"index_obs_moy":"",
        "index_obs_1": "",
        "index_obs_2": "",
        "index_obs_3": "",
        "index_cnr4": "",
        "index_bf5": "ray_rdiff_bf5_c7_Eti_%10",
        "index_arome_J0": "",
        "index_arome_J-1": "",
        "index_model_mnhsfx16pts" : None, 
        "title": "Rayonnement diffus ",
        "unit": "W/m²"
        },
    "INSO": {"index_obs_moy":"",
        "index_obs_1": "",
        "index_obs_2": "",
        "index_obs_3": "",
        "index_cnr4": "",
        "index_bf5": "ray_inso_bf5_c7_Eti_%10",
        "index_arome_J0": "",
        "index_arome_J-1": "",
        "index_model_mnhsfx16pts" : None, 
        "title": "Durée d'insolation ",
        "unit": "h"
        }
}

# Liste de toutes les variables qui sont tracées. Pour toute modification de cette liste,
# modifier VARIABLES en conséquence.
VARIABLES_PLOT = [
    "tmp_2m",
    "tmp_10m",
    "hum_rel",
    "vent_ff10m",
    "SWD",
    "SWU",
    "LWD",
    "LWU", 
    "flx_chaleur_sens",
    "flx_chaleur_lat",   
    "flx_chaleur_sol",
    "t_surface",
    "TG1cm",
    "WG1cm",
    "TG3cm",
    "WG5cm",
    "TG10cm",
    "WG10cm",
    "TG20cm",
    "WG20cm",
    "TG30cm",
    "WG30cm",
    "TG50cm",
    "WG50cm",
    "TG70cm",
    "WG70cm",
    "TG100cm",
    "WG100cm",
    "flx_mvt",
    "tke",
    "cumul_RR"]
#    "altitude_CL"]

# Liste des variables tracées pour la vue Panneaux Photovoltaiques
VARIABLES_PV_PLOT = ["PV", "RGD", "RD", "INSO"]

# Liste des variables tracées pour la vue Profils verticaux
VARIABLES_RS_PLOT = ["Température", "Humidité relative", "Vent"]

VARIABLES_RS = {"Température":
                    {
                        "label": "Température",
                        "unit": "°C"
                    },
                "Humidité relative":
                    {
                        "label": "Humidité relative",
                        "unit": "%"
                    },  # HR n'existe pas dans les obs AMDAR
                "Vent":
                    {
                        "label": "Vent",
                        "unit": "m/s"
                    }
                }
