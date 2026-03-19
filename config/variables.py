#!/usr/bin/env python3

# Ce dictionnaire rassemble les spécificités de chaque paramètres tracés. Les 2 premiers 'index' sont les noms donnés sur AIDA au paramètre en question, dans les observations et dans les modèles.
 #!# Ajout enveloppe Le 'index_modl_arome' est le dico de la nouvelle recuperation AROME.
# Le 'title' est le titre du graph qui sera affiché, donc c'est l'utilisateur qui choisi, idem pour le unit, c'est à l'utilisateur de rentrer les bonnes unités.
VARIABLES = {
    "tmp_2m": {
        "index_obs": "tpr_air_bs_c1_%60_Met_%1800",
        #"index_model": "tpr_air2m",
        #"index_model_arome" : "t2m", 
        "index_model_surfex": "T2M_NAT",
        "index_model": "tmp_2m",
        "title": "Température à 2m",
        "unit": "°C"
    },
    "tmp_10m": {
        "index_obs": "tpr_air_ht_c1_%60_Met_%1800",
        #"index_model": "tpr_air10m",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": "tmp_10m",
        "title": "Température à 10m",
        "unit": "°C"
    },
    "hum_rel": {
        "index_obs": "hum_relcapa_bs_c1_%60_Met_%1800",
        #"index_model": "hum_rel",
        #"index_model_arome": "hu2m",
        "index_model_surfex": "HU2M", 
        "index_model": "hum_rel",
        "title": "Humidité relative",
        "unit": "%"
    },
    "vent_ff10m": {
        "index_obs": "ven_ff_10mn_c1_UV_%1800",
        #"index_model": "ven_ff10m",
        #"index_model_arome": "Vamp10m", 
        "index_model_surfex": None,
        "index_model": "vent_ff10m",
        "title": "Vent moyen à 10m",
        "unit": "m/s"
    },
    "SWD": {
        "index_obs": "ray_rgd_cnr1_c2_%60_Met_%1800",
        #"index_model": "ray_rgd",
        #"index_model_arome" : "SWd",
        "index_model_surfex": "SWD", 
        "index_model": "SWD",
        "title": "Rayonnement global descendant (SW down)",
        "unit": "W/m²"
    },
    "SWU": {
        "index_obs": "ray_rgm_cnr1_c2_%60_Met_%1800",
        #"index_model": "ray_rgm",
        #"index_model_arome" : "SWu",
        "index_model_surfex": "SWU", 
        "index_model": "SWU",
        "title": "Rayonnement global montant (SW up)",
        "unit": "W/m²"
    },
    "LWD": {
        "index_obs": "ray_ird_cnr1_c2_%60_Met_%1800",
        #"index_model": "ray_ird",
        #"index_model_arome" : "LWd",
        "index_model_surfex": "LWD", 
        "index_model": "LWD",
        "title": "Rayonnement IR descendant (LW down)",
        "unit": "W/m²"
    },
    "LWU": {
        "index_obs": "ray_irm_cnr1_c2_%60_Met_%1800",
        #"index_model": "ray_irm",
        #"index_model_arome": "LWu", 
        "index_model_surfex": "LWU", 
        "index_model": "LWU",
        "title": "Rayonnement IR montant (LW up)",
        "unit": "W/m²"
    },    
    "flx_chaleur_sens": {
        "index_obs": "flx_hs_tson_Chb_%1800",
        #"index_model": "flx_hs",
        #"index_model_arome": "sfc_sens_flx",
        "index_model_surfex": "H",
        "index_model": "flx_chaleur_sens",
        "title": "Flux de chaleur sensible",
        "unit": "W/m²"
    },
    "flx_chaleur_lat": {
        "index_obs": "flx_le_Chb_%1800",
        #"index_model": "flx_le",
        #"index_model_arome": "sfc_lat_flx",
        "index_model_surfex": "LE",
        "index_model": "flx_chaleur_lat",
        "title": "Flux de chaleur latente",
        "unit": "W/m²"
    },    
    "flx_chaleur_sol": {
        "index_obs": "flx_phi0_moy_c2_%60",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": "flx_chaleur_sol",
        "title": "Flux de conduction dans le sol",
        "unit": "W/m²"
    },
    "t_surface": {
        "index_obs": "tpr_solIR_c1_%60",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": "t_surface",
        "title": "Température de surface",
        "unit": "°C"
    },
    "TG0_5cm": {
        "index_obs": "tpr_sol1cm_f2_tn1_valid_%900", 
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "t-1",
        "title": "Température du sol à -0.5 cm",
        "unit": "°C"
    },
    "TG2_5cm": {
        "index_obs": "tpr_sol3cm_f2_tn1_valid_%900", 
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "t_couche2",
        "title": "Température du sol à -2.5 cm",
        "unit": "°C"
    },
    "TG7cm": {
        "index_obs": "tpr_sol10cm_f2_tn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "TG7cm",
        "title": "Température du sol à -7 cm",
        "unit": "°C"
    },
    "TG15cm": {
        "index_obs": "tpr_sol20cm_f2_tn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "TG15cm",
        "title": "Température du sol à -15 cm",
        "unit": "°C"
    },
    "TG30cm": {
        "index_obs": "tpr_sol30cm_f2_tn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "TG30cm",
        "title": "Température du sol à -30 cm",
        "unit": "°C"
    },
    "TG50cm": {
        "index_obs": "tpr_sol50cm_f2_tn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "TG50cm",
        "title": "Température du sol à -50 cm",
        "unit": "°C"
    },
    "TG70cm": {
        "index_obs": "tpr_sol70cm_f2_tn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "TG70cm",
        "title": "Température du sol à -70 cm",
        "unit": "°C"
    },
    "TG90cm": {
        "index_obs": "tpr_sol90cm_f2_tn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None, 
        "index_model_surfex": None,
        "index_model": "TG90cm",
        "title": "Température du sol à -90 cm",
        "unit": "°C"
    },
    "WG0_5cm": {
        "index_obs": "",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'hu_couche1',
        "title": "Humidité du sol à -0.5 cm",
        "unit": "kg/kg"
    },
    "WG2_5cm": {
        "index_obs": "hum_sol5cm_f2_tpn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'hu_couche2',
        "title": "Humidité du sol à -2.5 cm",
        "unit": "kg/kg"
    },
    "WG7cm": {
        "index_obs": "hum_sol10cm_f2_tpn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'hu_couche3',
        "title": "Humidité du sol à -7 cm",
        "unit": "kg/kg"
    },
    "WG15cm": {
        "index_obs": "hum_sol20cm_f2_tpn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'WG15cm',
        "title": "Humidité du sol à -15 cm",
        "unit": "kg/kg"
    },
    "WG30cm": {
        "index_obs": "hum_sol30cm_f2_tpn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'WG30cm',
        "title": "Humidité du sol à -30 cm",
        "unit": "kg/kg"
    },
    "WG50cm": {
        "index_obs": "hum_sol50cm_f2_tpn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'WG50cm',
        "title": "Humidité du sol à -50 cm",
        "unit": "kg/kg"
    },
    "WG70cm": {
        "index_obs": "hum_sol70cm_f2_tpn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'WG70cm',
        "title": "Humidité du sol à -70 cm",
        "unit": "kg/kg"
    },
    "WG90cm": {
        "index_obs": "hum_sol100cm_f2_tpn1_valid_%900",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": 'WG90cm',
        "title": "Humidité du sol à -90 cm",
        "unit": "kg/kg"
    },
    "flx_mvt": {
        "index_obs": "flx_mvt_Chb_%1800",
        #"index_model": "flx_mvt",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": "flx_mvt",
        "title": "Vitesse de friction",
        "unit": "m/s"
    },
    "tke": {
        "index_obs": "trb_ect_gill_tke_%1800",
        #"index_model": "",
        #"index_model_arome": "tke",
        "index_model_surfex": None,
        "index_model": "tke",
        "title": "Energie cinétique turbulente",
        "unit": "m²/s²"
        },
    "cumul_RR": {
        "index_obs": "prp_rr_min_c2_%60_Som_%1800",
        #"index_model": "",
        #"index_model_arome": None,
        "index_model_surfex": None,
        "index_model": "cumul_RR",
        "title": "Cumuls de pluie (Obs: 30mn, ARO-ARP: 1h, MNH: 15mn)",
        "unit": "mm"
    },
    "altitude_CL": {
        "index_obs": "",
        #"index_model": "",
        #"index_model_arome": "pblh",
        "index_model_surfex": None,
        "index_model": "altitude_CL",
        "title": "Altitude de la couche limite",
        "unit": "m"
    },
    "flx_chaleur_sens_cum": {
        "index_obs": None,
        #"index_model": None,
        #"index_model_arome": None,
        "index_model_surfex": "HC",
        "index_model": "flx_chaleur_sens_cum",   
        "title": "Flux de chaleur sensible cumulé",
        "unit": "J/m²"
    },
    "flx_chaleur_lat_cum": {
        "index_obs": None,
        #"index_model": None,
        #"index_model_arome": None,
        "index_model_surfex": "LEC",  
        "index_model": "flx_chaleur_lat_cum",
        "title": "Flux de chaleur latente cumulé",
        "unit": "J/m²"
    },
    "SWD_cum": {
        "index_obs": None,
        #"index_model": None,
        #"index_model_arome": None,
        "index_model_surfex": "SWDC",  
        "index_model": "SWD_cum",
        "title": "Rayonnement SW descendant cumulé",
        "unit": "J/m²"
    },
    "SWU_cum": {
        "index_obs": None,
        #"index_model": None,
        #"index_model_arome": None,
        "index_model_surfex": "SWUC", 
        "index_model": "SWU_cum", 
        "title": "Rayonnement SW montant cumulé",
        "unit": "J/m²"
    },
    "LWD_cum": {
        "index_obs": None,
        #"index_model": None,
        #"index_model_arome": None,
        "index_model_surfex": "LWDC", 
        "index_model": "LWD_cum", 
        "title": "Rayonnement LW descendant cumulé",
        "unit": "J/m²"
    },
    "LWU_cum": {
        "index_obs": None,
        #"index_model": None,
        #"index_model_arome": None,
        "index_model_surfex": "LWUC",  
        "index_model": "LWU_cum",
        "title": "Rayonnement LW montant cumulé",
        "unit": "J/m²"
    },
}

'''    "PV": {"index_obs_moy":"ray_power_pv_Eti_%900_Met_%3600",
        "index_obs_1": "ray_power_pv_Eti_%900",
        "index_obs_2": "ray_power_pv_LG_Eti_%1800",
        "index_obs_3": "ray_power_pv_Voltec_Eti_%1800",
        "index_cnr4":"",
        "index_bf5":"",
        "index_arome_J0": "ray_power_pv_estim_aromeJ0_00_%3600",
        "index_arome_J-1": "ray_power_pv_estim_aromeJ_1_12_%3600",
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
        "title": "Durée d'insolation ",
        "unit": "h"
        }'''

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
    "TG0_5cm",
    "TG2_5cm",
    "TG7cm",
    "TG15cm",
    "TG30cm",
    "TG50cm",
    "TG70cm",
    "TG90cm",
    "WG0_5cm",
    "WG2_5cm",
    "WG7cm",
    "WG15cm",
    "WG30cm",
    "WG50cm",
    "WG70cm",
    "WG90cm",
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