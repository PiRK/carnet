#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Carnet de vol parapente
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

import datetime
import os
import sys
from tkinter.tix import *
from tkinter import messagebox
from tkinter import filedialog

from igctools import IGCTrace
from parawing import submit2parawing
from gestion_ailes import GestionAiles
from gestion_decos_atterros import GestionDecosAtterros
from detection_deco_atterro import trouver_deco_atterro
  
prog_path = os.path.dirname(sys.argv[0])
images_path = os.path.join(prog_path, "images")

class FrameVols(Frame):
    '''Carnet de vol.
    Attributs relatifs a un vol :
        Variables de type StringVar() :
            heure, deco, atterro, aile, type_vol, parcours, encadrement,
            compagnons,errmsg
        Variables de type IntVar() :
            jour, mois, annee, duree, distance_parcours, distance_totale,
            alti_min, alti_max, gain_max, gain_total, vario_min, vario_max, note
        Autre :
            recit : Entry, lat_d, lat_a, lon_d, lon_a
    Autres attributs:
        parawing_user, parawing_pwd : StringVar(),
        
        lbox_vols : liste des vols (widget listbox)
        
    '''
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.db_connected = False       
        self.conn = None
        self.cur = None      

        self.parawing_user = StringVar()
        self.parawing_pwd = StringVar()
        self.connected_to_parawing = False
        self.vol_sur_parawing = False

        # Variables pour les coordonnees du deco et de l'atterro
        self.lat_d = 0
        self.lon_d = 0
        self.lat_a = 0
        self.lon_a = 0
        
        # premiere frame : liste des vols
        f1 = Frame(self, bd=3)
        yscr_lb = Scrollbar(f1, orient='vertical')
        yscr_lb.pack(side="right", fill=tkinter.tix.Y)
        self.lbox_vols = Listbox(f1, bg="white", yscrollcommand=yscr_lb.set,
                                 selectmode="single", width=50)
        self.lbox_vols.pack(expand=1, fill=tkinter.tix.BOTH)
        self.lbox_vols.bind("<Double Button-1>", self.select_vol)
        yscr_lb.config(command=self.lbox_vols.yview)
        f1.pack(expand=1, fill=tkinter.tix.BOTH, side="left")
        
        # deuxieme frame : modifier ou ajouter un vol
        f2 = Frame(self, bd=3)

        ##frame pour les 3 boutons du haut
        f21 = Frame(f2, bd=3)
        new_icon = PhotoImage(file = os.path.join(images_path,
                                                   "document-new.gif"))
        open_icon = PhotoImage(file = os.path.join(images_path,
                                                   "document-open-7.gif"))
        remove_icon = PhotoImage(file = os.path.join(images_path,
                                                     "view-remove.gif"))
        b = Button(f21, text=" Nouveau vol", image = new_icon, compound='left',
                   command=self.clear_entries)
        b.image = new_icon
        b.grid(column=0, row=0, sticky="EW")
     
        b = Button(f21, text=" Supprimer vol", image=remove_icon, compound='left',
                   command=self.supprimer_vol)
        b.image = remove_icon
        b.grid(column=1, row=0, sticky="EW")
        
        b = Button(f21, text=" Charger trace igc", image=open_icon, compound='left',
                   command=self.charger_igc)
        b.image = open_icon
        b.grid(column=2, row=0, sticky="EW")
        
        f21.grid(column=1, row=0, columnspan=3, sticky="EW")
        f21.columnconfigure(0, pad=20)
        f21.columnconfigure(1, pad=20)
        f21.columnconfigure(2, pad=20)

        # Date
        Label(f2, text="Date :").grid(column=0, row=1, sticky="W")
        self.jour = IntVar()
        self.mois = IntVar()        
        self.annee = IntVar()
       
        now = datetime.datetime.now()
        
        cb = ComboBox(f2, label="Jour", dropdown=1, editable=1, bg="white",
                      variable=self.jour, listwidth = 20)
        cb.entry.config(width=2, bg='white')
        for i in range(31):
            cb.insert(tkinter.tix.END, i+1)
        cb.grid(column=1, row=1, sticky="W")
        self.jour.set(now.day)

        cb = ComboBox(f2, label="Mois", dropdown=1, editable=1,
                      variable=self.mois, value=1, listwidth = 20)
        cb.entry.config(width=2, bg='white')
        for i in range(12):
            cb.insert(tkinter.tix.END, i+1)
        cb.grid(column=2, row=1, sticky="W")
        self.mois.set(now.month)

        cb = ComboBox(f2, label="Année", dropdown=1, editable=1,
                      variable=self.annee, value=1, listwidth = 20)
        cb.entry.config(width=4, bg='white')
        for i in range(now.year, now.year-20, -1):
            cb.insert(tkinter.tix.END, i)
        cb.grid(column=3, row=1, sticky="W")    
        self.annee.set(now.year)

        #Heure
        self.heure = StringVar()
        
        Label(f2, text="Heure :").grid(column=0, row=2, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.heure)
        e.grid(column=1, row=2, sticky="W")

        #Decollage Atterrissage       
        self.deco = StringVar()
        self.atterro = StringVar()
        
        Label(f2, text="Décollage :").grid(column=0, row=3, sticky="W")
        self.cb_deco = ComboBox(f2, dropdown=1, editable=1,
                                variable=self.deco)
        self.cb_deco.entry.config(bg='white')
        self.cb_deco.grid(column=1, row=3, sticky="W") 

        Label(f2, text="Atterrissage :").grid(column=2, row=3, sticky="W")
        self.cb_atterro = ComboBox(f2, dropdown=1, editable=1,
                                   variable=self.atterro)
        self.cb_atterro.entry.config(bg='white')
        self.cb_atterro.grid(column=3, row=3, sticky="W") 
        
        #Aile
        self.aile = StringVar()
        
        Label(f2, text="Aile :").grid(column=0, row=4, sticky="W")
        self.cb_aile = ComboBox(f2, dropdown=1, editable=1,
                                variable=self.aile)
        self.cb_aile.entry.config(bg='white')
        self.cb_aile.grid(column=1, row=4, sticky="W") 
        
        # Type de vol
        self.type_vol = StringVar()
        
        Label(f2, text="Type de vol :").grid(column=0, row=5, sticky="W")
        cb = ComboBox(f2, dropdown=1, editable=0, variable=self.type_vol)
        cb.entry.config(bg='white')
        types_vol = ['Plouf', 'Vol thermique sur site', 'Cross', 'Vol rando',
                     'Gonflage', 'Soaring', 'Rando & cross', 'SIV', 'Biplace',
                     'Treuil', 'Voltige', 'Vol à ski', 'Speedriding',
                     'Compétition']
        for item in types_vol:
            cb.insert(tkinter.tix.END, item)
        cb.grid(column=1, row=5, sticky="W")

        # Parcours
        self.parcours = StringVar()
        Label(f2, text="Parcours :").grid(column=2, row=5, sticky="W")
        cb = ComboBox(f2, dropdown=1, editable=0, variable=self.parcours)
        cb.entry.config(bg='white')
        types_parcours = ['DL', 'DL1', 'DL2', 'DL3', 'AR', 'Triangle',
                          'Triangle FAI', 'Quadrilatere']
        for item in types_parcours:
            cb.insert(tkinter.tix.END, item)
        cb.grid(column=3, row=5, sticky="W")
        
        #Duree
        self.duree = IntVar()
        
        Label(f2, text="Durée (minutes) :").grid(column=0, row=6, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.duree)
        e.grid(column=1, row=6, sticky="W")

        #Distances
        self.distance_parcours = IntVar()
        self.distance_totale = IntVar()
        
        Label(f2, text="Distance sur\n parcours :").grid(column=0, row=7, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.distance_parcours)
        e.grid(column=1, row=7, sticky="W")

        Label(f2, text="Distance totale :").grid(column=2, row=7, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.distance_totale)
        e.grid(column=3, row=7, sticky="W")

        #Alti min max
        self.alti_max = IntVar()
        self.alti_min = IntVar()
        
        Label(f2, text="Altitude max :").grid(column=0, row=8, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.alti_max)
        e.grid(column=1, row=8, sticky="W")

        Label(f2, text="Altitude min :").grid(column=2, row=8, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.alti_min)
        e.grid(column=3, row=8, sticky="W")

        #Gain 
        self.gain_max = IntVar()
        self.gain_total = IntVar()
        
        Label(f2, text="Gain max :").grid(column=0, row=9, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.gain_max)
        e.grid(column=1, row=9, sticky="W")

        Label(f2, text="Gain total :").grid(column=2, row=9, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.gain_total)
        e.grid(column=3, row=9, sticky="W")

        #Vario min max
        self.vario_max = DoubleVar()
        self.vario_min = DoubleVar()
        
        Label(f2, text="Vario max (m/s) :").grid(column=0, row=10, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.vario_max)
        e.grid(column=1, row=10, sticky="W")

        Label(f2, text="Vario min (m/s) :").grid(column=2, row=10, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.vario_min)
        e.grid(column=3, row=10, sticky="W")
        
        # Encadrement
        self.encadrement = StringVar()
        Label(f2, text="Encadrement :").grid(column=0, row=11, sticky="W")
        cb = ComboBox(f2, dropdown=1, editable=0, variable=self.encadrement)
        cb.entry.config(bg='white')
        encadrements = ['Autonome', 'Entre potes', 'Club', 'Ecole']
        for item in encadrements:
            cb.insert(tkinter.tix.END, item)
        cb.grid(column=1, row=11, sticky="W")

        self.compagnons = StringVar()
        Label(f2, text="Compagnons :").grid(column=0, row=12, sticky="W")       
        e = Entry(f2, bg="white", textvariable=self.compagnons)
        e.grid(column=1, row=12, columnspan=3, sticky="EW")

        # Recit
        Label(f2, text="Récit :").grid(column=0, row=13, sticky="W")
        self.recit = Text(f2, width=50, wrap='word', height=10, bg = 'white')
        self.recit.grid(column=1, row=13, columnspan=3, sticky="EW")

        #Note
        self.note = IntVar()
        Label(f2, text="Note :").grid(column=0, row=14, sticky="W")
        cb = ComboBox(f2, dropdown=1, editable=0, variable=self.note,
                      listwidth=20)
        cb.entry.config(width=2, bg='white')
        for i in range(5):
            cb.insert(tkinter.tix.END, i+1)
        cb.grid(column=1, row=14,sticky = "W")
        l = Label(f2, text="(1 : Nul ... 5 : Génial)")
        l.grid(column=2, row=14, sticky="W")

        ##frame pour les 3 boutons du bas
        f22 = Frame(f2, bd=3)
        
        save_icon = PhotoImage(file = os.path.join(images_path,
                                                   "document-export.gif"))
        modif_icon = PhotoImage(file = os.path.join(images_path,
                                                   "db_comit.gif"))
        parawing_logo = PhotoImage(file = os.path.join(images_path,
                                                       "parawing.gif"))      
        b = Button(f22, text=" Enregistrer\nnouveau vol",
                   image  = save_icon, command=self.ajouter_vol,
                   compound='left')
        b.image = save_icon
        b.grid(column=0, row=0, sticky="EW")

        b = Button(f22, text=" Modifier le vol\nsélectionné", image= modif_icon, 
                  compound='left', command=self.modifier_vol)
        b.image = modif_icon
        b.grid(column=1, row=0, sticky="EW")

        b = Button(f22, text="Publier le vol\nsur parawing ", image=parawing_logo,
                   command=self.interface_export_parawing, compound='right')
        b.image = parawing_logo
        b.grid(column=2, row=0, sticky="EW")
        
        f22.grid(column=1, row=15, columnspan=3, sticky="EW")
        f22.columnconfigure(0, pad=20)
        f22.columnconfigure(1, pad=20)
        f22.columnconfigure(2, pad=20)

        # Message d'erreur en cas de probleme avec une valeur saisie
        self.errmsg = StringVar()
        l = Label(f2, textvariable=self.errmsg, fg='red')
        l.grid(column=0, row=16, columnspan=4)
        

        f2.pack(expand=1, fill=tkinter.tix.BOTH, side="right")

        f2.columnconfigure(0, pad=4)
        f2.columnconfigure(1, pad=4)
        f2.columnconfigure(2, pad=4)
        f2.columnconfigure(3, pad=4)    
        self.rowconfigure(0, pad=6)      
        self.rowconfigure(1, pad=6)     
        self.rowconfigure(2, pad=6)     
        self.rowconfigure(3, pad=6)     
        self.rowconfigure(4, pad=6)     
        self.rowconfigure(5, pad=6)      
        self.rowconfigure(6, pad=6)    
        self.rowconfigure(7, pad=6)      
        self.rowconfigure(8, pad=6)     
        self.rowconfigure(9, pad=6)     
        self.rowconfigure(10, pad=6)     
        self.rowconfigure(11, pad=6)     
        self.rowconfigure(12, pad=6)      
        self.rowconfigure(13, pad=6)      
        self.rowconfigure(14, pad=6)      
        self.rowconfigure(15, pad=6)

    def on_pilot_selection(self, conn):
        '''Fonction executee lorsqu'un pilote est selectionne

        Chargement des informations a partir de sa base de donnees'''
        self.db_connected = True
        self.conn = conn
        self.cur = self.conn.cursor()
        
        self.maj_liste_vols()
        self.maj_liste_decos_atterros()
        self.maj_liste_ailes()

    def maj_liste_vols(self):
        if not self.db_connected:
            self.errmsg.set("not connected to a db")
            return
        self.errmsg.set("")
        self.cur.execute('''SELECT * from vols order by annee desc, mois desc,
                           jour desc''')
        self.liste_vols_bdd = self.cur.fetchall()
        self.lbox_vols.delete(0, 'end')
        for vol in self.liste_vols_bdd:
            
            vol_str = "%02d/%02d/%04d" % (vol[3], vol[2], vol[1])
            vol_str += " - {:5} min - {:4} km - {}".format(vol[10], vol[11],
                                                              vol[5])
            self.lbox_vols.insert('end', vol_str)

    def maj_liste_decos_atterros(self):
        if not self.db_connected:
            self.errmsg.set("not connected to a db")
            return
        self.errmsg.set("")

        # DECOS:
        self.cur.execute('''SELECT * from decos order by deco''')
        self.liste_decos_bdd = self.cur.fetchall()

        self.cb_deco.slistbox.listbox.delete(0, 'end')
        for item in self.liste_decos_bdd:
            self.cb_deco.insert(tkinter.tix.END, item[1])

        # ATTERROS:
        self.cur.execute('''SELECT * from atterros order by atterro''')
        self.liste_atterros_bdd = self.cur.fetchall()

        self.cb_atterro.slistbox.listbox.delete(0, 'end')
        for item in self.liste_atterros_bdd:
            self.cb_atterro.insert(tkinter.tix.END, item[1])     
                
    def maj_liste_ailes(self):
        if not self.db_connected:
            self.errmsg.set("not connected to a db")
            return
        self.errmsg.set("")

        # DECOS:
        self.cur.execute('''SELECT * from ailes order by modele''')
        self.liste_ailes_bdd = self.cur.fetchall()

        self.cb_aile.subwidget_list['slistbox'].subwidget_list['listbox'].delete(0, 'end')
        for item in self.liste_ailes_bdd:
            self.cb_aile.insert(tkinter.tix.END, item[1])

            
    def select_vol(self, *args):
        '''Un double clic sur un vol dans la liste lance cette fonction qui
        met a jour les champs
        '''
        self.errmsg.set("")
        # RAZ
        self.clear_entries()
        self.jour.set(0)
        self.mois.set(0)
        self.annee.set(0)
        
        for i in self.lbox_vols.curselection():
            vol = self.liste_vols_bdd[int(i)]
            self.vid = vol[0]
            if vol[3] is not None:
                self.jour.set(vol[3])
            if vol[2] is not None:
                self.mois.set(vol[2])
            if vol[1] is not None:
                self.annee.set(vol[1])
            if vol[4] is not None:
                self.heure.set(vol[4])
            if vol[5] is not None:
                self.deco.set(vol[5])
            if vol[6] is not None:
                self.atterro.set(vol[6])
            if vol[7] is not None:
                self.aile.set(vol[7])
            if vol[8] is not None:
                 self.type_vol.set(vol[8])
            if vol[9] is not None:
                self.parcours.set(vol[9])
            if vol[10] is not None:
                self.duree.set(vol[10])
            if vol[11] is not None:
                self.distance_parcours.set(vol[11])
            if vol[12] is not None:
                self.distance_totale.set(vol[12])
            if vol[13] is not None:
                self.alti_max.set(vol[13])
            if vol[14] is not None:
                self.alti_min.set(vol[14])
            if vol[15] is not None:
                self.gain_max.set(vol[15])
            if vol[16] is not None:
                self.gain_total.set(vol[16])
            if vol[17] is not None:
                self.vario_max.set(vol[17])
            if vol[18] is not None:
                self.vario_min.set(vol[18])
            if vol[19] is not None:
                self.encadrement.set(vol[19])
            if vol[20] is not None:
                self.compagnons.set(vol[20])
            if vol[21] is not None:
                self.recit.delete('1.0', 'end')
                self.recit.insert('1.0', vol[21])
            if vol[22] is not None:
                self.note.set(vol[22])
            if vol[23]:
                self.vol_sur_parawing = True


    def clear_entries(self):
        '''Remise a zero des champs de saisie pour saisir un nouveau vol'''
        now = datetime.datetime.now()
        self.jour.set(now.day)
        self.mois.set(now.month)
        self.annee.set(now.year)
        self.heure.set("")
        self.deco.set("")
        self.atterro.set("")
        self.aile.set("")
        self.type_vol.set("")
        self.parcours.set("")
        self.duree.set(0)
        self.distance_totale.set(0)
        self.distance_parcours.set(0)
        self.alti_min.set(0)
        self.alti_max.set(0)
        self.gain_total.set(0)
        self.gain_max.set(0)
        self.vario_min.set(0)
        self.vario_max.set(0)
        self.encadrement.set("")
        self.compagnons.set("")
        self.note.set(0)
        self.recit.delete('1.0', 'end')
        self.vol_sur_parawing = False
        
        self.lat_d = 0
        self.lon_d = 0
        self.lat_a = 0
        self.lon_a = 0

    def ajouter_vol(self):
        '''Enregistrer les champs saisis dans un nouveau vol.'''
        if not self.db_connected:
            self.errmsg.set("not connected to a db")
            return
        self.errmsg.set("")

        # identifiant nouveau vol : incrementer l'identifiant max
        # des vols existants ou choisir 1 si la table est vide
        req = "SELECT MAX(vid) FROM vols"
        self.cur.execute(req)
        max_vid_list = self.cur.fetchall()
        if len(max_vid_list):
            if max_vid_list[0][0] is not None:
                self.vid = max_vid_list[0][0] + 1
            else :
                self.vid = 1
        else :
            self.vid = 1
        req =  "INSERT INTO vols VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?," 
        req += " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        if self.vol_sur_parawing:
            vsp = 1
        else:
            vsp = 0
        params = (self.vid, self.annee.get(), self.mois.get(), self.jour.get(),
                  self.heure.get(), self.deco.get(), self.atterro.get(),
                  self.aile.get(), self.type_vol.get(), self.parcours.get(),
                  self.duree.get(), self.distance_parcours.get(),
                  self.distance_totale.get(), self.alti_max.get(),
                  self.alti_min.get(), self.gain_max.get(),
                  self.gain_total.get(), self.vario_max.get(),
                  self.vario_min.get(), self.encadrement.get(),
                  self.compagnons.get(), self.recit.get('1.0', 'end'),
                  self.note.get(), vsp)

        self.cur.execute(req, params)
        self.conn.commit()
        
        self.maj_liste_vols()
        self.maj_bdd_deco_atterro()
        self.maj_bdd_ailes()

    def modifier_vol(self):
        '''Enregistrer les champs saisis dans un vol existant.'''
        self.errmsg.set("")
        if not self.db_connected:
            self.errmsg.set("Vous devez ouvrir un carnet de vol pour " +
                            "pouvoir modifier un vol.")
            return
        curselection = self.lbox_vols.curselection()
        if not len(curselection):
            self.errmsg.set("Aucun vol sélectionné")
            return

        vol = self.liste_vols_bdd[int(curselection[0])]

        confirmer = "Etes-vous sûr de vouloir modifier le vol"
        confirmer += " du %02d/%02d/%04d à %s ?" % (vol[3], vol[2],
                                                    vol[1], vol[5])
        vid = vol[0]
        
        if not messagebox.askyesno(message=confirmer, icon='question',
                                   title="Confirmation"):
            return
            
        req =  "UPDATE vols SET  annee = ?, mois = ?, jour = ?, heure = ? , "
        req += "deco = ?, atterro = ?, aile = ?, type_vol = ?, parcours = ?, "
        req += "duree = ?, distance_parcours = ?, distance_totale = ?, "
        req += "alti_max = ?, alti_min = ?, gain_max = ?, gain_total = ?, "
        req += "vario_max = ?, vario_min = ?, encadrement = ?, compagnons = ?, "
        req += " recit = ?, note = ?, vol_sur_parawing = ? WHERE vid = ?"


        if self.vol_sur_parawing:
            vsp = 1
        else:
            vsp = 0
        
        params = (self.annee.get(), self.mois.get(), self.jour.get(),
                  self.heure.get(), self.deco.get(), self.atterro.get(),
                  self.aile.get(), self.type_vol.get(), self.parcours.get(),
                  self.duree.get(), self.distance_parcours.get(),
                  self.distance_totale.get(), self.alti_max.get(),
                  self.alti_min.get(), self.gain_max.get(),
                  self.gain_total.get(), self.vario_max.get(),
                  self.vario_min.get(), self.encadrement.get(),
                  self.compagnons.get(), self.recit.get('1.0', 'end'),
                  self.note.get(), vsp, vid)
        
        self.cur.execute(req, params)
        self.conn.commit()
        
        self.maj_liste_vols()
        self.maj_bdd_deco_atterro()
        self.maj_bdd_ailes()
       
    def supprimer_vol(self):
        '''Supprimer un vol du carnet'''
        if not self.db_connected:
            self.errmsg.set("Vous devez ouvrir un carnet de vol pour " +
                            "pouvoir supprimer un vol")
            return

        curselection = self.lbox_vols.curselection()
        if not len(curselection):
            self.errmsg.set("Aucun vol sélectionné")
            return
        vol = self.liste_vols_bdd[int(curselection[0])]
        vid = vol[0]
        
        confirmer = "Etes-vous sûr de vouloir supprimer le vol"
        confirmer += " du %02d/%02d/%04d à %s ?" % (vol[3], vol[2],
                                                    vol[1], vol[5])
        confirmer = "Etes-vous sûr de vouloir supprimer définitivement le vol"
        confirmer += " (id=%d) ?" % (vid)
        
        if messagebox.askyesno(message=confirmer, icon='question',
                               title="Confirmation"):
            req = "DELETE FROM vols WHERE vid=?"

            self.cur.execute(req, (vid, ))
            self.maj_liste_vols()

    def maj_bdd_deco_atterro(self):
        '''Verification si le deco et l'atterro saisis sont déja dans la bdd
        idoine, et si non les ajouter'''

        deco = self.deco.get()
        req = "SELECT COUNT(*) FROM decos WHERE deco = ?"
        deco_in_db = (self.cur.execute(req, (deco,)).fetchall()[0][0] > 0)
        
        atterro = self.atterro.get()
        req = "SELECT COUNT(*) FROM atterros WHERE atterro = ?"
        atterro_in_db = self.cur.execute(req, (atterro,)).fetchall()[0][0] > 0

        if not deco_in_db and not atterro_in_db:
            # atterro et deco pas encore dans la bdd
            msg = "Souhaitez vous enregistrer ces nouveaux sites de "
            msg += "décollage et d'atterrissage ?"
        elif not deco_in_db:
            # atterro deja dans la bdd, pas le deco
            msg = "Souhaitez vous enregistrer ce nouveau site de décollage ?"
            atterro = ""
        elif not atterro_in_db:
            # deco deja dans la bdd, pas l'atterro
            deco = ""
            msg = "Souhaitez vous enregistrer ce nouveau site d'atterrissage ?"
        else:
            # Decos et atterros deja dans la bdd 
            return
        
        if messagebox.askyesno(message=msg, icon='question'):     
            GestionDecosAtterros(deco = deco, atterro=atterro,
                                 lat_d = self.lat_d, lon_d = self.lon_d,
                                 lat_a = self.lat_a, lon_a = self.lon_a,
                                 conn = self.conn, cur = self.cur)

    def maj_bdd_ailes(self):
        '''Verification si l'aile saisie est déja dans la bdd
        idoine, et si non l'ajouter'''

        aile = self.aile.get()
        req = "SELECT COUNT(*) FROM ailes WHERE modele = ?"
        aile_in_db = (self.cur.execute(req, (aile,)).fetchall()[0][0] > 0)
        
        if not aile_in_db:
            # aile deja dans la bdd
            msg = "Souhaitez vous enregistrer cette nouvelle aile ?"
            if messagebox.askyesno(message=msg, icon='question'):     
                GestionAiles(modele = aile, conn = self.conn, cur = self.cur) 
        else:
            # Aile deja dans la bdd 
            return
      
        
    def interface_export_parawing(self):
        '''Interface de saisie du nom d'utilisateur et mot de passe
        parawing.'''

        self.intf_paraw = Toplevel(self)

        msg = "Connexion au carnet de vol Parawing et ajout d'un vol"
        l = Label(self.intf_paraw, text=msg, font = "Arial 12 bold")
        l.grid(column=0, row=0, columnspan=2)
        
        if not self.connected_to_parawing:
            Label(self.intf_paraw, text="Pilote :").grid(column=0, row=1)
            e = Entry(self.intf_paraw, bg="white", textvariable = self.parawing_user)
            e.grid(column=1, row=1)
            Label(self.intf_paraw, text="Mot de passe :").grid(column=0, row=2)
            e = Entry(self.intf_paraw, bg="white", textvariable = self.parawing_pwd)
            e.grid(column=1, row=2)
        else:
            l = Label(self.intf_paraw, text="Déja connecté", fg="blue",
                      font = "Arial 12 bold")
            l.grid(column=0, row=1, columnspan=2)

        Label(self.intf_paraw, text="Publier le vol ?").grid(column=0, row=3)
        self.vol_public = IntVar()
        Checkbutton(self.intf_paraw, variable=self.vol_public).grid(column=1, row=3)
        self.vol_public.set(0)

        b=Button(self.intf_paraw, text="Ajouter le vol",command=self.export_parawing)
        b.grid(column=0, row=4)
        
        b=Button(self.intf_paraw, text="Annuler",
                 command=lambda: self.intf_paraw.destroy())
        b.grid(column=1, row=4)

        # Message d'erreur en cas de probleme avec une valeur saisie
        self.errmsg_paraw = StringVar()
        l = Label(self.intf_paraw, textvariable=self.errmsg_paraw, fg='red')
        l.grid(column=0, row=5, columnspan=2)
        
    def export_parawing(self):
        '''Connection parawing si necessaire et ajout du vol'''

        if self.vol_public.get():
            vis = "on"
        else:
            vis = "off"

        resp = submit2parawing(login = self.parawing_user.get(),
                              pwd = self.parawing_pwd.get(),
                              jour = str(self.jour.get()),
                              mois = str(self.mois.get()),
                              annee = str(self.annee.get()),
                              duree = str(self.duree.get()),
                              deco = self.deco.get(),
                              atterro = self.atterro.get(),
                              aile = self.aile.get(),
                              type_vol = self.type_vol.get(),
                              heure = self.heure.get(),
                              distance = str(self.distance_parcours.get()),
                              alt_max = str(self.alti_max.get()),
                              pt_bas = str(self.alti_min.get()),
                              gain_max= str(self.gain_max.get()),
                              gain_total = str(self.gain_total.get()),
                              cadre = self.encadrement.get(),
                              compagnons = self.compagnons.get(),
                              recit = self.recit.get(1.0, END),
                              note = str(self.note.get()),
                              visible = vis)
        
        if 'Login ou mot de passe incorrect' in resp:
            self.errmsg_paraw.set("Login ou mot de passe incorrect !")
            return                
        elif 'Echec de la connexion' in resp:
            self.errmsg_paraw.set("Echec de la connexion, raison inconnue.")
            return
        else:
            self.connected_to_parawing = True
            self.errmsg_paraw.set("")
            
        self.errmsg.set(resp)  

        self.intf_paraw.destroy()


    def charger_igc(self):
        '''Preremplir un vol a partir des infos tirees de la trace igc'''
        confirmer= "Vous allez charger une trace au format IGC pour déterminer"
        confirmer+= " les informations suivantes : date, durée, distance totale"
        confirmer+= ", altitude min et max, gain total, vario min et max. \nSi"
        confirmer += " vous avez déjà rempli certains de ces champs, les "
        confirmer += "informations que vous avez fournies seront écrasées."

        if not messagebox.askokcancel(message=confirmer, icon='info', 
                                     title="Confirmation"):
            return
        igcformat = (('Trace GPS au format IGC', '*.igc'),
                     ('Tous les fichiers', '*'))
        igcfname = filedialog.askopenfilename(filetypes=igcformat)
        if not len(igcfname):
            return
        igctrace = IGCTrace(igcfname)
        self.jour.set(igctrace.date.day)
        self.mois.set(igctrace.date.month)
        self.annee.set(igctrace.date.year)
        # a faire : conversion utc-> france
        self.heure.set("%02d" % (igctrace.trace[0].dt.hour) + ":" +
                       "%02d" % (igctrace.trace[0].dt.minute))  
        self.duree.set(igctrace.duration//60)
        self.distance_totale.set(int(igctrace.get_total_dist("km")))
        self.alti_min.set(igctrace.min_elev)
        self.alti_max.set(igctrace.max_elev)
        self.gain_total.set(igctrace.total_gain)
        self.vario_min.set(igctrace.min_vario)
        self.vario_max.set(igctrace.max_vario)
        self.type_vol.set("Cross")

        # Coord premier et dernier points
        self.lat_d = igctrace.trace[0].lat
        self.lon_d = igctrace.trace[0].lon
        self.lat_a = igctrace.trace[-1].lat
        self.lon_a = igctrace.trace[-1].lon

        if self.conn is not None:
            deco, atterro = trouver_deco_atterro(igctrace.trace,
                                                 self.conn)
        if deco is not None:
            self.deco.set(deco)
        if atterro is not None:
            self.atterro.set(atterro)
            



                
