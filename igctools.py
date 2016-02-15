#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   igc parsing
#   source: igc2kmz/igc.py 
#   (http://github.com/twpayne/igc2kmz/blob/master/igc2kmz/igc.py)
#   Copyright (C) 2008  Tom Payne
#
#   Process total distance, duration, gain, max and min elevation, sampling
#   interval from an igc file
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

import datetime
import re
from units import time_conv, length_conv
from coord import Coord

A_RECORD_RE = re.compile(r'A(.*)\Z')
B_RECORD_RE = re.compile(r'B(\d{2})(\d{2})(\d{2})(\d{2})(\d{5})([NS])'
                         r'(\d{3})(\d{5})([EW])([AV])(\d{5})(\d{5}).*')
C_RECORD_RE = re.compile(r'C(\d{2})(\d{5})([NS])(\d{3})(\d{5})([EW])(.*)\Z')
E_RECORD_RE = re.compile(r'E(\d{2})(\d{2})(\d{2})(\w{3})(.*)\Z')
G_RECORD_RE = re.compile(r'G(.*)\Z')
HFDTE_RECORD_RE = re.compile(r'H(F)(DTE)(\d\d)(\d\d)(\d\d)')
HFFXA_RECORD_RE = re.compile(r'H(F)(FXA)(\d+)\Z')
H_RECORD_RE = re.compile(r'H([FOP])([A-Z]{3}).*?:(.*)\Z')
I_RECORD_RE = re.compile(r'(\d{2})(\d{2})(\w{3})\Z')
L_RECORD_RE = re.compile(r'L(.*)\Z')

def parseDate(line):
    m =  HFDTE_RECORD_RE.match(line)     
    if m:
        day, month, year = map(int, m.group(3, 4, 5))
        try:
           date = datetime.date(2000 + year, month, day)
        except ValueError:
           raise SyntaxError(line)
        return date
    return SyntaxError(line)

def parseB(line,trdate):                
    m = B_RECORD_RE.match(line)
    if not m:
        raise SyntaxError(line)
    time = datetime.time(*map(int, m.group(1, 2, 3)))
    dt = datetime.datetime.combine(trdate, time)
    lat = int(m.group(4)) + int(m.group(5)) / 60000.0
    if m.group(6) == 'S':
        result.lat *= -1
    lon = int(m.group(7)) + int(m.group(8)) / 60000.0
    if m.group(9) == 'W':
        lon *= -1
    validity = m.group(10)
    alt = int(m.group(11))
    elev = int(m.group(12))
    return (dt,lat,lon,alt,elev)

