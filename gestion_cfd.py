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

from tkinter.tix import *
from tkinter import messagebox

images_path = os.path.join(os.path.dirname(sys.argv[0]), 'images')

class GestionCFD(Toplevel):
    '''Interface de gestion de la base de donnees du classment CFD.
    L'utilisateur peut saisir pour chaque annee ses classements.'''
    def __init__(self, parent=None, modele = "", conn = None,
                 cur = None):
        Toplevel.__init__(self, parent, takefocus=True)
            
        self.parent = parent
        
        self.annee = IntVar()
        self.classt_indiv = StringVar()
        self.classt_indiv_dans_club = StringVar()
        self.classt_club = StringVar()
        self.classt_feminin = StringVar()
        self.classt_espoir = StringVar()
        self.classt_biplace = StringVar()  
        
        self.conn = conn
        self.cur = cur

        self.protocol("WM_DELETE_WINDOW", self.doDestroy)       
        self.grid()
        
        self.errmsg = StringVar()
        if conn is None:
            err = "Vous n'etes actuellement connecté a aucune base de données."
            err += "\nVous devez sélectionner un pilote pour gérer ses "
            err += "classements CFD."
            self.errmsg.set(err)
            self.gui_not_connected()
        else:
            self.gui_connected()

    def gui_not_connected(self):
        '''Si on n'est pas connecté a une bdd, afficher un message d'erreur
        et un bouton "OK" pour quitter ce menu.
        '''
        l = Label(self, textvariable=self.errmsg, fg = 'red')
        l.grid(column=0, row=0)
        b = Button(self, text="OK", command=self.destroy)
        b.grid(column=0, row=1)

    def gui_connected(self):
        '''Interface de saisie/modif des classements'''
        
        #titre
        l = Label(self, text="Classements CFD :",
                  font = "Arial 14 underline")
        l.grid(column=0, row=0, columnspan=4, sticky="W")
        
        ## Liste des annees
##        self.cb_annee = ComboBox(self, label="Année", dropdown=1, editable=1,
##                                 variable = self.annee, listwidth = 20,
##                                 command = self.select_annee)
##        self.cb_annee.entry.config(width=5, bg='white')       
##        self.cb_annee.grid(column=0, row=1, sticky="W")
        l = Label(self, text="Année :")
        l.grid(column=0, row=1, sticky="W")
        e = Entry(self, textvariable= self.annee, bg="white")
        e.grid(column=1, row=1, sticky="EW")
        e.bind("<Return>", self.select_annee)
        e.bind('<KP_Enter>', self.select_annee)

        b = Button(self, text="Charger", command=self.select_annee)
        b.grid(column=2, row=1)


        ## Formulaire saisie des classments
        l = Label(self, text="Classement général\nindividuel :")
        l.grid(column=0, row=2, sticky="W")
        e = Entry(self, textvariable= self.classt_indiv, bg="white")
        e.grid(column=1, row=2, sticky="EW")
        
        l = Label(self, text="Classement du club :")
        l.grid(column=2, row=2, sticky="W")
        e = Entry(self, textvariable= self.classt_club, bg="white")
        e.grid(column=3, row=2, sticky="EW")
        
        l = Label(self, text="Classement individuel\nintra-club :")
        l.grid(column=0, row=3, sticky="W")
        e = Entry(self, textvariable= self.classt_indiv_dans_club, bg="white")
        e.grid(column=1, row=3, sticky="EW")
        
        l = Label(self, text="Classement féminin :")
        l.grid(column=2, row=3, sticky="W")
        e = Entry(self, textvariable= self.classt_feminin, bg="white")
        e.grid(column=3, row=3, sticky="EW")
        
        l = Label(self, text="Classement espoir :")
        l.grid(column=0, row=4, sticky="W")
        e = Entry(self, textvariable= self.classt_espoir, bg="white")
        e.grid(column=1, row=4, sticky="EW")
        
        l = Label(self, text="Classement biplace :")
        l.grid(column=2, row=4, sticky="W")
        e = Entry(self, textvariable= self.classt_biplace, bg="white")
        e.grid(column=3, row=4, sticky="EW")
        
        ## Message d'erreur eventuel
        Label(self, textvariable=self.errmsg, fg='red').grid(column=0, row=5,
                                                             columnspan=4)
        ## Boutons
        save_icon = PhotoImage(file = os.path.join(images_path,
                                                   "document-export.gif"))
        quit_icon = PhotoImage(file = os.path.join(images_path,
                                                   "gtk-quit.gif"))
        b = Button(self, text=" Enregistrer", command=self.save,
                   image= save_icon, compound='left')
        b.image = save_icon
        b.grid(column=0, row=6, columnspan=2, sticky="EW")
        ###Bouton quitter 
        b = Button(self, text=" Quitter", command=self.doDestroy,
                   image= quit_icon, compound='left')
        b.image = quit_icon
        b.grid(column=2, row=6, columnspan=2, sticky="EW")    

        self.columnconfigure(0, pad=6)
        self.columnconfigure(1, pad=6)
        self.columnconfigure(2, pad=6)
        self.columnconfigure(3, pad=6)   
        self.rowconfigure(0, pad=10)      
        self.rowconfigure(1, pad=4)     
        self.rowconfigure(2, pad=4)     
        self.rowconfigure(3, pad=4)     
        self.rowconfigure(4, pad=4)     
        self.rowconfigure(5, pad=10)    
        self.rowconfigure(6, pad=4) 
        
        self.maj_annees()
    
    def maj_annees(self):
        '''Mise a jour de la liste des annees dans la combo box
        et stockage des classements dans self.liste_classt_bdd'''
        
        self.cur.execute('''SELECT * from cfd order by annee''')
        self.liste_classt_bdd = self.cur.fetchall()

