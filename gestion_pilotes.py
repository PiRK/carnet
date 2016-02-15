#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Carnet de vol parapente - Menu de gestion des pilotes
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

db_path = os.path.join(os.path.dirname(sys.argv[0]), 'pilotes')
images_path = os.path.join(os.path.dirname(sys.argv[0]), 'images')

class GestionPilotes(Toplevel):
    '''Interface de gestion des pilotes invoquee depuis le menu "Editions"

    Une liste des pilotes existants est affichee avec des boutons permettant
    d'en ajouter, d'en supprimer ou d'en renommer.
    '''
    def __init__(self, parent=None):
        Toplevel.__init__(self, parent, takefocus=True)

        self.parent = parent       
        self.list_pilots = []
        
        self.protocol("WM_DELETE_WINDOW", self.doDestroy)
        
        self.grid()
        # Elements de l'interface graphique
        ## Titre
        l = Label(self, text="Pilotes:", font = "Arial 14 underline")
        l.grid(column=0, row=0, columnspan=2, sticky="W")
        ## Liste des pilotes
        yscr_lb = Scrollbar(self, orient='vertical')
        yscr_lb.grid(column=1, row=1, rowspan=4, sticky='NSW')

        self.lbox = Listbox(self, bg="white", yscrollcommand=yscr_lb.set,
                            selectmode="single", height=5)
        self.lbox.grid(column=0, row = 1, rowspan=4, sticky="NSEW")
        yscr_lb.config(command=self.lbox.yview)

        self.load_existing_pilots()
        ## Champ de saisie du nom 
        l = Label(self, text="Nouveau pilote:", font = "Arial 14 underline")
        l.grid(column=2, row=0, columnspan=2, sticky="W")

        Label(self, text="Nom:").grid(column=2, row=1, sticky="W")

        self.pilot = StringVar()
        e = Entry(self, textvariable= self.pilot, bg="white")
        e.grid(column=3, row=1, sticky="W")

        ## icones
        useradd_icon = PhotoImage(file = os.path.join(images_path,
                                                      "user-new-3.gif"))
        userren_icon = PhotoImage(file = os.path.join(images_path,
                                                      "edit.gif"))
        userdel_icon = PhotoImage(file = os.path.join(images_path,
                                                      "user-delete-2.gif"))
        ## Bouton d'ajout d'utilisateur
        b = Button(self, text=" Ajouter", command=self.add_pilot,
                   image= useradd_icon, width=80, compound='left')
        b.image = useradd_icon
        b.grid(column=2, row=2, columnspan=2, sticky="EW")
        ## Bouton d'effacement de l'utilisateur
        b = Button(self, text=" Supprimer", command=self.delete_pilot,
                   image= userdel_icon, width=80, compound='left')
        b.image = userdel_icon
        b.grid(column=2, row=3, columnspan=2, sticky="EW")
        ## Bouton de renommage d'un utilisateur
        b = Button(self, text=" Renommer", command=self.rename_pilot,
                   image= userren_icon, width=80, compound='left')
        b.image = userren_icon
        b.grid(column=2, row=4, columnspan=2, sticky="EW")

        ## Message d'erreur eventuel
        self.errmsg = StringVar()
        Label(self, textvariable=self.errmsg, fg='red').grid(column=0, row=5,
                                                             columnspan=5)
        ## Bouton OK pour quitter le menu
        b = Button(self, text="OK", pady=5, width=15, command=self.doDestroy)
        b.grid(column=0, row=6, columnspan=4)

        self.columnconfigure(0, pad=4, weight=2)
        self.columnconfigure(1, pad=2)
        self.columnconfigure(2, pad=6)
        self.columnconfigure(3, pad=6, weight=1)    
        self.rowconfigure(0, pad=4)      
        self.rowconfigure(1, pad=4)     
        self.rowconfigure(2, pad=4)     
        self.rowconfigure(3, pad=4)     
        self.rowconfigure(4, pad=4)     
        self.rowconfigure(5, pad=4)      
        self.rowconfigure(6, pad=4)   
        

    def load_existing_pilots(self):
        '''Get list of pilots database files'''
        # Effacement de la liste des pilotes
        self.lbox.delete(0,'end')

        # Recherche des fichiers de base de donnees
        self.list_pilots = glob.glob(os.path.join(db_path, '*'))   
        self.list_pilots.sort()    

        # Remplissage de la liste des pilotes
        for pilot in self.list_pilots:
            self.lbox.insert('end', os.path.basename(pilot))

        # Mise a jour du menu de selection des pilotes
        if self.parent is not None:
            self.parent.menupilotes.delete(0, 'end')
            self.parent.populate_menu_pilotes()

    def add_pilot(self):
        '''Ajout d'un pilote, creation de sa base de donnees.
        (une table pour les vols, une table pour les ailes, une table pour
        les decollages et une table pour les atterrissages.'''
        self.errmsg.set("")
        pilot = self.pilot.get()
        if pilot:
            filename = os.path.join(db_path, pilot)
            if filename in self.list_pilots:
                self.errmsg.set("Ce pilote existe déjà !")
                self.focus_set() 
                return               
            try:
                conn = sqlite3.connect(filename)
                cur = conn.cursor()
                cur.execute( '''CREATE TABLE vols (
                                       vid integer primary key,
                                       annee integer,
                                       mois integer,
                                       jour integer,
                                       heure text,
                                       deco text,
                                       atterro text,
                                       aile text,
                                       type_vol text,
                                       parcours text,
                                       duree integer,
                                       distance_parcours integer,
                                       distance_totale integer,
                                       alti_max integer,
                                       alti_min integer,
                                       gain_max integer,
                                       gain_total integer,
                                       vario_max real,
                                       vario_min real,
                                       encadrement text,
                                       compagnons text,
                                       recit text,
                                       note integer,
                                       vol_sur_parawing integer)''' )
                cur.execute( '''CREATE TABLE ailes (
                                       aid integer primary key,
                                       modele text,
                                       marque text,
                                       date_achat text,
                                       date_revision text,
                                       commentaires text)''' )
                cur.execute( '''CREATE TABLE decos (
                                       did integer primary key,
                                       deco text,
                                       latitude real,
                                       longitude real)''' )
                cur.execute( '''CREATE TABLE atterros (
                                       atid integer primary key,
                                       atterro text,
                                       latitude real,
                                       longitude real)''' )   
                cur.execute( '''CREATE TABLE cfd (
                                       annee integer primary key,
                                       classt_indiv integer,
                                       classt_club integer,
                                       classt_indiv_club integer,
                                       classt_feminin integer,
                                       classt_espoir integer,
                                       classt_biplace integer)''' )           
                conn.commit()
                conn.close()

            except:
                self.errmsg.set("Impossible d'ajouter le pilote. Vérifiez" +
                                " que le dossier\n" + db_path + "\nn'est pas" +
                                " en lecture seule et que le nom ne contient" +
                                "\npas de caracteres speciaux.")
                self.focus_set() 
                raise
        self.load_existing_pilots()
        
    def delete_pilot(self):
        '''Supprimer le pilote selectionne et sa base de donnees'''
        self.errmsg.set("")
        
        for i in self.lbox.curselection():
            confirmer = "Etes-vous sûr de vouloir supprimer le pilote "
            confirmer += os.path.basename(self.list_pilots[int(i)]) + " ?"
            if messagebox.askyesno(message=confirmer, icon='question',
                                   title="Confirmation de suppression"):
                try:
                    os.remove(self.list_pilots[int(i)])
                except:
                    self.errmsg.set("Impossible de supprimer le pilote " +
                                    os.path.basename(self.list_pilots[int(i)]))
                    self.focus_set()
                    raise
        self.focus_set()
        self.load_existing_pilots()               

    def rename_pilot(self):
        '''Renommer le pilote selectionne'''
        self.errmsg.set("")
        new_pilot_name = self.pilot.get()
        if new_pilot_name:
            for i in self.lbox.curselection():
                confirmer = "Etes-vous sûr de vouloir renommer\nle pilote "
                confirmer += os.path.basename(self.list_pilots[int(i)])
                confirmer += " en " + new_pilot_name + " ? Si un pilote de\n"
                confirmer += "ce nom existe il sera écrasé." 
                if messagebox.askyesno(message=confirmer, icon='question',
                                       title="Confirmation de renommage"):
                    try:
                        os.rename(self.list_pilots[int(i)],
                                  os.path.join(db_path, new_pilot_name))
                    except:
                        self.errmsg.set("Impossible de renommer le pilote en '"+
                                        new_pilot_name + "'. Vérifiez que le " +
                                        "dossier\n" + db_path + "\nn'est pas " +
                                        "en lecture seule et que le nouveau " +
                                        "nom ne\ncontient pas de caracteres " +
                                        "speciaux.")
                        self.focus_set()
                        raise
        self.focus_set()
        self.load_existing_pilots()

    def doDestroy(self):
        '''Quitter'''
        self.destroy()
        
if __name__ == '__main__':
    GestionPilotes().mainloop()