class IGCTrace:
    '''Tools for processing a gps trace in IGC format.
    '''
    def __init__(self, igcfname):
        self.fname = igcfname
        self.trace = []
        # Date
        self.date = datetime.date(2000,1,1)
        # Total distance in meters
        self.total_dist = 0
        # Time between first and last position in seconds
        self.duration = 0
        # Average sampling interval (s)
        self.sampling_interval = 0.
        # Maximum elevation
        self.max_elev = 0
        self.min_elev = 9999
        # Total altitude gain
        self.total_gain = 0
        # min and max climb rate
        self.max_vario = 0.
        self.min_vario = 0.

        self.process_file()

    def process_file(self):
        '''Extract the GPS trace from the file as a list of Coord objects,
        find the min and max elevation, the total distance in meters, the
        date and the duration of the flight in seconds.'''      
        igcf = open(self.fname)
        prev_coord = None        
        for line in igcf:
            if re.search('^HFDTE',line):
                # Date of the flight
                self.date = parseDate(line)
            if re.search('^B',line):
                (dt,lat,lon,alt,elev) = parseB(line,self.date)
                cur_coord = Coord(lat,lon,elev,dt)
                # GPS trace
                self.trace.append(cur_coord)
                # Min and max elevation
                if elev > self.max_elev:
                    self.max_elev = elev
                if elev < self.min_elev:
                    self.min_elev = elev
                if prev_coord is not None:
                    # Total distance
                    self.total_dist += prev_coord.distance_to(cur_coord)
                    # Total gain
                    gain = cur_coord.elev - prev_coord.elev
                    if gain > 0:
                        self.total_gain += gain
                    vario = gain / (cur_coord.dt.second - prev_coord.dt.second)
                    if vario > self.max_vario:
                        self.max_vario = vario
                    elif vario < self.min_vario:
                        self.min_vario = vario
                prev_coord = cur_coord

        # Flight duration in seconds
        delta_dt = self.trace[-1].dt - self.trace[0].dt 
        self.duration = delta_dt.seconds

        # Average sampling interval
        self.sampling_interval = self.duration / len(self.trace)

        # Number of points
        self.n = len(self.trace)
        igcf.close()

    def __repr__(self):
        representation = "File: " + self.fname + "\n"
        representation += "%d GPS positions (avg sampl interval: %.2f s)\n" % \
                                     (len(self.trace), self.sampling_interval)
        representation += "Duration: %d min\n" % (self.get_duration("min"))        
        representation += "Distance: %.3f km\n" % (self.get_total_dist("km"))
        representation += "Elevation range: %d-%d m\n" % (self.min_elev,
                                                          self.max_elev)
        representation += "Total gain: %d m\n" % (self.total_gain)
        representation += "Vario range: %.2f %.2f m/s\n" % (self.min_vario,
                                                            self.max_vario)
        #representation += "\t" + str(self.trace) + "\n"
        return representation

    def get_total_dist(self, unit="m"):
        '''Return distance in the specified unit. Default unit: meters.
        Other available units are km, m, mi, nmi, ft, yd, in.'''
        return length_conv(self.total_dist, unit)
    
    def get_duration(self, unit="s"):
        '''Return duration of flight in the specified unit. Default unit: s.
        Other available units are min, h, d.'''
        return time_conv(self.duration, unit)

    def get_max_elev(self, unit="m"):
        '''Return max elevation in specified unit. Default unit: m.'''
        return length_conv(self.max_elev, unit)

    def get_min_elev(self, unit="m"):
        '''Return min elevation. Default unit: m.'''
        return length_conv(self.min_elev, unit)

    def get_total_gain(self, unit="m"):
        '''Return min elevation. Default unit: m.'''
        return length_conv(self.total_gain, unit)

    def best_dl(self):
        '''Meilleure distance libre sans point de contournement'''
        self.DL = 0
        for i in range(0, self.n):
            for j in range(i+1, self.n):
                dij = self.trace[i].distance_to(self.trace[j])
                if dij > self.DL:
                    self.DL = dij
                    i0, j0 = (i, j)
        self.DL_BD = self.trace[i0]
        self.DL_BA = self.trace[j0]

## TROP LENT
    def best_dl1(self):
        '''Meilleure distance libre avec un point de contournement'''       
        self.DL1 = 0
        # Approx en decimant la trace
        for i in range(0, self.n, 10):
            for j in range(i+10, self.n, 10):
                for k in range(j+10, self.n, 10):
                    dijk = self.trace[i].distance_to(self.trace[j])
                    dijk += self.trace[j].distance_to(self.trace[k])
                    if dijk > self.DL1:
                        self.DL1 = dijk
                        i0, j0, k0 = (i, j, k)
        # On suppose que l'approx precedente etait proche du maximum global
        # et on affine.
        i1, j1, k1 = (i0, j0, k0)
        for i in range(i0-10, i0+10):
            if i < 0: continue
            for j in range(j0-10, j0+10):
                if j <= i: continue
                for k in range(k0-10, k0+10):
                    if k <= j or k >= self.n: continue
                    dijk = self.trace[i].distance_to(self.trace[j])
                    dijk += self.trace[j].distance_to(self.trace[k])
                    if dijk > self.DL1:
                        self.DL1 = dijk
                        i1, j1, k1 = (i, j, k)
        self.DL1_BD = self.trace[i1]
        self.DL1_B1 = self.trace[j1]
        self.DL1_BA = self.trace[k1]

    def best_dl2(self):
        '''Meilleure distance libre avec deux points de contournement.
        Avertissement : cette fonction prend plus de 10 minutes sur une
        trace de 2000 points'''
        n = len(self.trace)
        self.DL2 = 0
        # Approx en decimant
        for i in range(0, self.n, 10):
            for j in range(i+1, self.n, 10):
                for k in range(j+1, self.n, 10):
                    for l in range(k+1, self.n, 10):
                        dijkl = self.trace[i].distance_to(self.trace[j])
                        dijkl += self.trace[j].distance_to(self.trace[k])
                        dijkl += self.trace[k].distance_to(self.trace[l])                       
                        if dijkl > self.DL2:
                            self.DL2 = dijkl
                            (i0, j0, k0, l0) = (i, j, k, l)
        # affinage
        i1, j1, k1, l1 = (i0, j0, k0, l0)
        for i in range(i0-10, i0+10):
            if i<0:continue
            for j in range(j0-10, j0+10):
                if j<=i: continue
                for k in range(k0-10, k0+10):
                    if k<=j: continue
                    for l in range(l0-10, l0+10):
                        if l<=k or l >= self.n: continue
                        dijkl = self.trace[i].distance_to(self.trace[j])
                        dijkl += self.trace[j].distance_to(self.trace[k])
                        dijkl += self.trace[k].distance_to(self.trace[l])                       
                        if dijkl > self.DL2:
                            self.DL2 = dijkl
                            (i1, j1, k1, l1) = (i, j, k, l)
                            
        self.DL2_BD = self.trace[i1]
        self.DL2_B1 = self.trace[j1]
        self.DL2_B2 = self.trace[k1]
        self.DL2_BA = self.trace[l1]

    def find_BD_BA_pairs(self):
        '''Trouver tous les couples de points (BD, BA) tel que BD-BA < 3km.'''
        self.BD_BA_pairs = []
        for i in range(0, self.n):
            for j in range(i+1, self.n):
                if self.trace[i].distance_to(self.trace[j]) <= 3000:
                    self.BD_BA_pairs.append((i, j))

