#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Carnet de vol parapente - Classes pour gerer les coordonnees GPS
# et les formats de latitude/longitude
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
from math import acos, asin, atan2, cos, pi, sin, sqrt, radians
import re

R = 6371000.0

class Coord():
    def __init__(self, lat, lon, elev=0., dt=None):
        self.lat = lat   #degree
        self.lon = lon   #degree
        self.elev = elev
        self.dt = dt
        
        self.lat_rad = radians(lat)
        self.lon_rad = radians(lon)

    def __repr__(self):
        representation = "(%.2f, %.2f, %d, %s)" % (self.lat, self.lon,
                                                   self.elev, self.dt)
        return representation
        
    def distance_to(self, other):
        """Return the distance from self to other."""
        d = sin(self.lat_rad) * sin(other.lat_rad) \
            + cos(self.lat_rad) * cos(other.lat_rad) \
            * cos(self.lon_rad - other.lon_rad)
        return R * acos(d) if d < 1.0 else 0.0
        
    def is_in_cylinder(self,center,radius,base_elev,top_elev):
        """Returns True if self is inside a cylinder centered
        on center (Coord object) with given radius, base elevation 
        and top elevation."""
        # Check elevation
        if self.elev < base_elev or self.elev > top_elev:
            return False
        # Check horizontal distance to center
        if self.distance_to(center) > radius :
            return False
        return True

def distance(A, B):
    '''Distance from point A=(latA, longA) to point B=(latB, longB)
    lat and long are in degrees.'''
    d = sin(radians(A[0])) * sin(radians(B[0])) \
       + cos(radians(A[0])) * cos(radians(B[0])) \
       * cos(radians(A[1]) - radians(B[1]))
    return R * acos(d) if d < 1.0 else 0.0

          
# DDD.DDDDD° format   
dec_deg_re = re.compile(r"^(-?\d+(\.\d*)?) *°? *([NSEW])?$")
# DDD° MM.MMM' format
deg_dec_min_re = re.compile(r"^(-?\d+) *° *(\d+(\.\d*)?) *' *([NSEW])?$")
# DDD° MM' SS.S'' format
deg_min_dec_sec_re = re.compile(r"""^(-?\d+) *° *(\d+) *' *(\d+(\.\d*)?) *(''|") *([NSEW])?$""")

class LatitudeLongitude():
    '''Class handling a geographical latitude or longitude in various formats:
        - signed decimal degrees as a string (DDD.DDD°)
        - signed degrees and decimal minutes as a string (DDD° MM.MMM')
        - signed degrees, minutes and seconds as a string (DDD° MM' SS'')
        - signed degrees, minutes and decimals seconds as a string (DDD° MM' SS.SSS'')
        - any of the above variants unsigned with a trailing N, S, E or W
        - decimal degrees as a float

    Class attributes are:
        decimal_degres, radians, degrees, decimal_minutes, minutes,
        decimal_seconds, seconds'''
    def __init__(self, l):
        self.is_blank_string = False
        if not type(l) == type(float()) and not type(l) == type(str()):
            raise TypeError("Latitude/longitude should be provided as a " +
                            "float or a string")            
        elif type(l) == type(float()):
            self.decimal_degrees = l
        elif type(l) == type(str()):           
            # DDD.DDDDD° format    
            if dec_deg_re.match(l.strip()):
                m = dec_deg_re.match(l.strip())
                self.decimal_degrees = float(m.group(1))
                if m.group(3) == 'S' or m.group(3) == 'W':
                    self.decimal_degrees *= -1
            # DDD° MM.MMM format
            elif deg_dec_min_re.match(l.strip()):
                m = deg_dec_min_re.match(l.strip())
                deg = int(m.group(1))
                mins = float(m.group(2))
                self.decimal_degrees = deg + mins/60
                if m.group(4) == 'S' or m.group(4) == 'W':
                    self.decimal_degrees *= -1
            # DDD° MM' SS.S" format
            elif deg_min_dec_sec_re.match(l.strip()):
                m = deg_min_dec_sec_re.match(l.strip())
                deg = int(m.group(1))
                mins = int(m.group(2))
                secs = float(m.group(3))
                self.decimal_degrees = deg + (mins + secs / 60) / 60
                if m.group(6) == 'S' or m.group(6) == 'W':
                    self.decimal_degrees *= -1
            elif l.strip() == '':
                self.is_blank_string = True
                self.decimal_degrees = None
            else:
                raise ValueError("Wrong format for latitude/longitude! Should " +
                                 "be: DDD.DDD° or DDD°MM.MMM' or DDD°MM'SS.S''")
            
        if self.is_blank_string:
            self.radians = None    
            self.degrees = None
            self.decimal_minutes = None
            self.minutes = None
            self.decimal_seconds = None
            self.seconds = None
            return
        
        self.radians = radians(self.decimal_degrees)     
        self.degrees = int(self.decimal_degrees)
        self.decimal_minutes = abs(self.decimal_degrees - self.degrees) * 60
        self.minutes = int(self.decimal_minutes)
        self.decimal_seconds = (self.decimal_minutes - self.minutes) * 60
        self.seconds = int(self.decimal_seconds)

    def __repr__(self):
        '''Return latitude or longitude as a string in the following format:
               DDD° MM' SS.SSS"
        '''
        if self.is_blank_string:
            rep = ""
        else:
            rep= '''{:3d}° {:2d}' {:6.3f}"'''.format(self.degrees,
                                                     self.minutes,
                                                     self.decimal_seconds)
        return rep
        

# Tests
if __name__ == '__main__':
    c = Coord(45.6, -123.45, 1337, datetime.datetime.now())
    print(c)
    l = LatitudeLongitude("35 °  20' 00.0'' W")
    print(l)
    print(l.decimal_degrees)
    
