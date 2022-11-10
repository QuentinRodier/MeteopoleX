#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:03:21 2021

@author: avrillauds
"""

import os
import sys

AH = os.getenv('AIDA_HOME', '/home/common/aida')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

# Définition acquid acquid=identifiant de la journee pour lecture donnée sous forme vecteur

def donnees(doy1, doy2, annee1, annee2, parametre, plateforme):

    acqid_fin = annee2[-2:] + f"{int(doy2):04}"
    acqid_debut = annee1[-2:] + f"{int(doy1):04}"

    # AIDA.read_datas fonction de lecture du module AIDA pour lire les données

    values, time, header = AIDA.read_datas(
        plateforme + acqid_debut, parametre, plateforme + acqid_fin)
    return [values, time, header]