# Ne marche pas (et trop lent)
    def best_ar(self):
        '''Meilleur distance aller-retour'''
        self.AR = 0
        # Approx en decimant
        for i in range(0, self.n, 10):
            for j in range(i+10, self.n, 10):
                for k in range(j+10, self.n, 10):
                    for l in range(k+10, self.n, 10):
                        # Il faut moins de 3 km entre BD et BA
                        if self.trace[i].distance_to(self.trace[l]) > 3000:
                            continue
                        djk = 2 * self.trace[j].distance_to(self.trace[k])                       
                        if djk > self.AR:
                            self.AR = djk
                            (i0, j0, k0, l0) = (i, j, k, l)
        # affinage
        i1, j1, k1, l1 = (i0, j0, k0, l0)
        for i in range(i0-10, i0+10):
            if i<0:continue
            for j in range(j0-10, j0+10):
                if j<=i: continue
                for k in range(k0-10, k0+10):
                    if k<=j: continue
                    for l in range(l0-10, l0+10):
                        if l<=k or l >= self.n: continue
                        # Il faut moins de 3 km entre BD et BA
                        if self.trace[i].distance_to(self.trace[l]) > 3000:
                            continue
                        djk = 2 * self.trace[j].distance_to(self.trace[k])                       
                        if djk > self.AR:
                            self.AR = djk
                            (i1, j1, k1, l1) = (i, j, k, l)
    
        self.AR_BD = self.trace[i1]
        self.AR_B1 = self.trace[j1]
        self.AR_B2 = self.trace[k1]
        self.AR_BA = self.trace[l1]
        print(i1, j1, k1, l1)

if __name__ == '__main__':
    test = IGCTrace('/gcserv1d1/tmp/pierre/igc/pef.igc')
    print(test)
    print(test.date.year, test.date.month, test.date.day)
    print(test.trace[0].dt.hour,':',test.trace[0].dt.minute)
##    print("Date: " + str(test.date))
##    print("Duration: " + str(test.duration) + " seconds, " +
##          str(test.get_duration("min")) + " minutes, " +
##          str(test.get_duration("h")) + " hours, " +
##          str(test.get_duration("d")) + " days")
##    print("Distance: " + str(test.total_dist) + " m, " +
##          str(test.get_total_dist("km")) + " km, " +
##          str(test.get_total_dist("mi")) + " mi, " +
##          str(test.get_total_dist("ft")) + " ft")
##    print("Min elevation: " + str(test.min_elev) + " m, " +
##          str(test.get_min_elev("ft")) + " ft")
##    print("Max elevation: " + str(test.max_elev) + " m, " +
##          str(test.get_max_elev("ft")) + " ft")
##    print("Total gain: " + str(test.total_gain) + " m, " +
##          str(test.get_total_gain("ft")) + " ft")

##    t0 = datetime.datetime.now()
##    test.best_dl()
##    t1 = datetime.datetime.now()
##    print("DL: %.2f km (temps de calcul: %d s)" % (test.DL / 1000, (t1-t0).seconds))
##
##    t0 = datetime.datetime.now()
##    test.best_dl1()
##    t_ = (datetime.datetime.now() - t0).seconds
##    print("DL1: %.2f km (temps de calcul: %d s)" % (test.DL1 / 1000, t_))
##
##    t0 = datetime.datetime.now()
##    test.best_dl2()
##    t_ = (datetime.datetime.now() - t0).seconds
##    print("DL2: %.2f km (temps de calcul: %d s)" % (test.DL2 / 1000, t_))
##
##    t0 = datetime.datetime.now()
##    test.best_ar()
##    t_ = (datetime.datetime.now() - t0).seconds
##    print("AR: %.2f km (temps de calcul: %d s)" % (test.AR / 1000, t_))
