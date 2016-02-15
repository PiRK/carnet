#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   recuperation du classement general CFD des membres d'un club
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

import re
import urllib.request
import warnings


class CFDWarning(Warning):
    pass

classement_g_re = re.compile(
    r'''<td class="active">(\d+)</td>'''                       # classement
    r'''<td><a href="/pilote/\w+/\w+">(.+)</a></td>'''         # nom du pilote
    r'''<td><a href="/cfd/liste/\d+/club/\d+">(.+)</a></td>''' # club 
    r'''<td>(.)</td>'''                                        # nombre de vols
    r'''<td>([\d\.]+)</td>''')                                 # score


class ParserClassementG():
    '''
    Cette classe prend pour argument une annee (integer ou string) et un club
    puis récupère tous les résultats des pilotes du club dans une liste au
    format suivant :
    [(classement1, nom1, club1, score1), (classement2, nom2, club2, score2)...]
    Si aucun club n'est spécifié, l'ensemble du classement est récupéré.
    '''
    def __init__(self, annee, club=None, pilote=None):
        self.club = club
        self.pilote = pilote
        if type(annee) == type(int()):
            url = "http://parapente.ffvl.fr/cfd/classement/G/%d" % (annee)
        elif type(annee) == type(str()):
            url = "http://parapente.ffvl.fr/cfd/classement/G/" + annee.strip()
        else:
            raise TypeError("'annee' doit être un entier ou une chaine de " +
                            "caractères")
        f = urllib.request.urlopen(url)
        text = f.read().decode('utf-8')
        text = re.sub(r"&#039;", "'", text)  # recuperation des apostrophes

        self.classement = []
        self.classement_pilote = 0
        self.classement_pilote_club = 0
        self.npilotes = 0
        self.npilotes_club = 0
        self.process(text)

        if not self.classement:
            avertissement = "Aucun résultat trouvé sur le site de la Coupe "
            avertissement += " Fédérale de Distance pour l'année " + str(annee)
            if not club:
                avertissement += " et le club " + club + "."
            else:
                avertissement += "."
            warnings.warn(CFDWarning(avertissement))
            
        if not pilote and not self.classement_pilote:
            avertissement = "Aucun résultat trouvé pour le pilote " + pilote
            warnings.warn(CFDWarning(avertissement))
            
        
    def process(self, text):
        for line in text.split('\n'):
            m = classement_g_re.search(line)
            if m:
                self.npilotes += 1
                # si pas de club spécifié, récupérer tous les pilotes
                if not self.club:
                    self.classement.append(m.group(1,2,3,5))
                # sinon prendre seulement ceux du club
                else:
                    club = m.group(3)
                    if club.lower() == self.club.lower():
                        self.npilotes_club += 1
                        self.classement.append(m.group(1,2,3,5))
                        # récupérer les classements du pilote spécifié
                        if not self.pilote:
                            pilote = m.group(2)
                            if pilote.lower() == self.pilote.lower():
                                self.classement_pilote = int(m.group(1))
                                self.classement_pilote_club = self.npilotes_club
                        
                        

    def get_classement(self):
        '''Renvoie la liste des pilotes dans l'ordre du classement.
        Si un club est spécifié, seul les pilotes du club sont inclus dans la
        liste, sinon tous les pilotes de France sont inclus.'''
        return self.classement
    
    def get_classement_pilote(self):
        '''Cette fonction renvoie le classement général du pilote.
        Si aucun pilote n'est spécifié ou que le pilote spécifié n'a pas été
        trouvé dans le classement général, on renvoie 0'''
        return self.classement_pilote

    def get_classement_pilote_club(self):
        '''Cette fonction renvoie le classement du pilote dans son club.
        Si aucun pilote n'est spécifié ou que le pilote spécifié n'a pas été
        trouvé dans le classement général, on renvoie 0'''
        return self.classement_pilote_club

classement_club_re = re.compile(
    r'''<td>(\d+)</td>'''                                # classement
    r'''<td><a href="/cfd/liste/\d+/club/\d+">(.+)</a></td>''' # club 
    r'''<td>(\d+)</td>'''                             # pilotes total
    r'''<td>(\d+)</td>'''                        # pilotes classement
    r'''<td>.*</td><td>(\d+)</td>''')                        # points                       
      
class ParserClassementClub():
    '''
    Cette classe prend pour argument une annee (integer ou string) et un club
    puis récupère le classement des clubs pour l'année spécifié au format :
    [(classement1, club1, npilotes_total1, npilotes_classement1, points1),
    (classement2, club2, npilotes_total2, npilotes_classement2, points2)...]
    '''
    def __init__(self, annee, club=None):
        self.club = club
        if type(annee) == type(int()):
            url = "http://parapente.ffvl.fr/cfd/classement/club/%d" % (annee)
        elif type(annee) == type(str()):
            url = "http://parapente.ffvl.fr/cfd/classement/club/"+annee.strip()
        else:
            raise TypeError("'annee' doit être un entier ou une chaine de " +
                            "caractères")
        f = urllib.request.urlopen(url)
        text = f.read().decode('utf-8')
        text = re.sub(r"&#039;", "'", text)  # recuperation des apostrophes

        self.classement = []
        self.classement_club = 0
        self.nclubs = 0
        self.score_club = 0
        self.process(text)

        if not self.classement:
            avertissement = "Aucun résultat trouvé sur le site de la Coupe "
            avertissement += " Fédérale de Distance pour l'année " + str(annee)
            warnings.warn(CFDWarning(avertissement))
            
        if not club and not self.classement_club:
            avertissement = "Aucun résultat trouvé pour le club " + club
            warnings.warn(CFDWarning(avertissement))
            
        
    def process(self, text):
        for line in text.split('\n'):
            m = classement_club_re.search(line)
            if m:
                self.nclubs += 1
                self.classement.append(m.group(1,2,3,4,5))
                if not self.club:
                    club = m.group(2)
                    if club.lower() == self.club.lower():
                        self.classement_club = self.nclubs
                        self.score_club = float(m.group(5))
                        

    def get_classement(self):
        '''Renvoie la liste des club dans l'ordre du classement.'''
        return self.classement
    
    def get_classement_club(self):
        '''Cette fonction renvoie le classement général du club.
        Si aucun club n'est spécifié ou que le club spécifié n'a pas été
        trouvé dans le classement, on renvoie 0'''
        return self.classement_club

    def get_score_club(self):
        '''Cette fonction renvoie le score du club.
        Si aucun club n'est spécifié ou que le club spécifié n'a pas été
        trouvé dans le classement, on renvoie 0'''
        return self.score_club


        
if __name__ == '__main__':
    test = ParserClassementG(2010, "Les Tire-clous Du Grand Manti", "Pierre Knobel")
    print(test.classement)
    print(test.classement[test.classement_pilote_club - 1])
    test = ParserClassementClub(2010, "Les Tire-clous Du Grand Manti")
    print(test.classement)
    print(test.classement[test.classement_club - 1])
