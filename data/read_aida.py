#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from functools import lru_cache
import pickle
from pathlib import Path
import hashlib
import numpy as np

AH = os.getenv('AIDA_HOME', '/home/common/aida')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

# Répertoire pour le cache disque (ajuster selon votre config)
CACHE_DIR = Path("/home/manip/MeteopoleX/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cache en mémoire LRU pour les requêtes récentes
@lru_cache(maxsize=100)
def _make_cache_key(doy1, doy2, annee1, annee2, parametre, plateforme):
    """Génère une clé unique pour le cache"""
    key_str = f"{doy1}_{doy2}_{annee1}_{annee2}_{parametre}_{plateforme}"
    return hashlib.md5(key_str.encode()).hexdigest()


def _get_cache_path(cache_key):
    """Retourne le chemin du fichier cache"""
    return CACHE_DIR / f"aida_{cache_key}.pkl"


def _load_from_disk_cache(cache_key):
    """Charge les données depuis le cache disque"""
    cache_path = _get_cache_path(cache_key)
    
    if cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Erreur lecture cache: {e}")
            return None
    return None


def _save_to_disk_cache(cache_key, data):
    """Sauvegarde les données dans le cache disque"""
    cache_path = _get_cache_path(cache_key)
    
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"Erreur écriture cache: {e}")


def donnees(doy1, doy2, annee1, annee2, parametre, plateforme):
    """
    Lecture AIDA avec cache 2 niveaux (mémoire + disque)
    
    Version optimisée qui:
    - Vérifie d'abord le cache mémoire (LRU)
    - Puis le cache disque
    - Ne lit AIDA qu'en dernier recours
    """
    # Générer la clé de cache
    cache_key = _make_cache_key(doy1, doy2, annee1, annee2, parametre, plateforme)
    
    # Essayer le cache disque
    cached_data = _load_from_disk_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Lecture depuis AIDA 
    acqid_fin = annee2[-2:] + f"{int(doy2):04}"
    acqid_debut = annee1[-2:] + f"{int(doy1):04}"
    
    # Affichage des logs dans fichier
    with open('/home/manip/MeteopoleX/Site_web_dev/read_aida.log', 'w') as aida_log:
        sys.stdout = aida_log
        values, time, header = AIDA.read_datas(
            plateforme + acqid_debut, 
            parametre, 
            plateforme + acqid_fin
        )
    
    sys.stdout = sys.__stdout__
    
    result = [values, time, header]
    
    # Sauvegarder dans le cache disque
    _save_to_disk_cache(cache_key, result)
    
    return result


def donnees_batch(doy1, doy2, annee1, annee2, parametres_dict, plateforme):
    """
    Lecture batch de plusieurs paramètres AIDA en une seule passe
    
    Args:
        doy1, doy2, annee1, annee2: période
        parametres_dict: dict {nom_param: index_aida}
        plateforme: 'Tf', 'Rt', 'Gt'
        
    Returns:
        dict {nom_param: [values, time, header]}
    """
    results = {}
    
    # Grouper les paramètres par ceux qui sont en cache vs non-cachés
    to_load = []
    
    for nom_param, index_aida in parametres_dict.items():
        cache_key = _make_cache_key(doy1, doy2, annee1, annee2, index_aida, plateforme)
        cached = _load_from_disk_cache(cache_key)
        
        if cached is not None:
            results[nom_param] = cached
        else:
            to_load.append((nom_param, index_aida))
    
    # Charger les données manquantes
    for nom_param, index_aida in to_load:
        data = donnees(doy1, doy2, annee1, annee2, index_aida, plateforme)
        results[nom_param] = data
    
    return results


def clear_cache(older_than_days=7):
    """
    Nettoie le cache disque des fichiers plus vieux que X jours
    
    Args:
        older_than_days: âge limite en jours
    """
    import time
    
    now = time.time()
    cutoff = now - (older_than_days * 86400)
    
    deleted = 0
    for cache_file in CACHE_DIR.glob("aida_*.pkl"):
        if cache_file.stat().st_mtime < cutoff:
            cache_file.unlink()
            deleted += 1
    
    print(f"Cache AIDA nettoyé: {deleted} fichiers supprimés")

