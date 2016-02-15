#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Carnet de vol parapente - Detection du decollage le plus proche du depart
# d'une trace et de l'atterrissage le plus proche de son arrivee
# Copyright (C) 2011 Pierre Knobel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from coord import Coord

def trouver_deco_atterro(trace_gps, conn_bdd):
    '''Chercher si la base de donnees a un decollage dans un rayon de 100 m
    du point de depart et un atterrissage dans un rayon de 100 m du point
    d'arrivee de la trace GPS.

    Le format de la trace GPS doit etre une liste d'objets de type Coord()
    '''

    cur = conn_bdd.cursor()
    
    dist_deco_le_plus_proche = 99999
    deco_proche = None
    
    cur.execute('''SELECT * from decos order by deco''')
    liste_decos_bdd = cur.fetchall()

    # Chercher le deco le plus proche du depart de la trace GPS
    for deco in liste_decos_bdd:
        # Verifier que la latitude et la longitude sont enregistrees dans la
        # base de donnees
        try:
            float(deco[2])
            float(deco[3])
        # sinon, passer au decollage suivant
        except:
            continue
        
        coord_deco = Coord(deco[2], deco[3])
        dist_deco = coord_deco.distance_to(trace_gps[0])
        if dist_deco <= dist_deco_le_plus_proche :
            deco_proche = deco[1]
            dist_deco_le_plus_proche = dist_deco
        
    dist_atterro_le_plus_proche = 99999
    atterro_proche = None
    
    cur.execute('''SELECT * from atterros order by atterro''')
    liste_atterros_bdd = cur.fetchall()

    # Chercher l'atterro le plus proche de l'arrive de la trace GPS
    for atterro in liste_atterros_bdd:
        # Verifier que la latitude et la longitude sont enregistrees dans la
        # base de donnees
        try:
            float(atterro[2])
            float(atterro[3])
        # sinon, passer a l'atterro suivant
        except:
            continue
        
        coord_atterro = Coord(atterro[2], atterro[3])
        dist_atterro = coord_atterro.distance_to(trace_gps[-1])
        if dist_atterro <= dist_atterro_le_plus_proche :
            atterro_proche = atterro[1]
            dist_atterro_le_plus_proche = dist_atterro

    # Verifier que le deco le plus proche est a moins de 100 m
    if not dist_deco_le_plus_proche < 100:
        deco_proche = None
    # Verifier que l'atterro le plus proche est a moins de 150 m
    if not dist_atterro_le_plus_proche < 150:
        atterro_proche = None

    return (deco_proche, atterro_proche)
