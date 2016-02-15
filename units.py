#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Fonctions de conversions de distance et temps

## Distance
def m2ft(dist_m):
   "Meters to feets"
   return dist_m / 0.3048

def m2yd(dist_m):
   "Meters to yard"
   return dist_m / 0.9144

def m2mi(dist_m):
   "Meters to miles"
   return dist_m / 1609.344

def m2nmi(dist_m):
   "Meters to nautical miles"
   return dist_m / 1852

def m2in(dist_m):
   "Meters to inches"
   return dist_m / 0.0254

def length_conv(l, unit="m"):
     '''Convert l (meters) into specified unit.'''
     if unit == "km":
         l_new = l / 1000
     elif unit == "m":
         l_new = l
     elif unit == "mi":
         l_new = m2mi(l)
     elif unit == "nmi":
         l_new = m2nmi(l)
     elif unit == "ft":
         l_new = m2ft(l)
     elif unit == "yd":
         l_new = m2yd(l)
     elif unit == "in":
         l_new = m2in(l)
     else:
         err_msg = "Illegal length unit " + unit + ". "
         err_msg += "Available units are km, m, mi, ft, in and yd."
         raise ValueError(err_msg)
     return l_new


## Temps
def s2min(time_sec):
   "Seconds to minutes"
   return time_sec / 60

def s2h(time_sec):
   "Seconds to hours"
   return time_sec / 3600

def s2d(time_sec):
   "Seconds to days"
   return time_sec / 86400

def time_conv(t, unit="s"):
     '''Return duration of flight in the specified unit. Default unit: s.
     Other available units are min, h, d.'''
     if unit == "min":
         t_new = s2min(t) 
     elif unit == "s":
         t_new = t 
     elif unit == "h":
         t_new = s2h(t) 
     elif unit == "d":
         t_new = s2d(t)
     else:
         err_msg = "Illegal time unit " + unit + ". "
         err_msg += "Available units are s, min, h and d."
         raise ValueError(err_msg)
     return t_new
