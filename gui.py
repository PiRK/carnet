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

import glob
import os
import sqlite3
from tkinter.tix import *
from tkinter import messagebox
from tkinter import filedialog

from frame_vols import FrameVols
from frame_stats import FrameStats
from frame_cfd import FrameCFD
from gestion_pilotes import GestionPilotes
from gestion_decos_atterros import GestionDecosAtterros
from gestion_ailes import GestionAiles
from gestion_cfd import GestionCFD
from parawing import csv2db

db_path = os.path.join(os.path.dirname(sys.argv[0]), 'pilotes')

class CarnetVol(Tk):
    '''Racine de l'interface graphique. Executer ce fichier pour lancer
    le programme

    Cette classe gere les menu et onglets ainsi que la connexion a la base de
    donnees puis invoque les sous-classes pour l'affichage du carnet de vol,
    des statistiques et des classements CFD. Elle s'occupe de leur transferer
    la connexion a la base de donnees une fois celle-ci etablie.
    '''
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.parent = parent
        self.db_connected = False

        self.protocol("WM_DELETE_WINDOW", self.doDestroy)
        
        self.GUI()

    def GUI(self):
        # Barre de menu
        menubar = Menu(self)
        menufichier = Menu(menubar, tearoff=0)
        
        self.menupilotes = Menu(menufichier, tearoff=0) 
        self.populate_menu_pilotes()
        menufichier.add_cascade(label = "Choix pilote", menu=self.menupilotes)

        menufichier.add_command(label = "Import parawing",
                                command=self.import_parawing)
        menufichier.add_separator()
        menufichier.add_command(label = "Quitter",
                                command=self.doDestroy)
        menubar.add_cascade(label="Fichier", menu=menufichier)

        menueditions = Menu(menubar, tearoff=0)
        menueditions.add_command(label = "Pilotes",
                                 command=self.gestion_pilotes)
        menueditions.add_command(label = "Décos/Atterros",
                                 command=self.gestion_decos_atterros)
        menueditions.add_command(label = "Ailes",
                                 command=self.gestion_ailes)
        menueditions.add_command(label = "Classements CFD",
                                 command=self.gestion_cfd)

        menubar.add_cascade(label="Editions", menu=menueditions)
        
        self.config(menu=menubar)
        
        # Onglets
        self.nb = tkinter.tix.NoteBook(self, name='nb')
        ## Onglet carnet de vol
        self.nb.add('vols', label="Vols", underline=0)
        self.f_vols = FrameVols(self.nb.vols)
        self.f_vols.pack(expand=1, fill=tkinter.tix.BOTH)
        ## Onglet stats de vol
        self.nb.add('stats', label="Statistiques", underline=0)
        self.f_stats = FrameStats(self.nb.stats)
        self.f_stats.pack(expand=1, fill=tkinter.tix.BOTH)
        ## Onglet classement CFD
        self.nb.add('cfd', label="CFD", underline=0)
        self.f_cfd = FrameCFD(self.nb.cfd)
        self.f_cfd.pack(expand=1, fill=tkinter.tix.BOTH)

        self.nb.pack(expand=1, fill=tkinter.tix.BOTH)
       
    def gestion_pilotes(self):
        '''Fenetre de gestion des pilotes'''
        GestionPilotes(self)

    def gestion_decos_atterros(self):
        '''Fenetre de gestion des decos et atterros'''
        if not self.db_connected:
            GestionDecosAtterros(conn = None, cur = None)
        else:
            GestionDecosAtterros(conn = self.conn,
                                 cur = self.cur)
            
    def gestion_ailes(self):
        '''Fenetre de gestion des decos et atterros'''
        if not self.db_connected:
            GestionAiles(conn = None, cur = None)
        else:
            GestionAiles(conn = self.conn,
                         cur = self.cur)

    def gestion_cfd(self):
        '''Fenetre de gestion des decos et atterros'''
        if not self.db_connected:
            GestionCFD(conn = None, cur = None)
        else:
            GestionCFD(conn = self.conn,
                         cur = self.cur)
            
    def populate_menu_pilotes(self):
        self.load_existing_pilots()
        test = []
        i=0
        # ajouter une entree de menu pour chaque utilisateur
        for pilot in self.list_pilots:
            # fonction qui renvoie une fonction qui se connecte a une BdD
            # (cf http://fr.w3support.net/index.php?db=so&id=728356 )
            def db_load_function_generator(pilot):
                def pilot_db_load():
                    # Si on est deja connecte, demander confirmation et fermer
                    #  la connexion precedente
                    if self.db_connected:
                        confirmer = "Etes-vous sûr de vouloir changer de pilote ?\n"
                        confirmer+="Les modifications non enregistrées seront perdues."
                        if not messagebox.askyesno(message=confirmer, icon='question',
                                                   title="Changer d'utilisateur"):
                            return
                        self.conn.close()
                        self.db_connected = False
                        self.f_vols.db_connected = False
                        self.f_stats.db_connected = False
                        self.f_cfd.db_connected = False

                    print("Connexion a la BdD : " + pilot)
                    # Se connecter a la nouvelle db
                    self.conn = sqlite3.connect(pilot)
                    self.cur = self.conn.cursor()
                    self.db_connected = True
                    # Transferer les infos de connection bdd aux onglets
                    self.f_vols.on_pilot_selection(self.conn)
                    self.f_stats.on_pilot_selection(self.conn)
                    self.f_cfd.on_pilot_selection(self.conn)
                return pilot_db_load
            
            self.menupilotes.add_command(label = os.path.basename(pilot),
                                    command=db_load_function_generator(pilot))
        
        
    def import_parawing(self):
        '''Import des vols d'un fichier csv exporté sur parawing
        '''
        if not self.db_connected:
            print("Sélectionnez un pilote avant d'importer des vols dans sa"
                  + " base de données.")
            return
   
        csvformat = (('Tous les fichiers', '*'),
                     ("Fichier d'export parawing", '*.csv'))   
        csvfname = filedialog.askopenfilename(filetypes=csvformat)

        if csvfname:      
            csv2db(csvfname, self.conn)
            self.f_vols.maj_liste_vols()
            self.f_stats.fill_cb_annees()


    def load_existing_pilots(self):
        '''Get list of pilots database files'''        
        self.list_pilots = glob.glob(os.path.join(db_path, '*'))   
        self.list_pilots.sort()    


    def doDestroy(self):
        # a faire : demander confirmation
        if self.db_connected:
            self.conn.commit()
            self.conn.close()
        self.destroy()


if __name__ == "__main__":
    app = CarnetVol(None)
    app.title('Carnet de vol')
    app.mainloop()
