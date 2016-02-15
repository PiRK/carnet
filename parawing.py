#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Publication d'un vol sur carnet.parawing.net et import d'un fichier csv
#   Copyright (C) 2011  Pierre Knobel
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv, os, re, sys
import urllib.request
import http.cookiejar


login_url = "http://carnet.parawing.net/login.php"
insert_vol_url = "http://carnet.parawing.net/insert_vol.php"
url_get_aile = 'http://carnet.parawing.net/serv_get_aile?'
url_get_site = 'http://carnet.parawing.net/serv_get_site?'

# Bac a sable pour les tests. En production, decommenter les lignes precedentes
#login_url = "http://bacasable.parawing.net/login.php"
#insert_vol_url = "http://bacasable.parawing.net/insert_vol.php"
#url_get_aile = 'http://bacasable.parawing.net/serv_get_aile?'
#url_get_site = 'http://bacasable.parawing.net/serv_get_site?'

def submit2parawing(login, pwd, jour, mois, annee, duree, deco = "",
                       atterro = "", aile = "", type_vol = "", heure = "",
                       distance = "",  alt_max = "", pt_bas = "", gain_max= "",
                       gain_total = "", cadre="", compagnons = "", recit = "",
                       note = "3", visible = "off"):
    '''Fonction qui soumet un vol sur parawing.net. Tous les parametres doivent
    etre des chaines de caracteres unicodes.

    La fonction renvoie un message d'erreur ou de succes'''

    # Ne pas publier un vol sur parawing si python < 3.2
    # (problèmes d'encodage avec python 3.1 et linux)
    if sys.version_info[0] == 3 and sys.version_info[1] < 2:
        return "Python 3.2 ou plus récent requis pour cette fonction."

    # Connexion au carnet Parawing
    login_data = urllib.parse.urlencode({'login' : login,
                                         'pass' : pwd})
        
    cj = http.cookiejar.CookieJar()
    cp = urllib.request.HTTPCookieProcessor(cj)
    paraw_opener = urllib.request.build_opener(cp)

    resp = paraw_opener.open(login_url, login_data.encode('iso-8859-1'))
    test = resp.read().decode('iso-8859-1')
    
    if 'Login ou mot de passe incorrect.' in test:
        return "Login ou mot de passe incorrect !"
    elif not 'vol.php' in test:
        return "Echec de la connexion, raison inconnue."

    # Prepartion de la requete HTTP POST pour soumettre le vol
    ## Conversion type_vol en code vol parawing
    types_vols =  {"Plouf":"20", "Vol thermique sur site":"40", 
                   'Gonflage':'1', 'Vol rando':'60', '':'20',
                   "Cross":"50", "Rando & cross":"50", "SIV":'80',
                   'Treuil':'70', 'Voltige':'95', 'Vol à ski':'61',
                   'Speedriding':'62', 'Soaring':'255',
                   'Compétition':'97'}
    cadres = {"Autonome":'4', "Entre potes":'3', 'Club':'2', 'Ecole':'1',
              '':'4'}

    if cadre not in cadres:
        raise ValueError("Le parametre 'cadre' ne peut prendre que les "
                         "valeurs suivante : '" +
                         "', '".join(cadres.keys()) + "'.")
    if type_vol not in types_vols:
        raise ValueError("Le parametre 'type_vol' ne peut prendre que les "
                         "valeurs suivantes : '" +
                         "', '".join(types_vols.keys()) + "'.")

    ## Creation de la liste des parametres
    np = "Vol ajouté avec le carnet python3"

    vol = {'jour': jour,
           'mois': mois,
           'annee': annee,
           'duree': duree,
           'type':types_vols[type_vol],
           'heure': heure.encode('iso-8859-1'),
           'distance': distance,
           'alt_max': alt_max,
           'pt_bas': pt_bas,
           'gain_max': gain_max,
           'gain_total': gain_total,
           'cadre': cadres[cadre],
           'compagnons': compagnons.encode('iso-8859-1'),
           'recit': recit.encode('iso-8859-1'),
           'ma_note': note,
           'notes_perso': np.encode('iso-8859-1'),
           'visible': visible,
           'flag_aile':'1', 'flag_site':'1', 'flag_site_atterro':'1',
           'choix':'Ajouter'}

    ## Verification si l'aile, le deco ou l'atterro sont deja enrgistres sur
    ## parawing et ajustement des parametres en consequence 
    data_aile = urllib.parse.urlencode({'pilote':login, 'key':'cavole'})
    webfile_aile = urllib.request.urlopen(url_get_aile + data_aile)
    liste_ailes = webfile_aile.read().decode('iso-8859-1')

    if aile in liste_ailes:
        vol['aile'] = aile.encode('iso-8859-1')
    else:
        vol['newaile'] = aile.encode('iso-8859-1')

    data_deco = urllib.parse.urlencode({'pilote':login, 'type':'d', 'key':'cavole'})
    webfile_deco = urllib.request.urlopen(url_get_site + data_deco)
    liste_decos = webfile_deco.read().decode('iso-8859-1')

    if deco.lower() in liste_decos.lower():
        vol['site'] = deco.encode('iso-8859-1')
    else:
        vol['newsite'] = deco.encode('iso-8859-1')
        
    data_atterro = urllib.parse.urlencode({'pilote':login, 'type':'a',
                                           'key':'cavole'})
    webfile_atterro = urllib.request.urlopen(url_get_site + data_atterro)
    liste_atterros = webfile_atterro.read().decode('iso-8859-1')

    if atterro.lower() in liste_atterros.lower():
        vol['site_atterro'] = atterro.encode('iso-8859-1')
    else:
        vol['newsite_atterro'] = atterro.encode('iso-8859-1')

    # Publication du vol (requete POST)
    data = urllib.parse.urlencode(vol)
    resp = paraw_opener.open(insert_vol_url, data.encode('iso-8859-1'))
    #resp = paraw_opener.open(insert_vol_url, data)

    test = resp.read().decode('iso-8859-1')
    
    if not "Le vol est enregistr&eacute; dans votre carnet." in test:
        print(test)
        return "Echec de la publication du vol sur Parawing"

    ret = "Publication réussie sur parawing."
    if 'Un nouveau site de decollage' in test:
        ret += "\nNouveau décollage ajouté à votre carnet parawing."
    if 'Une nouvelle aile' in test:
        ret += "\nNouvelle aile ajoutée à votre carnet parawing."
    if "Un nouveau site d'atterrissage" in test:
        ret += "\nNouvel atterrissage ajouté à votre carnet parawing."
    if "donnant votre avis sur votre aile !":
        ret += "\nConnectez vous sur Parawing.net et participez à l'"
        ret += "amélioration des données en donnant votre avis sur votre aile !"
    return  ret


