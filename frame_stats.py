#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Carnet de vol parapente - Affichage des statistiques sur les vols
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


# A faire :
# ajouter graphiques annuels (duree, duree moyenne, vitesse moyenne, nombre de vols, classement CFD)
import datetime
import os
import sys
from tkinter.tix import *
from tkinter import messagebox
from tkinter import filedialog

from divers import cumul, list_days_since_origin, days_since_origin, date_annotations
  
prog_path = os.path.dirname(sys.argv[0])
images_path = os.path.join(prog_path, "images")

bgc = "#e3e3fa"

# Marges en pixels autour des graphiques
m = 50

class FrameStats(Frame):
    '''Statistiques extraites du carnet de vol       
    '''
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        
        self.db_connected = False       
        self.conn = None
        self.cur = None

        # Annee
        self.annee = StringVar()

        # Nombre de vol
        self.nvols = StringVar()
        # Temps de vol format HHhMM
        self.tvol = StringVar()
        # Temps moyen par vol (minutes)
        self.tvol_moy = StringVar()
        # Distance sur parcours declares
        self.d_parcours = StringVar()
        # Distance moyenne par vol
        self.d_parcours_moy = StringVar()
        # Vitesse moyenne sur parcours de cross
        self.v_parcours = StringVar()
        # Vitesse / sol moyenne
        self.v_gps = StringVar()
        # Vitesse moyenne sur parcours de cross
        self.v_parcours = StringVar()

        f0 = Frame(self, bd=3)

        # Menu deroulant pour selection de l'annee
        self.cb_annee = ComboBox(f0, label="Année", dropdown=1, editable=0,
                                 bg="white", variable=self.annee, listwidth=30,
                                 command=self.stats_vols)
        self.cb_annee.entry.config(width=8, bg='white')
        self.cb_annee.pack(side='top')
        #self.cb_annee.grid(column=0, row=0, sticky="W")
        
        # premiere frame a gauche spour l'affichage de statistiques
        f1 = Frame(f0, bd=3, relief="groove", bg = bgc)
        
        l = Label(f1, text="Nombre de vols :", bg = bgc)
        l.grid(column=0, row=0, sticky="W")
        
        Label(f1, textvariable=self.nvols, bg = bgc).grid(column=1, row=0,
                                                          sticky="W")

        Label(f1, text="Temps de vol cumulé :", bg = bgc).grid(column=0,
                                                                row=2,
                                                                sticky="W")
        Label(f1, textvariable=self.tvol, bg = bgc).grid(column=1,
                                                         row=2, sticky="W")        

        Label(f1, text="Durée moyenne :", bg = bgc).grid(column=0, row=3,
                                                         sticky="W")
        Label(f1, textvariable=self.tvol_moy, bg = bgc).grid (column=1, row=3,
                                                              sticky="W")   

        Label(f1, text="Distance cross\ncumulée :", bg = bgc).grid(column=0,
                                                                   row=4,
                                                                   sticky="W")
        Label(f1, textvariable=self.d_parcours, bg = bgc).grid(column=1, row=4,
                                                               sticky="W")

        l = Label(f1, text="Distance moyenne\npar cross :", bg = bgc)
        l.grid(column=0, row=5, sticky="W") 
        Label(f1, textvariable=self.d_parcours_moy, bg = bgc).grid(column=1,
                                                                   row=5,
                                                                   sticky="W")
        
        l = Label(f1, text="Vitesse moyenne\n sur parcours :", bg = bgc)
        l.grid(column=0, row=6, sticky="W")
        Label(f1, textvariable=self.v_parcours, bg = bgc).grid(column=1,
                                                                row=6,
                                                                sticky="W")
        
        l= Label(f1, text="Vitesse moyenne\nau GPS :", bg = bgc)
        l.grid (column=0, row=7, sticky="W")
        Label(f1, textvariable=self.v_gps, bg = bgc).grid(column=1, row=7,
                                                          sticky="W")
        
        
        #f1.grid(column=0, row=1)
        
        f1.pack(expand=1, fill=tkinter.tix.BOTH)

        f1.columnconfigure(0, pad=10)
        f1.columnconfigure(1, pad=10)
        f1.rowconfigure(0, pad=20)
        f1.rowconfigure(1, pad=20)
        f1.rowconfigure(2, pad=20)
        f1.rowconfigure(3, pad=20)
        f1.rowconfigure(4, pad=20)
        f1.rowconfigure(5, pad=20)
        f1.rowconfigure(6, pad=20)
        f1.rowconfigure(7, pad=20)

        f0.pack(side="left", expand=0, fill=tkinter.tix.BOTH)
        
        # deuxieme frame a gauche pour l'affichage de graphiques
        f2 = Frame(self, bd=3, relief="groove")
        
        self.type_graph = StringVar()
        self.cb_graph = ComboBox(f2, label="Type de graphique", dropdown=1,
                                 editable=0, bg="white", listwidth=250,
                                 variable=self.type_graph, 
                                 command=self.affiche_graph)
        self.cb_graph.slistbox.listbox.config(height=13)
        self.cb_graph.entry.config(width=30)
        
        self.cb_graph.pack(side="top")

        self.cb_graph.insert('end', "Cumul de temps de vol")
        self.cb_graph.insert('end', "Temps de vol")
        self.cb_graph.insert('end', "Temps de vol par mois")
        self.cb_graph.insert('end', "Temps de vol total annuel")
        self.cb_graph.insert('end', "Temps de vol moyen et max annuel")
        self.cb_graph.insert('end', "Cumul de distance")
        self.cb_graph.insert('end', "Distance")
        self.cb_graph.insert('end', "Distance moyenne et max annuelle")
        self.cb_graph.insert('end', "Cumul du nombre de vols")
        self.cb_graph.insert('end', "Nombre de vols par mois")
        self.cb_graph.insert('end', "Nombre de vols par an")
        self.cb_graph.insert('end', "Types de vols")
        self.cb_graph.insert('end', "Types de vols par temps de vol")
        self.cb_graph.insert('end', "Encadrement")
        self.cb_graph.insert('end', "Encadrement par temps de vol")

        h = len(self.cb_graph.slistbox.listbox.get(0, END))
        self.cb_graph.slistbox.listbox.config(height=h)
        
        self.canv = Canvas(f2, bg = bgc)
        self.canv.pack(expand=1, fill=tkinter.tix.BOTH, side="bottom")

        # Get canvas width and height
        self.canv.bind("<Configure>", self.resize_graph)
        
        self.w = self.canv.winfo_width()
        self.h = self.canv.winfo_height()

        f2.pack(expand=1, fill=tkinter.tix.BOTH, side="right")
        
        self.columnconfigure(0, pad=4)
        self.columnconfigure(1, pad=4, weight=2)
        self.rowconfigure(0, pad=4)
        self.rowconfigure(1, pad=4, weight=2)

    def on_pilot_selection(self, conn):
        '''Fonction executee lorsqu'un pilote est selectionne

         Chargement des informations a partir de sa base de donnees'''

        self.db_connected = True
        self.conn = conn
        self.cur = self.conn.cursor()

        self.fill_cb_annees()
        self.stats_vols()

    def fill_cb_annees(self):
        '''Recuperer les annees des vols et les ajouter a la liste deroulante
        '''
        if not self.db_connected:
            return
        self.cur.execute("SELECT DISTINCT annee FROM vols ORDER BY annee DESC")
        liste_annees = [str(a[0]) for a in self.cur.fetchall()]

        self.cb_annee.slistbox.listbox.delete(0, 'end')
        for annee in liste_annees:
            self.cb_annee.insert(tkinter.tix.END, annee)
        self.cb_annee.insert(tkinter.tix.END, "Toutes")

        self.annee.set("Toutes")

    def stats_vols(self, *args):
        '''calculer les statistiques de vol
        '''
        if not self.db_connected:
            return
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())

        # Nombre vols
        if not annee:
            req = 'SELECT count(*) FROM vols WHERE NOT type_vol = "Gonflage"'
            self.cur.execute(req)
        else:
            req = '''SELECT count(*) FROM vols
                  WHERE NOT type_vol = "Gonflage"
                  AND annee = ?'''
            self.cur.execute(req, (annee, ))         
        self.nvols.set(str(self.cur.fetchall()[0][0]))
        
        # Duree cumulee
        if not annee:
            req = 'SELECT SUM(duree) FROM vols WHERE NOT type_vol = "Gonflage"'
            self.cur.execute(req)
        else:
            req = '''SELECT SUM(duree) FROM vols
                  WHERE NOT type_vol = "Gonflage"
                  AND annee = ?'''
            self.cur.execute(req, (annee, ))
        tvol_min = self.cur.fetchall()[0][0]
        if tvol_min is not None:
            tvol_str = "%02d h %02d min" % (tvol_min // 60, tvol_min % 60)
        else:
            tvol_str =  ''
        self.tvol.set(tvol_str)     

        # Duree moyenne
        if not annee:
            req = 'SELECT AVG(duree) FROM vols WHERE NOT type_vol = "Gonflage"'
            self.cur.execute(req)
        else:
            req = '''SELECT AVG(duree) FROM vols
                  WHERE NOT type_vol = "Gonflage"
                  AND annee = ?'''
            self.cur.execute(req, (annee, ))
        tvol_moy = self.cur.fetchall()[0][0] 
        if tvol_moy is not None:
            tvol_str = "%02d min" % (int(tvol_moy))
        else:
            tvol_str = ''
        self.tvol_moy.set(tvol_str)

        # Distance cross cumulee
        if not annee:
            req = '''SELECT SUM(distance_parcours) FROM vols
                  WHERE NOT distance_parcours = 0'''
            self.cur.execute(req)
        else:
            req = '''SELECT SUM(distance_parcours) FROM vols
                  WHERE NOT distance_parcours = 0
                  AND annee = ?'''
            self.cur.execute(req, (annee, ))
        d_parcours = self.cur.fetchall()[0][0]
        if d_parcours is not None:
            dist_str = str(d_parcours) + " km"
        else:
            dist_str = ''
        self.d_parcours.set(dist_str)      

        # Distance cross moyenne
        if not annee:
            req = '''SELECT AVG(distance_parcours) FROM vols
                  WHERE NOT distance_parcours = 0'''
            self.cur.execute(req)
        else:
            req = '''SELECT AVG(distance_parcours) FROM vols
                  WHERE NOT distance_parcours = 0
                  AND annee = ?'''
            self.cur.execute(req, (annee, ))
        d_parcours_moy = self.cur.fetchall()[0][0]
        if d_parcours_moy is not None:
            dist_str = "%d km" % (d_parcours_moy)
        else:
            dist_str = ''
        self.d_parcours_moy.set(dist_str)

        # Vitesse cross moyenne
        if not annee:
            req = '''SELECT CAST(SUM(distance_parcours) as real) / SUM(duree) * 60
                  FROM vols
                  WHERE NOT distance_parcours = 0
                  AND NOT duree = 0'''
            self.cur.execute(req)
        else:
            req = '''SELECT CAST(SUM(distance_parcours) as real) / SUM(duree) * 60
                  FROM vols
                  WHERE NOT distance_parcours = 0
                  AND NOT duree = 0
                  AND annee = ?'''
            self.cur.execute(req, (annee, ))
        v_parcours = self.cur.fetchall()[0][0]
        if v_parcours is not None:
            v_str = "%.2f km/h" % (v_parcours)
        else:
            v_str = ''
        self.v_parcours.set(v_str)       
        
        # Vitesse gps moyenne
        if not annee:
            req = '''SELECT CAST(SUM(distance_totale) as real) / SUM(duree) * 60
                  FROM vols
                  WHERE NOT distance_totale = 0
                  AND NOT duree = 0'''
            self.cur.execute(req)
        else:
            req = '''SELECT CAST(SUM(distance_totale) as real) / SUM(duree) * 60
                  FROM vols
                  WHERE NOT distance_totale = 0
                  AND NOT duree = 0
                  AND annee = ?'''
            self.cur.execute(req, (annee, ))
        v_gps = self.cur.fetchall()[0][0]
        if v_gps is not None:
            v_str = "%.2f km/h" % (v_gps)
        else:
            v_str = ''
        self.v_gps.set(v_str)
        
        # Remise a jour du graphique apres avoir change d'annee
        self.affiche_graph()

    def resize_graph(self, event):
        '''Fonction executee lors du redimensionnement de la fenetre.
        Mise a jour de la hauteur et largeur du canvas et de l'affichage.
        '''
        self.w = event.width
        self.h = event.height
        self.affiche_graph()

    def affiche_graph(self, *args):
        '''Fonction invoquee lors de la selection d'un type de graphique
        ainsi que lors du redimensionnement de la fenetre.'''
        if not self.db_connected:
            return
        if self.type_graph.get() == "Cumul de temps de vol":
            self.affiche_cumul_tvol()
        elif self.type_graph.get() == "Temps de vol":
            self.affiche_tvol()
        elif self.type_graph.get() == "Temps de vol par mois":
            self.affiche_tvol_par_mois()
        elif self.type_graph.get() == "Temps de vol total annuel":
            self.affiche_duree_totale_annuelle()
        elif self.type_graph.get() == "Temps de vol moyen et max annuel":
            self.affiche_duree_max_moy_annuelle()
        elif self.type_graph.get() == "Cumul de distance":
            self.affiche_cumul_distance()
        elif self.type_graph.get() == "Distance moyenne et max annuelle":
            self.affiche_distance_annuelle()
        elif self.type_graph.get() == "Distance":
            self.affiche_distance()
        elif self.type_graph.get() == "Cumul du nombre de vols":
            self.affiche_cumul_nvols()
        elif self.type_graph.get() == "Nombre de vols par mois":
            self.affiche_nvols_par_mois()
        elif self.type_graph.get() == "Nombre de vols par an":
            self.affiche_nvols_annuel()
        elif self.type_graph.get() == "Types de vols":
            self.affiche_repartition_type_vol()
        elif self.type_graph.get() == "Types de vols par temps de vol":
            self.affiche_repartition_type_vol_temps()
        elif self.type_graph.get() == "Encadrement":
            self.affiche_repartition_encadrement()
        elif self.type_graph.get() == "Encadrement par temps de vol":
            self.affiche_repartition_encadrement_temps()


    def affiche_cumul_tvol(self, *args):
        '''Recupere les valeurs necessaires pour l'affichage de la courbe de
        cumul de temps de vol puis appelle la fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT annee, mois, jour, duree FROM vols
                  WHERE NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour'''      
            self.cur.execute(req)
        else:
            req = '''SELECT annee, mois, jour, duree FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        l_dates = [datetime.date(v[0], v[1], v[2]) for v in l_vols]
        min_date, max_date = (min(l_dates), max(l_dates))
        l_jours = list_days_since_origin(l_dates, origin = min_date)

        # annotation de l'axe des abscissses : 1er de chaque mois
        # les annotations sont des chaines de caracteres stockees dans un dico 
        # indexe par la position en x
        annot1_x, annot2_x = date_annotations(l_dates)
                    
        l_tvol = [v[3] for v in l_vols]
        l_cumul_tvol = cumul(l_tvol)

        self.affiche_cumul(l_jours, l_cumul_tvol, labels1_x = annot1_x,
                           labels2_x = annot2_x, xlegend = "Date",
                           ylegend = "Temps de vol (min)")

    def affiche_tvol(self, *args):
        '''Recupere les valeurs necessaires pour l'affichage de la courbe de
        temps de vol puis appelle la fonction d'affichage'''     
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT annee, mois, jour, duree FROM vols
                  WHERE NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour'''      
            self.cur.execute(req)
        else:
            req = '''SELECT annee, mois, jour, duree FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        l_dates = [datetime.date(v[0], v[1], v[2]) for v in l_vols]
        l_jours = list_days_since_origin(l_dates)
                        
        annot1_x, annot2_x = date_annotations(l_dates)

        l_tvol = [v[3] for v in l_vols]

        self.affiche_points(l_jours, l_tvol, labels1_x = annot1_x,
                            labels2_x = annot2_x, xlegend = "Date",
                            ylegend = "Temps de vol (min)")
        
    def affiche_cumul_distance(self, *args):
        '''Recupere les valeurs necessaires pour l'affichage de la courbe de
        cumul de distance en cross puis appelle la fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT annee, mois, jour, distance_parcours FROM vols
                  WHERE NOT distance_parcours = 0
                  ORDER BY annee, mois, jour'''      
            self.cur.execute(req)
        else:
            req = '''SELECT annee, mois, jour, distance_parcours FROM vols
                  WHERE annee = ?
                  AND NOT distance_parcours = 0
                  ORDER BY annee, mois, jour
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        l_dates = [datetime.date(v[0], v[1], v[2]) for v in l_vols]
        l_jours = list_days_since_origin(l_dates)

        annot1_x, annot2_x = date_annotations(l_dates)

        l_dist = [v[3] for v in l_vols]
        l_cumul_dist = cumul(l_dist)

        self.affiche_cumul(l_jours, l_cumul_dist, labels1_x = annot1_x,
                           labels2_x = annot2_x , xlegend = "Date",
                           ylegend = "Distance (km)")

    def affiche_distance(self, *args):
        '''Recupere les valeurs necessaires pour l'affichage des distances
        puis appelle la fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT annee, mois, jour, distance_parcours FROM vols
                  WHERE NOT distance_parcours = 0
                  ORDER BY annee, mois, jour'''      
            self.cur.execute(req)
        else:
            req = '''SELECT annee, mois, jour, distance_parcours FROM vols
                  WHERE annee = ?
                  AND NOT distance_parcours = 0
                  ORDER BY annee, mois, jour
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        l_dates = [datetime.date(v[0], v[1], v[2]) for v in l_vols]
        l_jours = list_days_since_origin(l_dates)

        annot1_x, annot2_x = date_annotations(l_dates)

        l_dist = [v[3] for v in l_vols]

        self.affiche_points(l_jours, l_dist, labels1_x = annot1_x,
                            labels2_x = annot2_x, xlegend = "Date",
                            ylegend = "Distance (km)")

    def affiche_cumul_nvols(self, *args):
        '''Recupere les valeurs necessaires pour l'affichage de la courbe de
        cumul de temps de vol puis appelle la fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT annee, mois, jour FROM vols
                  WHERE NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour'''      
            self.cur.execute(req)
        else:
            req = '''SELECT annee, mois, jour FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        l_dates = [datetime.date(v[0], v[1], v[2]) for v in l_vols]
        l_jours = list_days_since_origin(l_dates)

        annot1_x, annot2_x = date_annotations(l_dates)

        l_cumul_nvols = cumul([1 for v in l_vols])

        self.affiche_cumul(l_jours, l_cumul_nvols, labels1_x = annot1_x,
                           labels2_x = annot2_x, xlegend = "Dates",
                           ylegend = "Nombre de vols")


    def affiche_repartition_type_vol(self):
        '''Recupere les valeurs necessaires pour l'affichage du camembert de
        de repartition des types de vol puis appelle la fonction d'affichage'''     
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT type_vol FROM vols'''      
            self.cur.execute(req)
        else:
            req = '''SELECT type_vol  FROM vols
                  WHERE annee = ?
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = [v[0] for v in self.cur.fetchall()]

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        # types vol
        liste_tv = ["Plouf", "Vol thermique sur site", "Cross", "Vol rando",
               "Gonflage", "Soaring", "Rando & cross", "SIV", "Treuil",
               "Voltige", "Vol à ski", "Speedriding", "Compétition"]

        repartition_tv = {}
        
        for v in l_vols:
            for tv in liste_tv:
                if v == tv:
                    if not v  in repartition_tv:
                        repartition_tv[v] = 1
                    else:
                        repartition_tv[v] += 1       

        self.affiche_camembert(repartition_tv)
   
    def affiche_repartition_type_vol_temps(self):
        '''Recupere les valeurs necessaires pour l'affichage du camembert de
        de repartition des types de vol par temps de vol puis appelle la
        fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT type_vol, duree FROM vols'''      
            self.cur.execute(req)
        else:
            req = '''SELECT type_vol, duree  FROM vols
                  WHERE annee = ?
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        # types vol
        liste_tv = ["Plouf", "Vol thermique sur site", "Cross", "Vol rando",
               "Gonflage", "Soaring", "Rando & cross", "SIV", "Treuil",
               "Voltige", "Vol à ski", "Speedriding", "Compétition"]

        repartition_tv = {}
        
        for v in l_vols:
            for tv in liste_tv:
                if v[0] == tv:
                    if not tv in repartition_tv:
                        repartition_tv[tv] = v[1]
                    else:
                        repartition_tv[tv] += v[1]       

        self.affiche_camembert(repartition_tv)
 
    def affiche_repartition_encadrement(self):
        '''Recupere les valeurs necessaires pour l'affichage du camembert de
        de repartition des types de vol puis appelle la fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT encadrement FROM vols'''      
            self.cur.execute(req)
        else:
            req = '''SELECT encadrement  FROM vols
                  WHERE annee = ?
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = [v[0] for v in self.cur.fetchall()]

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        # encadrements
        liste_encadrements = ['Autonome', 'Entre potes', 'Club', 'Ecole']
        repartition_enc = {}
        
        for v in l_vols:
            for enc in liste_encadrements:
                if v == enc:
                    if not enc in repartition_enc:
                        repartition_enc[enc] = 1
                    else:
                        repartition_enc[enc] += 1       

        self.affiche_camembert(repartition_enc)
   
    def affiche_repartition_encadrement_temps(self):
        '''Recupere les valeurs necessaires pour l'affichage du camembert de
        de repartition des types de vol par temps de vol puis appelle la
        fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT encadrement, duree FROM vols'''      
            self.cur.execute(req)
        else:
            req = '''SELECT encadrement, duree  FROM vols
                  WHERE annee = ?
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        # encadrements
        liste_encadrements = ['Autonome', 'Entre potes', 'Club', 'Ecole']
        repartition_enc = {}
        
        for v in l_vols:
            for enc in liste_encadrements:
                if v[0] == enc:
                    if not enc in repartition_enc:
                        repartition_enc[enc] = v[1]
                    else:
                        repartition_enc[enc] += v[1]       

        self.affiche_camembert(repartition_enc)

    def affiche_nvols_par_mois(self):
        '''Recupere les valeurs necessaires pour l'affichage de la courbe du
        nombre de  vols par mois puis appelle la fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT annee, mois, jour FROM vols
                  WHERE NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour'''      
            self.cur.execute(req)
        else:
            req = '''SELECT annee, mois, jour FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        l_dates = [datetime.date(v[0], v[1], v[2]) for v in l_vols]
        min_date, max_date = (min(l_dates), max(l_dates))

        n_mois = 0
        n_annee = 0
        l_mois = []
        l_nvols_par_mois = []
        l_dates = []
        annot1_x = {}
        annot2_x = {}
        
        for y in range(min_date.year, max_date.year + 1):
            annot2_x[n_mois] = "%d" % (y)
            for m in range(1, 13):                
                if min_date <= datetime.date(y, m, 28) and\
                   datetime.date(y, m, 1) <= max_date:
                    req = '''SELECT COUNT(*) FROM vols
                          WHERE annee = ?
                          AND mois = ?'''
                    self.cur.execute(req, (y, m))
                    l_nvols_par_mois.append(self.cur.fetchall()[0][0])
                    l_mois.append(n_mois)
                    l_dates.append(datetime.date(y, m, 1))
                    annot1_x[n_mois] = "%d" % (m)
                    n_mois += 1           
            n_annee += 1
                    
        self.affiche_histogramme(l_mois, l_nvols_par_mois, labels1_x = annot1_x,
                                 labels2_x = annot2_x, xlegend = "Mois",
                                 ylegend = "Nombre de vols par mois")
        
    def affiche_nvols_annuel(self):
        '''Recupere les valeurs necessaires pour l'affichage de l'histogramme
        du nombre de vols par an'''

        req = '''SELECT DISTINCT annee FROM vols
              WHERE NOT type_vol = "Gonflage"
              ORDER BY annee'''
        self.cur.execute(req)
        l_annees = [item[0] for item in self.cur.fetchall()]

        if len(l_annees) < 2:
            self.canv.delete("all")
            return       

        l_nvols_annee = []
        annot1_x = {}
        
        for annee in l_annees:
            req = '''SELECT COUNT(*)
                  FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage"'''      
            self.cur.execute(req, (annee, ))
            nvols = self.cur.fetchall()

            l_nvols_annee.append(nvols[0][0])
            annot1_x[annee] = "%d" % (annee)
                          
        self.affiche_histogramme(l_annees, l_nvols_annee,
                                 labels1_x = annot1_x, xlegend = "Années",
                                 ylegend = "Nombre de vols par an")
 
    def affiche_tvol_par_mois(self):
        '''Recupere les valeurs necessaires pour l'affichage de la courbe du
        temps de vol par mois puis appelle la fonction d'affichage'''
        if self.annee.get() == "Toutes":
            annee = 0
        else:
            annee = int(self.annee.get())
        if not annee:
            req = '''SELECT annee, mois, jour, duree FROM vols
                  WHERE NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour'''      
            self.cur.execute(req)
        else:
            req = '''SELECT annee, mois, jour, duree FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage" 
                  ORDER BY annee, mois, jour
                  '''      
            self.cur.execute(req, (annee,))
            
        l_vols = self.cur.fetchall()

        if len(l_vols) < 2:
            self.canv.delete("all")
            return

        l_dates = [datetime.date(v[0], v[1], v[2]) for v in l_vols]
        min_date, max_date = (min(l_dates), max(l_dates))

        n_mois = 0
        n_annee = 0
        l_mois = []
        l_tvol_par_mois = []
        l_dates = []
        annot1_x = {}
        annot2_x = {}
        
        for y in range(min_date.year, max_date.year + 1):
            annot2_x[n_mois] = "%d" % (y)
            for m in range(1, 13):                
                if min_date <= datetime.date(y, m, 28) and\
                   datetime.date(y, m, 1) <= max_date:
                    req = '''SELECT SUM(duree) FROM vols
                          WHERE annee = ?
                          AND mois = ?
                          AND NOT type_vol = "Gonflage"'''
                    self.cur.execute(req, (y, m))
                    t_vol = self.cur.fetchall()[0][0]
                    if t_vol is not None:
                        l_tvol_par_mois.append(t_vol)
                    else:
                        l_tvol_par_mois.append(0)
                    l_mois.append(n_mois)
                    l_dates.append(datetime.date(y, m, 1))
                    annot1_x[n_mois] = "%d" % (m)
                    n_mois += 1           
            n_annee += 1
            
        self.affiche_histogramme(l_mois, l_tvol_par_mois, labels1_x = annot1_x,
                                 labels2_x = annot2_x, xlegend = "Mois",
                                 ylegend = "Temps de vol par mois (min)")
        
    def affiche_distance_annuelle(self):
        '''Recupere les valeurs necessaires pour l'affichage de l'histogramme
        de la distance max et la distance moyenne annuelle'''

        req = '''SELECT DISTINCT annee FROM vols
              WHERE distance_parcours > 0
              ORDER BY annee'''
        self.cur.execute(req)
        l_annees = [item[0] for item in self.cur.fetchall()]

        if len(l_annees) < 2:
            self.canv.delete("all")
            return       

        l_dist_moy_annee = []
        l_dist_max_annee = []   
        annot1_x = {}
        
        for annee in l_annees:
            req = '''SELECT MAX(distance_parcours), AVG(distance_parcours)
                  FROM vols
                  WHERE annee = ?
                  AND distance_parcours > 0'''      
            self.cur.execute(req, (annee, ))
            distances = self.cur.fetchall()

            l_dist_max_annee.append(distances[0][0])
            l_dist_moy_annee.append(distances[0][1])
            annot1_x[annee] = "%d" % (annee)
                          
        self.affiche_histogramme(l_annees, l_dist_max_annee,
                                 list_y2 = l_dist_moy_annee,
                                 labels1_x = annot1_x, xlegend = "Années",
                                 ylegend = "Distance max et moyenne par année")
          
    def affiche_duree_max_moy_annuelle(self):
        '''Recupere les valeurs necessaires pour l'affichage de l'histogramme
        de la durée max_ et la durée moyenne annuelle'''

        req = '''SELECT DISTINCT annee FROM vols
              WHERE duree > 0
              AND NOT type_vol = "Gonflage"
              ORDER BY annee'''
        self.cur.execute(req)
        l_annees = [item[0] for item in self.cur.fetchall()]

        if len(l_annees) < 2:
            self.canv.delete("all")
            return       

        l_duree_moy_annee = []
        l_duree_max_annee = []   
        annot1_x = {}
        
        for annee in l_annees:
            req = '''SELECT MAX(duree), AVG(duree)
                  FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage"
                  AND duree > 0'''      
            self.cur.execute(req, (annee, ))
            durees = self.cur.fetchall()

            l_duree_max_annee.append(durees[0][0])
            l_duree_moy_annee.append(durees[0][1])
            annot1_x[annee] = "%d" % (annee)
                          
        self.affiche_histogramme(l_annees, l_duree_max_annee,
                                 list_y2 = l_duree_moy_annee,
                                 labels1_x = annot1_x, xlegend = "Années",
                                 ylegend = "Temps de vol max et moyen annuel")

    def affiche_duree_totale_annuelle(self):
        '''Recupere les valeurs necessaires pour l'affichage de l'histogramme
        du temps de vol cumulé annuel'''

        req = '''SELECT DISTINCT annee FROM vols
              WHERE duree > 0
              AND NOT type_vol = "Gonflage"
              ORDER BY annee'''
        self.cur.execute(req)
        l_annees = [item[0] for item in self.cur.fetchall()]

        if len(l_annees) < 2:
            self.canv.delete("all")
            return       

        l_duree_tot_annee = []
        annot1_x = {}
        
        for annee in l_annees:
            req = '''SELECT SUM(duree)
                  FROM vols
                  WHERE annee = ?
                  AND NOT type_vol = "Gonflage"
                  AND duree > 0'''      
            self.cur.execute(req, (annee, ))
            durees = self.cur.fetchall()

            l_duree_tot_annee.append(durees[0][0]/60)
            annot1_x[annee] = "%d" % (annee)
                          
        self.affiche_histogramme(l_annees, l_duree_tot_annee,
                                 labels1_x = annot1_x, xlegend = "Années",
                                 ylegend = "Temps de vol total annuel (h)")
        
    def affiche_cumul(self, list_x, list_y, labels1_x = None, labels2_x = None,
                      xlegend = '', ylegend = ''):
        '''Affiche une courbe y = f(x) en escalier avec x dans list_x et y
        dans list_y.
        labels_x est un dictionnaire contenant des chaines de caracteres indexees
        par la position sur l'axe
        
        list_x, list_y doivent contenir le meme nombre 
        d'elements.
        '''
        n = len(list_x)
        if len(list_y) != len(list_x):
            raise Error("list_x and list_y should have the same lenght")

        self.canv.delete("all")

        # valeurs min et max a prendre en compte pour les axes
        min_x, max_x = (min(list_x), max(list_x))
        #min_y, max_y = (min(list_y), max(list_y))
        min_y, max_y = (0, max(list_y))

        # pas en pixels par unite
        if max_x != min_x:
            pas_x = (self.w - 2*m) / (max_x - min_x)
        else: pas_x = (self.w - 2*m)
        if max_y != min_y:
            pas_y = (self.h - 2*m) / (max_y - min_y)
        else: pas_y = (self.h - 2*m)

        # affichage axes x et y
        self.canv.create_line(m, self.h - m, self.w - m, self.h - m,
                              arrow = "last")
        self.canv.create_text(self.w - m, self.h - m - 5,
                              text=xlegend, anchor="se")
        if labels1_x is not None:
            for tic in labels1_x:
                self.canv.create_line(m + (tic - min_x) * pas_x,
                                      self.h - m,
                                      m + (tic - min_x) * pas_x,
                                      self.h - m + 5)
                self.canv.create_text(m + (tic - min_x) * pas_x,
                                      self.h - m + 6, text=labels1_x[tic],
                                      anchor="n", font = "Arial 8")
        if labels2_x is not None:
            for tic in labels2_x:
                self.canv.create_text(m + (tic - min_x) * pas_x,
                                      self.h - m + 16, text=labels2_x[tic],
                                      anchor="nw", font = "Arial 8 bold")
            
        self.canv.create_line(m, self.h - m, m, m,
                              arrow = "last")
        self.canv.create_text(m+5, m, text=ylegend, anchor="w")
        # mettre 10 annotations regulierement espacees sur l'axe y
        y = self.h - m
        annotation = min_y
        pas_annotation_y = (max_y - min_y) / 10
        for i in range(10):
            self.canv.create_line(m-5, y, m, y)
            self.canv.create_text(m - 6, y, text="%d" % (annotation),
                                  anchor="e")
            annotation += pas_annotation_y
            y -= (self.h - 2*m) / 10

        # affichage courbe        
        x0, y0 = (min_x, min_y)

        for i in range(0, n):
            x1, y1 = (list_x[i], list_y[i])
            self.canv.create_line(m + (x0 - min_x) * pas_x,
                                  self.h  - m - (y0 - min_y) * pas_y,
                                  m + (x1 - min_x) * pas_x,
                                  self.h - m - (y0 - min_y) * pas_y,
                                  fill = "blue", width = 2)
            self.canv.create_line(m + (x1 - min_x) * pas_x,
                                  self.h - m - (y0 - min_y) * pas_y,
                                  m + (x1 - min_x) * pas_x,
                                  self.h - m - (y1 - min_y) * pas_y,
                                  fill = "blue", width = 2)

            x0, y0 = (x1, y1)

    def affiche_points(self, list_x, list_y, labels1_x = None, labels2_x = None,
                       xlegend = '',
                       ylegend = ''):
        '''Affiche une series de points (x, y) avec x dans list_x et y
        dans list_y.
        Si labels_x et labels_y sont specifies, leurs valeurs sont utilisees
        pour annoter les axes.     (a programmer)  
        
        list_x, list_y, labels_x et labels_y doivent contenir le meme nombre 
        d'elements.
        '''
        n = len(list_x)
        if len(list_y) != len(list_x):
            raise Error("list_x and list_y should have the same lenght")

        self.canv.delete("all")

         # valeurs min et max a prendre en compte pour les axes
        min_x, max_x = (min(list_x), max(list_x))
        #min_y, max_y = (min(list_y), max(list_y))
        min_y, max_y = (0, max(list_y))

        # pas en pixels par unite
        if max_x != min_x:
            pas_x = (self.w - 2*m) / (max_x - min_x)
        else: pas_x = (self.w - 2*m)
        if max_y != min_y:
            pas_y = (self.h - 2*m) / (max_y - min_y)
        else: pas_y = (self.h - 2*m)

        # affichage axes x et y
        self.canv.create_line(m, self.h - m, self.w - m, self.h - m,
                              arrow = "last")
        self.canv.create_text(self.w - m, self.h - m - 5,
                              text=xlegend, anchor="se")
        for tic in labels1_x:
            self.canv.create_line(m + (tic - min_x) * pas_x,
                                  self.h - m,
                                  m + (tic - min_x) * pas_x,
                                  self.h - m + 5, width = 2)
            self.canv.create_text(m + (tic - min_x) * pas_x,
                                  self.h - m + 6, text=labels1_x[tic],
                                  anchor="n")      
        if labels2_x is not None:
            for tic in labels2_x:
                self.canv.create_text(m + (tic - min_x) * pas_x,
                                      self.h - m + 16, text=labels2_x[tic],
                                      anchor="nw", font = "Arial 8 bold")
            
        self.canv.create_line(m, self.h - m, m, m,
                              arrow = "last")
        self.canv.create_text(m+5, m, text=ylegend, anchor="w")
        # mettre 10 annotations regulierement espacees sur l'axe y
        y = self.h - m
        annotation = min_y
        pas_annotation_y = (max_y - min_y) / 10
        for i in range(10):
            self.canv.create_line(m-5, y, m, y)
            self.canv.create_text(m - 6, y, text="%d" % (annotation),
                                  anchor="e")
            annotation += pas_annotation_y
            y -= (self.h - 2*m) / 10

        for i in range(0, n):
            x, y = (list_x[i], list_y[i])
            self.canv.create_line(m + (x - min_x) * pas_x - 3,
                                  self.h  - m - (y - min_y) * pas_y,
                                  m + (x - min_x) * pas_x + 3,
                                  self.h - m - (y - min_y) * pas_y,
                                  fill = "blue", width = 2)       
            self.canv.create_line(m + (x - min_x) * pas_x,
                                  self.h  - m - (y - min_y) * pas_y - 3,
                                  m + (x - min_x) * pas_x,
                                  self.h - m - (y - min_y) * pas_y + 3,
                                  fill = "blue", width = 2)

    def affiche_histogramme(self, list_x, list_y1, list_y2 = None,
                            labels1_x = None, labels2_x = None, xlegend = '',
                            ylegend = ''):
        '''Affiche un histogramme avec les valeurs de list_x en abscisse et
        celles de list_y en ordonnee.
        Si labels_x et labels_y sont specifies, leurs valeurs sont utilisees
        pour annoter les axes.     
        
        list_x, list_y, labels_x et labels_y doivent contenir le meme nombre 
        d'elements.
        '''
        n = len(list_x)
        if len(list_y1) != len(list_x):
            raise Error("list_x and list_y should have the same lenght")

        self.canv.delete("all")

        # largeur en pixels d'un rectangle de l'histogramme:
        l = (self.w - 2*m) / n - 8

         # valeurs min et max a prendre en compte pour les axes
        min_x, max_x = (min(list_x), max(list_x))
        min_y, max_y = (0, max(list_y1))

        # echelle en pixels par unite
        if max_x != min_x:
            pas_x = (self.w - 2*m) / (max_x - min_x + 1)
        else: pas_x = (self.w - 2*m)
        if max_y != min_y:
            pas_y = (self.h - 2*m) / (max_y - min_y)
        else: pas_y = (self.h - 2*m)

        # affichage axes x et y
        self.canv.create_line(m, self.h - m, self.w - m, self.h - m,
                              arrow = "last")
        self.canv.create_text(self.w - m, self.h - m - 5,
                              text=xlegend, anchor="w")
        for tic in labels1_x:
            self.canv.create_line(m + (tic - min_x) * pas_x + l/2,
                                  self.h - m,
                                  m + (tic - min_x) * pas_x + l/2,
                                  self.h - m + 5, width = 2)
            self.canv.create_text(m + (tic - min_x) * pas_x + l/2,
                                  self.h - m + 6, text=labels1_x[tic],
                                  anchor="n")      
        if labels2_x is not None:
            for tic in labels2_x:
                self.canv.create_text(m + (tic - min_x) * pas_x,
                                      self.h - m + 16, text=labels2_x[tic],
                                      anchor="nw", font = "Arial 8 bold")
            
        self.canv.create_line(m, self.h - m, m, m,
                              arrow = "last")
        self.canv.create_text(m+5, m-10, text=ylegend, anchor="w")
        # mettre 10 annotations sur l'axe y
        y = self.h - m
        annotation = min_y
        pas_annotation_y = (max_y - min_y) / 10
        for i in range(10):
            self.canv.create_line(m-5, y, m, y)
            self.canv.create_text(m - 6, y, text="%.2f" % (annotation),
                                  anchor="e")
            annotation += pas_annotation_y
            y -= (self.h - 2*m) / 10

        for i in range(0, n):
            x, y1 = (list_x[i], list_y1[i])
            self.canv.create_rectangle((m + (x - min_x) * pas_x,
                                      self.h  - m,
                                      m + (x - min_x) * pas_x + l,
                                      self.h - m - (y1 - min_y) * pas_y),
                                      fill = "orange")
            if list_y2 is not None:
                y2 = list_y2[i]
                self.canv.create_rectangle((m + (x - min_x) * pas_x + 2,
                                          self.h  - m,
                                          m + (x - min_x) * pas_x + l + 2,
                                          self.h - m - (y2 - min_y) * pas_y),
                                          fill = "dark green")
                
    def affiche_camembert(self, repartition_v):
        '''Affiche un diagramme circulaire a partir d'un dictionnaire contenant
        des valeurs positives. Les cles du dico sont utilisees pour la legende
        et doivent donc etre un texte descriptif de la valeur.
        
        La somme de toutes les valeurs represente 100 % du diagramme. 
        '''
        self.canv.delete("all")

        min_hw = min(self.h, self.w)
        colors = ['blue', 'red', 'yellow', 'cyan', 'goldenrod',
                  'green', 'hot pink', '#C0C0C0', 'black']
       
        min_v = min(repartition_v.values())
        max_v = max(repartition_v.values())

        total_v = sum(repartition_v.values())

        if min_v < 0 :
            raise ValueError("Cannot plot a negative value on a pie chart")

        def frac(n):
            return 360. * n / total_v
            
        # affichage camembert
        start = frac(0)
        i = 0
        leg = m

        for key in sorted(list(repartition_v.keys())):
            extent = frac(repartition_v[key])
            pourcentage = " %d%%" % (repartition_v[key] / total_v * 100)
            self.canv.create_arc((m, m, min_hw - m, min_hw - m), start = start,
                                 extent = extent, fill = colors[i])

            self.canv.create_rectangle((min_hw, leg, min_hw+10, leg+10),
                                       fill = colors[i])
            self.canv.create_text(min_hw + 15, leg + 5, text=key + pourcentage,
                                  anchor="w")
            
            leg += 10 + m
            i += 1
            if i >= len(colors):
                i = 0
            start += extent
    

if __name__ == '__main__':
    root = Tk()
    FrameStats(root).pack()
    root.mainloop()

