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

class GestionAiles(Toplevel):
    '''Interface de gestion de la base de donnees des ailes.
    L'utilisateur peut ajouter, supprimer et modifier des ailes.
    Les infos d'une aile sont son nom (ou modele) (requis), sa marque,
    sa date d'achat, sa date de derniere revisio'''
    def __init__(self, parent=None, modele = "", conn = None,
                 cur = None):
        Toplevel.__init__(self, parent, takefocus=True)
            
        self.parent = parent
        
        self.modele = StringVar()
        self.modele.set(modele)
        self.marque  = StringVar()
        self.date_achat  = StringVar()
        self.date_revision  = StringVar()
        
        self.conn = conn
        self.cur = cur

        self.protocol("WM_DELETE_WINDOW", self.doDestroy)       
        self.grid()
        
        self.errmsg = StringVar()
        if conn is None:
            err = "Vous n'etes actuellement connecté a aucune base de données."
            err += "\nVous devez sélectionner un pilote pour gérer ses "
            err += "ailes."
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
        '''Interface de saisie/modif des ailes'''
        
        #DECOS
        l = Label(self, text="Ailes :",
                  font = "Arial 14 underline")
        l.grid(column=0, row=0, columnspan=6, sticky="W")
        
        ## Liste des ailes      
        yscr_lb = Scrollbar(self, orient='vertical')
        yscr_lb.grid(column=1, row=1, rowspan=3, sticky='NSW')

        self.lbox = Listbox(self, bg="white", yscrollcommand=yscr_lb.set,
                              selectmode="single", height=5)
        self.lbox.grid(column=0, row = 1, rowspan=3, sticky="NSEW")
        yscr_lb.config(command=self.lbox.yview)
        
        self.lbox.bind("<Double Button-1>", self.select_aile)

        ## Formulaire saisie des ailes
        Label(self, text="Modèle:").grid(column=2, row=1, sticky="W")
        e = Entry(self, textvariable= self.modele, bg="white")
        e.grid(column=3, row=1, sticky="EW")

        Label(self, text="Marque :").grid(column=4, row=1, sticky="W")
        e = Entry(self, textvariable= self.marque, bg="white")
        e.grid(column=5, row=4, sticky="EW")
    
        Label(self, text="Date d'achat :").grid(column=2, row=2, sticky="W")
        e = Entry(self, textvariable= self.date_achat, bg="white")
        e.grid(column=3, row=2, sticky="W")
        
        l = Label(self, text="Date dernière\nrévision :")
        l.grid(column=4, row=2, sticky="W")
        e = Entry(self, textvariable= self.date_revision, bg="white")
        e.grid(column=5, row=2, sticky="EW")

        Label(self, text="Divers :").grid(column=2, row=3, sticky="W")
        self.commentaires = Text(self, wrap='word', width=40, height=3,
                                 bg="white")
        self.commentaires.grid(column=3, row=3,columnspan=3, sticky="EW")
        
        
        ## Boutons
        add_icon = PhotoImage(file = os.path.join(images_path,
                                                  "list-add.gif"))
        edit_icon = PhotoImage(file = os.path.join(images_path,
                                                   "edit.gif"))
        del_icon = PhotoImage(file = os.path.join(images_path,
                                                  "list-remove.gif"))

        ###Bouton d'ajout 
        b = Button(self, text=" Ajouter", command=self.add_aile,
                   image= add_icon, compound='left')
        b.image = add_icon
        b.grid(column=2, row=4, columnspan=2, sticky="EW")
        ###Bouton de modif 
        b = Button(self, text=" Modifier l'aile", command=self.edit_aile,
                   image= edit_icon, compound='left')
        b.image = edit_icon
        b.grid(column=4, row=4, columnspan=2, sticky="EW")    
        ###Bouton de suppression deco
        b = Button(self, text=" Supprimer l'aile", command=self.del_aile,
                   image= del_icon, compound='left')
        b.image = del_icon
        b.grid(column=3, row=5, columnspan=2, sticky="EW")

        Label(self, textvariable=self.errmsg, fg='red').grid(column=0, row=6,
                                                             columnspan=6)

        b = Button(self, text="OK", pady=5, width=15, command=self.doDestroy)
        b.grid(column=0, row=7, columnspan=6)


        self.columnconfigure(0, pad=4, weight=2)
        self.columnconfigure(1, pad=2)
        self.columnconfigure(2, pad=6)
        self.columnconfigure(3, pad=6)   
        self.columnconfigure(4, pad=6)  
        self.columnconfigure(5, pad=6)  
        self.rowconfigure(0, pad=4)      
        self.rowconfigure(1, pad=4)     
        self.rowconfigure(2, pad=4)     
        self.rowconfigure(3, pad=4)     
        self.rowconfigure(4, pad=4)     
        self.rowconfigure(5, pad=4)      
        self.rowconfigure(6, pad=4) 
        self.rowconfigure(7, pad=4)
        
        self.maj_ailes()

    def maj_ailes(self):
        '''Mise a jour de la liste des ailes  '''
        self.cur.execute('''SELECT * from ailes order by modele''')
        self.liste_ailes_bdd = self.cur.fetchall()

        self.lbox.delete(0, 'end')
        for item in self.liste_ailes_bdd:
            self.lbox.insert(tkinter.tix.END, item[1])

    def select_aile(self, *args):
        '''Un double clic sur une aile dans la liste lance cette fonction qui
        met a jour les champs'''
        self.errmsg.set("")
        for i in self.lbox.curselection():
            aile = self.liste_ailes_bdd[int(i)]
            self.aid = aile[0]
            if aile[1] is not None:
                self.modele.set(aile[1])
            if aile[2] is not None:
                self.marque.set(aile[2])
            else:
                self.marque.set("")
            if aile[3] is not None:
                self.date_achat.set(aile[3])
            else:
                self.marque.set("")
            if aile[4] is not None:
                self.date_revision.set(aile[4])
            else:
                self.marque.set("")
            self.commentaires.delete('1.0', 'end')
            if aile[5] is not None:
                self.commentaires.insert('1.0', aile[5])
                
                               
    def add_aile(self):
        '''Ajouter une aile a la base de donnees'''
        self.errmsg.set("")
        modele = self.modele.get().strip()
        if modele:
            req = "INSERT INTO ailes(modele, marque, date_achat, "
            req += "date_revision, commentaires) VALUES (?, ?, ?, ?, ?)"

            params = (self.modele.get(), self.marque.get(), 
                      self.date_achat.get(), self.date_revision.get(),
                      self.commentaires.get('1.0', 'end'))

            self.cur.execute(req, params)
            self.conn.commit()

            self.maj_ailes()
        else:
            err = "Vous devez fournir au moins le nom de l'aile"
            self.errmsg.set(err)
        
        
    def del_aile(self):
        '''Supprimer une aile de la base de donnees'''

        curselection = self.lbox.curselection()
        if not len(curselection):
            self.errmsg.set("Aucune aile sélectionnée")
            return
        
        aile = self.liste_ailes_bdd[int(curselection[0])]
        aid = aile[0]
        confirmer = "Etes-vous sûr de vouloir supprimer définitivement l'"
        confirmer += 'aile "%s" ?' % (aile[1])
        if messagebox.askyesno(message=confirmer, icon='question',
                               title="Confirmation"):
            req = "DELETE FROM ailes WHERE aid=?"

            self.cur.execute(req, (aid, ))
            self.maj_ailes()
            
        self.focus_set()

  
    def edit_aile(self):
        '''Enregistrer les champs saisis dans une aile existante
        '''
        self.errmsg.set("")
        
        curselection = self.lbox.curselection()
        if not len(curselection):
            self.errmsg.set("Aucune aile sélectionné")
            return

        aile = self.liste_ailes_bdd[int(curselection[0])]
        aid = aile[0]

        confirmer = "Etes-vous sûr de vouloir modifier l'aile"
        confirmer += ' "%s" ?' % (aile[1])
        

        if not messagebox.askyesno(message=confirmer, icon='question',
                                   title="Confirmation"):
            
            self.focus_set()
            return

        if self.modele.get().strip(): 
            req =  "UPDATE ailes SET  modele = ?, marque = ?, "
            req += "date_achat = ?, date_revision = ?, commentaires = ? "
            req += "WHERE aid = ?"
            
            params = (self.modele.get(), self.marque.get(), 
                      self.date_achat.get(), self.date_revision.get(),
                      self.commentaires.get('1.0', 'end'), aid)

            self.cur.execute(req, params)
            self.conn.commit()

            self.maj_ailes()
        else:
            err = "Vous devez fournir au moins le nom de l'aile"
            self.errmsg.set(err)

        self.focus_set()

    
    def doDestroy(self):
        '''Confirmer les modifications de la base de donnees et quitter'''
        if self.conn is not None:
            self.conn.commit()
        
        self.destroy()
        
if __name__ == '__main__':
    GestionAiles().mainloop()