def parse_date(datestring):
    '''Cette fonction prend en parametre une date au format JJ/MM/AAA
    et renvoie une liste de 3 int [jour, mois, annee]
    '''
    # supprimer les eventuels espaces avant et apres la date
    datestring = datestring.strip()
    # tester le format
    if not re.match(r'\d\d/\d\d/\d\d\d\d', datestring.strip()):
        raise ValueError("Wrong format for date string. Should be DD/MM/YYYY")

    return datestring.split("/")

def parse_parawing_csv(filename):
    '''Lit un fichier CSV exporte depuis parawing et renvoie une liste de
    listes'''
    
    csv_reader = csv.reader(open(filename, newline='', encoding='iso-8859-14'),
                            delimiter=";")
    return list(csv_reader)

def csv2db(csv_filename, conn=None):
    '''Charge les vols du fichier csv_filename et les charge dans la base de
    donnees sqlite3 identifiee par sa connection conn (objet sqlite3.connect)
    '''
    if conn is not None:
        cur = conn.cursor()
    else:
        print("Pas de connexion bdd")

    # identifiant nouveau vol : incrementer l'identifiant max
    # des vols existants ou choisir 1 si la table est vide
    req = "SELECT MAX(vid) FROM vols"
    cur.execute(req)
    max_vid_list = cur.fetchall()
    if len(max_vid_list):
        if max_vid_list[0][0] is not None:
            vid = max_vid_list[0][0] + 1
        else :
            vid = 1
    else :
        vid = 1

    vols = parse_parawing_csv(csv_filename)

    # Correspondances type de vol avec ceux proposes sur parawing
    types_vol = {'Plouf':'Plouf', 'Grand Vol':'Plouf',
                 'Vol local':'Vol thermique sur site', 'Cross':'Cross',
                 'Vol rando':'Vol rando', 'Gonflage':'Gonflage',
                 'Pente ecole':'Gonflage', 'BI Pédagogique':'Biplace',
                 'Triangle':'Cross', 'Triangle FAI':'Cross',
                 'Vol à ski':'Vol à ski', 'Speed riding':'Speedriding',
                 'Vol treuil':'Treuil', 'SIV':'SIV', 'Pilotage':'SIV',
                 'Seance voltige':'Voltige', 'Seance wagas':'Voltige',
                 'Competition A':'Compétition',
                 'Competition B':'Compétition'}
    
    for vol in vols:
        # la premiere ligne est une ligne de description du format
        if vol[0] == 'Date':
            continue
        # une ligne doit avoir 17 champs
        if len(vol) != 17:
            print("ligne corrompue:")
            print(vol)
            continue

        if vol[4] not in types_vol:
            type_vol = None
        else:
            type_vol = types_vol[vol[4]]
            
        jour, mois, annee = parse_date(vol[0])

        req =  "INSERT INTO vols VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?," 
        req += " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

        #Vol sur parawing (toujours vrai puisqu'on lit un export de parawing)
        vsp = 1

        params = (vid, annee, mois, jour, None, vol[1], vol[2], vol[3],
                  type_vol, None, vol[5], vol[6], None, vol[10], vol[11],
                  vol[12], vol[13], None, None, vol[15], vol[16],  None,
                  None, vsp)

        cur.execute(req, params)
        vid += 1
        
    conn.commit()       

if __name__ == '__main__':  
    print(submit2parawing(login = 'pirk',
                          pwd = 'fake',
                          jour = '18',
                          mois = '05',
                          annee = '2011',
                          duree = '911',
                          deco = "récupères",
                          atterro = "Lumbin",
                          aile = "USS Enterprise",
                          type_vol = "Speedriding",
                          heure = "Stardate 1313.5",
                          distance = "133",
                          alt_max = "9998",
                          pt_bas = "42",
                          gain_max= "1500",
                          gain_total = "16978",
                          cadre = "Entre potes",
                          compagnons = "Kirk et Picard",
                          recit = "tré",
                          note = "4",
                          visible = "on"))

##    jour, mois, annee = parse_date("11/09/2001")
##    print(jour, mois, annee)


