#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Carnet de vol parapente - Menu de gestion des sites
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

from coord import LatitudeLongitude

images_path = os.path.join(os.path.dirname(sys.argv[0]), 'images')

class GestionDecosAtterros(Toplevel):
    '''Interface de gestion des decos et atterros.

    L'utilisateur peut ajouter, supprimer et modifier des sites. Les
    informations qui caracterisent un site sont son nom (obligatoire),
    sa latitude et sa longitude'''

    def __init__(self, parent=None, deco = "", atterro = "", lat_d = 0,
                 lon_d = 0, lat_a = 0, lon_a = 0, conn = None,
                 cur = None):
        Toplevel.__init__(self, parent, takefocus=True)
            
        self.parent = parent
        
        self.deco = StringVar()
        self.deco.set(deco)
        self.atterro  = StringVar()
        self.atterro.set(atterro)
        # Latitude/longitude deco/atterro
        self.lat_d = StringVar()        
        self.lon_d = StringVar()        
        self.lat_a = StringVar()       
        self.lon_a = StringVar() 
        if lat_d > 0:
            self.lat_d.set(str(lat_d))
        else :
            self.lat_d.set("")
        if lon_d > 0:
            self.lon_d.set(str(lon_d))
        else :
            self.lon_d.set("")
        if lat_a > 0:
            self.lat_a.set(str(lat_a))
        else :
            self.lat_a.set("")
        if lon_a > 0:
            self.lon_a.set(str(lon_a))
        else :
            self.lon_a.set("")

        self.conn = conn
        self.cur = cur

        self.protocol("WM_DELETE_WINDOW", self.doDestroy)       
        self.grid()
        
        self.errmsg = StringVar()
        if conn is None:
            err = "Vous n'etes actuellement connecté a aucune base de données."
            err += "\nVous devez sélectionner un pilote pour gérer ses "
            err += "décollages et atterrissages."
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
        '''Interface de saisie/modif des decollages et atterrissages
        '''   
        #DECOS
        l = Label(self, text="Décollages :",
                  font = "Arial 14 underline")
        l.grid(column=0, row=0, columnspan=6, sticky="W")
        
        ## Liste des decollages       
        yscr_lbd = Scrollbar(self, orient='vertical')
        yscr_lbd.grid(column=1, row=1, rowspan=4, sticky='NSW')

        self.lbox_d = Listbox(self, bg="white", yscrollcommand=yscr_lbd.set,
                              selectmode="single", height=5)
        self.lbox_d.grid(column=0, row = 1, rowspan=4, sticky="NSEW")
        yscr_lbd.config(command=self.lbox_d.yview)
        
        self.lbox_d.bind("<Double Button-1>", self.select_deco)

        ## Formulaire saisie des decollages
        Label(self, text="Nom:").grid(column=2, row=1, sticky="W")
        e = Entry(self, textvariable= self.deco, bg="white")
        e.grid(column=3, row=1, columnspan=3, sticky="EW")

        Label(self, text="Latitude déco :").grid(column=2, row=2, sticky="W")
        e = Entry(self, textvariable= self.lat_d, bg="white")
        e.grid(column=3, row=2, sticky="W")
    
        Label(self, text="Longitude déco :").grid(column=4, row=2, sticky="W")
        e = Entry(self, textvariable= self.lon_d, bg="white")
        e.grid(column=5, row=2, sticky="W")

        ## Boutons
        add_icon = PhotoImage(file = os.path.join(images_path,
                                                  "list-add.gif"))
        edit_icon = PhotoImage(file = os.path.join(images_path,
                                                   "edit.gif"))
        del_icon = PhotoImage(file = os.path.join(images_path,
                                                  "list-remove.gif"))

        ###Bouton d'ajout deco
        b = Button(self, text=" Ajouter", command=self.add_deco,
                   image= add_icon, compound='left')
        b.image = add_icon
        b.grid(column=2, row=3, columnspan=2, sticky="EW")
        ###Bouton de modif deco
        b = Button(self, text=" Modifier décollage", command=self.edit_deco,
                   image= edit_icon, compound='left')
        b.image = edit_icon
        b.grid(column=4, row=3, columnspan=2, sticky="EW")    
        ###Bouton de suppression deco
        b = Button(self, text=" Supprimer décollage", command=self.del_deco,
                   image= del_icon, compound='left')
        b.image = del_icon
        b.grid(column=3, row=4, columnspan=2, sticky="EW")

        #ATTERROS
        l = Label(self, text="Atterrissages :",
                  font = "Arial 14 underline")
        l.grid(column=0, row=5, columnspan=6, sticky="W")

        ## Liste des atterrissages        
        yscr_lba = Scrollbar(self, orient='vertical')
        yscr_lba.grid(column=1, row=6, rowspan=4, sticky='NSW')

        self.lbox_a = Listbox(self, bg="white", yscrollcommand=yscr_lba.set,
                              selectmode="single", height=5)
        self.lbox_a.grid(column=0, row = 6, rowspan=4, sticky="NSEW")
        yscr_lba.config(command=self.lbox_a.yview)

        self.lbox_a.bind("<Double Button-1>", self.select_atterro)
        
        ## Formulaire saisie des atterrissages
        Label(self, text="Nom:").grid(column=2, row=6, sticky="W")
        e = Entry(self, textvariable= self.atterro, bg="white")
        e.grid(column=3, row=6, columnspan=3, sticky="EW")

        l = Label(self, text="Latitude atterro :")
        l.grid(column=2, row=7, sticky="W")
        e = Entry(self, textvariable= self.lat_a, bg="white")
        e.grid(column=3, row=7, sticky="W")
    
        l = Label(self, text="Longitude atterro :")
        l.grid(column=4, row=7, sticky="W")
        e = Entry(self, textvariable= self.lon_a, bg="white")
        e.grid(column=5, row=7, sticky="W") 

        ###Bouton d'ajout deco
        b = Button(self, text=" Ajouter", command=self.add_atterro,
                   image= add_icon, compound='left')
        b.image = add_icon
        b.grid(column=2, row=8, columnspan=2, sticky="EW")
        ###Bouton de modif deco
        b = Button(self, text=" Modifier atterrissage",
                   command=self.edit_atterro,
                   image= edit_icon, compound='left')
        b.image = edit_icon
        b.grid(column=4, row=8, columnspan=2, sticky="EW")    
        ###Bouton de suppression deco
        b = Button(self, text=" Supprimer atterrissage",
                   command=self.del_atterro,
                   image= del_icon, compound='left')
        b.image = del_icon
        b.grid(column=3, row=9, columnspan=2, sticky="EW")

        self.errmsg = StringVar()
        Label(self, textvariable=self.errmsg, fg='red').grid(column=0, row=10,
                                                             columnspan=6)

        b = Button(self, text="OK", pady=5, width=15, command=self.doDestroy)
        b.grid(column=0, row=11, columnspan=6)


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
        self.rowconfigure(8, pad=4)     
        self.rowconfigure(9, pad=4)     
        self.rowconfigure(10, pad=4)     
        self.rowconfigure(11, pad=4) 
        
        self.maj_decos_atterros()

    def maj_decos_atterros(self):
        '''Mise a jour de la liste des sites a partir des informations
        contenues dans la base de donnees.'''
        # DECOS:
        self.cur.execute('''SELECT * from decos order by deco''')
        self.liste_decos_bdd = self.cur.fetchall()

        self.lbox_d.delete(0, 'end')
        for item in self.liste_decos_bdd:
            self.lbox_d.insert(tkinter.tix.END, item[1])

        # ATTERROS:
        self.cur.execute('''SELECT * from atterros order by atterro''')
        self.liste_atterros_bdd = self.cur.fetchall()

        self.lbox_a.delete(0, 'end')
        for item in self.liste_atterros_bdd:
            self.lbox_a.insert(tkinter.tix.END, item[1])  

    def select_deco(self, *args):
        '''Un double clic sur un deco dans la liste lance cette fonction qui
        met a jour les champs Nom, Latitude et Longitude'''
        self.errmsg.set("")
        for i in self.lbox_d.curselection():
            deco = self.liste_decos_bdd[int(i)]
            self.did = deco[0]
            if deco[1] is not None:
                self.deco.set(deco[1])
            if deco[2] is not None:
                self.lat_d.set(str(deco[2]))
            else:
                self.lat_d.set("")
            if deco[3] is not None:
                self.lon_d.set(str(deco[3]))
            else:
                self.lon_d.set("")
                               
    def add_deco(self):
        '''Ajouter un site de decollage a la base de donnees.'''
        self.errmsg.set("")
        deco = self.deco.get().strip()
        if deco:
            try:
                lat_d = LatitudeLongitude(self.lat_d.get())
                lon_d = LatitudeLongitude(self.lon_d.get())
            except:
                self.errmsg.set("Format invalide pour la latitude " +
                                "ou la longitude.")
                raise
            else:
                req = "INSERT INTO decos(deco, latitude, longitude) "
                req += "VALUES (?, ?, ?)"
                lad = lat_d.decimal_degrees
                lod = lon_d.decimal_degrees

                self.cur.execute(req, (deco, lad, lod))
                self.conn.commit()

                self.maj_decos_atterros()
        else:
            err = "Vous devez fournir au moins le nom du site de décollage"
            self.errmsg.set(err)
        
        
    def del_deco(self):
        '''Supprimer un site de decollage de la base de donnees'''
        curselection = self.lbox_d.curselection()
        if not len(curselection):
            self.errmsg.set("Aucun deco sélectionné")
            self.focus_set()
            return
        
        deco = self.liste_decos_bdd[int(curselection[0])]
        did = deco[0]
        confirmer = "Etes-vous sûr de vouloir supprimer définitivement le "
        confirmer += 'site de décollage "%s" ?' % (deco[1])
        if messagebox.askyesno(message=confirmer, icon='question',
                               title="Confirmation"):
            req = "DELETE FROM decos WHERE did=?"

            self.cur.execute(req, (did, ))
            self.maj_decos_atterros()
            
        self.focus_set()

  
    def edit_deco(self):
        '''Enregistrer les champs saisis dans un deco existant (modification
        de la base de donnees)
        '''
        self.errmsg.set("")
        
        curselection = self.lbox_d.curselection()
        if not len(curselection):
            self.errmsg.set("Aucun site de décollage sélectionné")
            return

        deco = self.liste_decos_bdd[int(curselection[0])]
        did = deco[0]

        confirmer = "Etes-vous sûr de vouloir modifier le site de décollage"
        confirmer += ' "%s" ?' % (deco[1])
        

        if not messagebox.askyesno(message=confirmer, icon='question',
                                   title="Confirmation"):
            self.focus_set()
            return

        if self.deco.get().strip():
            try:
                lat_d = LatitudeLongitude(self.lat_d.get())
                lon_d = LatitudeLongitude(self.lon_d.get())
            except:
                self.errmsg.set("Format invalide pour la latitude " +
                                "ou la longitude.")
                raise
            else:
                req =  "UPDATE decos SET  deco = ?, latitude = ?, "
                req += "longitude = ? WHERE did = ?"
                
                lad = lat_d.decimal_degrees
                lod = lon_d.decimal_degrees

                self.cur.execute(req, (self.deco.get(), lad, lod, did))
                self.conn.commit()

                self.maj_decos_atterros()
        else:
            err = "Vous devez fournir au moins le nom du site de décollage"
            self.errmsg.set(err)
            
        self.focus_set()
            

    def select_atterro(self, *args):
        '''Un double clic sur un atterro dans la liste lance cette fonction
        qui met a jour les champs
        '''
        self.errmsg.set("")
        for i in self.lbox_a.curselection():
            atterro = self.liste_atterros_bdd[int(i)]
            self.atid = atterro[0]
            if atterro[1] is not None:
                self.atterro.set(atterro[1])
            if atterro[2] is not None:
                self.lat_a.set(str(atterro[2]))
            else:
                self.lat_a.set("")
            if atterro[3] is not None:
                self.lon_a.set(str(atterro[3]))
            else:
                self.lon_a.set("")
                
    def add_atterro(self):
        '''Ajouter un site d'atterrissage a la base de donnees'''
        self.errmsg.set("")
        atterro = self.atterro.get().strip()
        if atterro:
            try:
                lat_a = LatitudeLongitude(self.lat_a.get())
                lon_a = LatitudeLongitude(self.lon_a.get())
            except:
                self.errmsg.set("Format invalide pour la latitude " +
                                "ou la longitude.")
                self.focus_set()
                raise
            else:
                req = "INSERT INTO atterros(atterro, latitude, longitude) "
                req += "VALUES (?, ?, ?)"
                laa = lat_a.decimal_degrees
                loa = lon_a.decimal_degrees

                self.cur.execute(req, (atterro, laa, loa))
                self.conn.commit()

                self.maj_decos_atterros()
        else:
            err = "Vous devez fournir au moins le nom du site d'atterrisage"
            self.errmsg.set(err)
    
    def del_atterro(self):
        '''Supprimer un site d'atterrissage de la base de donnnes
        '''
        curselection = self.lbox_a.curselection()
        if not len(curselection):
            self.errmsg.set("Aucun atterro sélectionné")
            self.focus_set()
            return

        atterro = self.liste_atterros_bdd[int(curselection[0])]
        atid = atterro[0]
        
        confirmer = "Etes-vous sûr de vouloir supprimer définitivement le "
        confirmer += '''site d'atterrissage "%s" ?''' % (atterro[1])
        
        if messagebox.askyesno(message=confirmer, icon='question',
                               title="Confirmation"):
            req = "DELETE FROM atterros WHERE atid=?"

            self.cur.execute(req, (atid, ))
            self.maj_decos_atterros()
            
        self.focus_set()
            
    def edit_atterro(self):
        '''Enregistrer les champs saisis dans un atterro existant.
        (modification de la base de donnees)
        '''
        self.errmsg.set("")
        
        curselection = self.lbox_a.curselection()
        if not len(curselection):
            self.errmsg.set("Aucun site d'atterrissage sélectionné")
            self.focus_set()
            return

        atterro = self.liste_atterros_bdd[int(curselection[0])]
        atid = atterro[0]

        confirmer = "Etes-vous sûr de vouloir modifier le site d'atterrissage"
        confirmer += ' "%s" ?' % (atterro[1])

        if not messagebox.askyesno(message=confirmer, icon='question',
                                   title="Confirmation"):
            self.focus_set()
            return
        
        if self.atterro.get().strip():
            try:
                lat_a = LatitudeLongitude(self.lat_a.get())
                lon_a = LatitudeLongitude(self.lon_a.get())
            except:
                self.errmsg.set("Format invalide pour la latitude " +
                                "ou la longitude.")
                self.focus_set()
                raise
            else:
                req =  "UPDATE atterros SET  atterro = ?, latitude = ?, "
                req += "longitude = ? WHERE atid = ?"
                
                laa = lat_a.decimal_degrees
                loa = lon_a.decimal_degrees

                self.cur.execute(req, (self.atterro.get(), laa, loa, atid))
                self.conn.commit()

                self.maj_decos_atterros()
        else:
            err = "Vous devez fournir au moins le nom du site d'atterrissage"
            self.errmsg.set(err)
            
        self.focus_set()

    
    def doDestroy(self):
        '''Confimer les modifications de la base de donnees et quitter le
        menu'''
        if self.conn is not None:
            self.conn.commit() 
        self.destroy()
        
if __name__ == '__main__':
    GestionDecosAtterros(conn="not none").mainloop()