##        self.cb_annee.slistbox.listbox.delete(0, 'end')
##        for item in self.liste_classt_bdd:
##            self.lbox.insert(tkinter.tix.END, item[0])

    def select_annee(self, *args):
        '''Selection d'une annee dans la combo box :
        charger tous les classements de cette annee dans les champs de saisie
        '''
        self.errmsg.set("")
        annee = self.annee.get()
        if annee:
            for item in self.liste_classt_bdd:
                if annee != item[0]:
                    continue
                else:
                    if item[1] is not None:
                        self.classt_indiv.set(str(item[1]))
                    else: self.classt_indiv.set('')
                    if item[2] is not None:
                        self.classt_club.set(str(item[2]))
                    else: self.classt_club.set('')
                    if item[3] is not None:
                        self.classt_indiv_dans_club.set(str(item[3]))
                    else: self.classt_indiv_dans_club.set('')
                    if item[4] is not None:
                        self.classt_feminin.set(str(item[4]))
                    else: self.classt_feminin.set('')
                    if item[5] is not None:
                        self.classt_espoir.set(str(item[5]))
                    else: self.classt_espoir.set('')
                    if item[6] is not None:
                        self.classt_biplace.set(str(item[6]))
                    else: self.classt_biplace.set('')     
                    

    def save(self, *args):
        '''Enregistrer les valeurs saisies pour une nouvelle annee
        ou modifier les valeurs pour une annee existante'''
        liste_annees = [item[0] for item in self.liste_classt_bdd]
       
        if self.annee.get() in liste_annees:
            self.edit_existing()
        else:
            self.add_new()
    
                               
    def add_new(self):
        '''Ajouter une nouvelle annee'''
        self.errmsg.set("")
        annee = self.annee.get()
        if annee:
            req = "INSERT INTO cfd VALUES (?, ?, ?, ?, ?, ?, ?)"

            try:
                indiv = int(self.classt_indiv.get())
            except:
                indiv = None
            try:
                club = int(self.classt_club.get())
            except:
                club = None
            try:
                indiv_club = int(self.classt_indiv_dans_club.get())
            except:
                indiv_club = None
            try:
                feminin = int(self.classt_feminin.get())
            except:
                feminin = None
            try:
                espoir = int(self.classt_espoir.get())
            except:
                espoir = None
            try:
                biplace = int(self.classt_biplace.get())
            except:
                biplace = None

            params = (annee, indiv, club, indiv_club, feminin, espoir, biplace)

            self.cur.execute(req, params)
            self.conn.commit()

            self.errmsg.set("Classements enregistrés avec succes")

            self.maj_annees()
        else:
            err = 'Vous devez remplir le champ "Année"'
            self.errmsg.set(err)
  
    def edit_existing(self):
        '''Enregistrer les champs saisis dans une annee existante
        '''
        
        self.errmsg.set("")
        
        annee = self.annee.get()
        if not annee:
            self.errmsg.set("Aucune année sélectionné")
            return

        confirmer = "Etes-vous sûr de vouloir modifier vos résultats CFD\n "
        confirmer += "de l'année %d ?" % (annee)        

        if not messagebox.askyesno(message=confirmer, icon='question',
                                   title="Confirmation"):       
            self.focus_set()
            return

        req =  "UPDATE cfd SET  classt_indiv = ?, classt_club = ?, "
        req += "classt_indiv_club = ?, classt_feminin = ?, classt_espoir = ?, "
        req += "classt_biplace = ? "
        req += "WHERE annee = ?"
    
        try:
            indiv = int(self.classt_indiv.get())
        except:
            indiv = None
        try:
            club = int(self.classt_club.get())
        except:
            club = None
        try:
            indiv_club = int(self.classt_indiv_dans_club.get())
        except:
            indiv_club = None
        try:
            feminin = int(self.classt_feminin.get())
        except:
            feminin = None
        try:
            espoir = int(self.classt_espoir.get())
        except:
            espoir = None
        try:
            biplace = int(self.classt_biplace.get())
        except:
            biplace = None

        params = (indiv, club, indiv_club, feminin, espoir, biplace, annee)
        
        self.cur.execute(req, params)
        self.conn.commit()
        self.errmsg.set("Classements enregistrés avec succes")
        self.maj_annees()
        self.focus_set()

    
    def doDestroy(self):
        '''Confirmer les modifications de la base de donnees et quitter'''
        if self.conn is not None:
            self.conn.commit()
        
        self.destroy()
        
if __name__ == '__main__':
    GestionCFD(conn = "4").mainloop()
