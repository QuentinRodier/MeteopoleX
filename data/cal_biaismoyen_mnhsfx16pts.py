#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  19 08:35:41 2026
@author: Renaud Lestringant
"""

import numpy as np

from config.models import POINTS_mnhsfx16pts

def cal_bm(biais_mnhsfx16pts):

   Npts = len(POINTS_mnhsfx16pts)
   point = POINTS_mnhsfx16pts[0]  
   ndays = biais_mnhsfx16pts[point]['ndays']

   bm = {}
   for n in range(Npts):
     point = POINTS_mnhsfx16pts[n]  
     V = biais_mnhsfx16pts[point]['values']
     mean_V = np.nanmean(V.reshape(ndays,-1) , axis=0)
     bm[point] = {}
     bm[point]['values'] = mean_V[1::2]
     bm[point]['time']   = np.arange(1,24+1)
     if n == 0:
       name_histo = "hourly_histo"
       bm[name_histo] = {}
       sum_notNaN =  np.sum(~np.isnan(V.reshape(ndays,-1)) ,axis=0)
       bm[name_histo]['values'] = 100 * sum_notNaN[1::2] / ndays
       bm[name_histo]['time']   = np.arange(1,24+1)
       bm[name_histo]['ndays']  = ndays

   return bm
