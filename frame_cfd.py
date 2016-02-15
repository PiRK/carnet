#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Carnet de vol parapente - Affichage des classements CFD
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

from classement_cfd import ParserClassementG, ParserClassementClub

class FrameCFD(Frame):
    '''Statistiques extraites du carnet de vol       
    '''
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        
        self.db_connected = False       
        self.conn = None
        self.cur = None

        # Annee
        self.annee = StringVar()
        # Club
        self.club = StringVar()
        # Nom du pilote
        self.nom_pilote = StringVar()

        f0 = Frame(self, bd=3)
        # liste déroulante année
        self.cb_annee = ComboBox(f0, label="Année", dropdown=1, editable=1,
                                 bg="white", variable=self.annee, listwidth=30)
        self.cb_annee.entry.config(width=8, bg='white')
        self.cb_annee.pack(side='left')

        # club
        Label(f0, text="Club :").pack(side='left')
        e = Entry(f0, bg="white", textvariable=self.club)
        e.pack(side='left', expand=1, fill=tkinter.tix.X)
        # pilote
        l = Label(f0, text="Nom du pilote :").pack(side='left')
        e = Entry(f0, bg="white", textvariable=self.nom_pilote)
        e.pack(side='left', expand=1, fill=tkinter.tix.X)
        # bouton OK        
        b = Button(f0, text="OK", command=self.on_button_click)
        b.pack(side='left')
        f0.pack(side='top', expand=1, fill=tkinter.tix.X)
        

        f1 = Frame(self, bd=3)
        f11 = Frame(f1, bd=3)
        yscr_g = Scrollbar(f11, orient='vertical')
        yscr_g.pack(side="right", fill=tkinter.tix.Y)
        self.classement_g = Text(f11, wrap='none',  yscrollcommand=yscr_g.set,
                                 bg = 'white', width=50)
        self.classement_g.insert('1.0', 'Classement général :\n')
        self.classement_g.tag_add('titre', '1.0', '2.0 - 1 chars')                        
        self.classement_g.tag_config('titre', font=('times', 16, 'underline'),
                                     justify='center', foreground='blue') 
        self.classement_g.pack(expand=1, fill=tkinter.tix.BOTH)
        yscr_g.config(command=self.classement_g.yview)
        f11.pack(side="left", expand=1, fill=tkinter.tix.BOTH)
        

        f12 = Frame(f1, bd=3)
        yscr_c = Scrollbar(f12, orient='vertical')
        yscr_c.pack(side="right", fill=tkinter.tix.Y)
        self.classement_c = Text(f12, wrap='none',  yscrollcommand=yscr_c.set,
                                 bg = 'white', width=40)
        self.classement_c.insert('1.0', 'Classement club :\n')
        self.classement_c.tag_add('titre', '1.0', '2.0 - 1 chars')                        
        self.classement_c.tag_config('titre', font=('times', 16, 'underline'),
                                     justify='center', foreground='blue') 
        self.classement_c.pack(expand=1, fill=tkinter.tix.BOTH)
        yscr_c.config(command=self.classement_c.yview)
        
        f12.pack(side="right", expand=1, fill=tkinter.tix.BOTH)

        f1.pack(side='bottom', expand=1, fill=tkinter.tix.BOTH)
        
    def on_pilot_selection(self, conn):
        '''Fonction executee lorsqu'un pilote est selectionne

         Chargement des informations a partir de sa base de donnees'''

        self.db_connected = True
        self.conn = conn
        self.cur = self.conn.cursor()

        # Vérification de l'existence de la base de données
        req = '''CREATE TABLE IF NOT EXISTS nom_club_pilote (
                     id integer primary key,
                     nom text,
                     club text)'''
        self.cur.execute(req)

        self.prefill_entries()

    def prefill_entries(self):
        '''Recuperer les données par défaut du pilote dans la base de données
        (nom du pilote, club) et remplir la liste déroulante des saisons de
        2000-2001 à la saison en cours.
        '''
        if not self.db_connected:
            return

        self.cur.execute('''SELECT nom, club
                         FROM nom_club_pilote
                         WHERE id = 1''')
        tmp = self.cur.fetchall()
        if tmp:
            nom, club = tmp[0]
            self.nom_pilote.set(nom)
            self.club.set(club)

        now = datetime.datetime.now()
        # Début de la saison en septembre
        if now.month >= 9:
            self.cb_annee.insert(tkinter.tix.END, str(now.year))
            self.annee.set(str(now.year))
        else:
            self.annee.set(str(now.year - 1))
        for y in range(now.year-1, 1999, -1):
            self.cb_annee.insert(tkinter.tix.END, str(y))

        
    def on_button_click(self):
        '''Récupérer les classements CFD pour l'année, le pilote et le club
        spécifiés. Mettre à jour le nom du pilote et le club dans la base
        de données avec les valeurs saisies. Afficher les classements.'''
        if not self.db_connected:
            return

        req = '''INSERT OR REPLACE INTO nom_club_pilote VALUES (1, ?, ?)'''
        self.cur.execute(req, (self.nom_pilote.get(), self.club.get()))

        classementG = ParserClassementG(self.annee.get(),
                                        self.club.get(),
                                        self.nom_pilote.get()).get_classement()
        self.classement_g.delete('2.0', 'end')
        self.classement_g.insert('end', '\n\n')
        # tag pour style gras
        self.classement_g.tag_config('b', font=('monospace', 8, 'bold'))
        # tag pour style normal
        self.classement_g.tag_config('n', font=('monospace', 8)) 
        for pilote in classementG:
            line = "%-4s %-30s %-40s %s\n" % pilote
            if pilote[1].lower() == self.nom_pilote.get().lower():
                tag = 'b'
            else:
                tag = 'n'
            self.classement_g.insert('end', line, tag)
        
        classementClub = ParserClassementClub(self.annee.get(),
                                              self.club.get()).get_classement()
        self.classement_c.delete('2.0', 'end')
        self.classement_c.insert('end', '\n\n')
        # tag pour style gras
        self.classement_c.tag_config('b', font=('monospace', 8, 'bold'))
        # tag pour style normal
        self.classement_c.tag_config('n', font=('monospace', 8))
        for club in classementClub:
            line = "%-4s %-50s %-3s %s\n" % (club[0:2] + club[3:])
            if club[1].lower() == self.club.get().lower():
                self.classement_c.insert('end', line, 'b')
            else:
                self.classement_c.insert('end', line, 'n')
        

if __name__ == '__main__':
    root = Tk()
    FrameCFD(root).pack()
    root.mainloop()

