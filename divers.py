#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

def cumul(ilist):
    '''Function takes a list of values [a0, a1, ...] as an argument and returns
    the list of same lenght [a0, a0 + a1, a0 + a1 + a2...]
    '''
    c = 0
    olist = []
    for item in ilist:
        c += item
        olist.append(c)

    return olist

def list_days_since_origin(ldates, origin=None):
    '''Function takes a list of datetime.date objects and an optional
    origin date as arguments, and returns a list of number of days between
    each date of the list and the origin.

    If origin is not specified, the first item of the list is used.
    '''
    if origin is None:
        origin = ldates[0]

    ldays = [(d - origin).days for d in ldates]

    return ldays

def days_since_origin(date, origin):
    '''Function takes a datetime.date objects and an origin datetime.date as
    arguments, and returns a the number of days between date and the origin.
    '''
    days = (date - origin).days

    return days

def date_annotations(list_dates):
    '''Returns two dictionnaries of axis annotations. The value is the text of 
    the annotation, the key is the position on the axis. The first dictionnary
    annotates the months and the second one the years.
    The parameters to supply is a list of datetime.date objects.
    '''
    annot_m = {}
    annot_y = {}
    months = {1:'J', 2:'F', 3:'M', 4:'A', 5:'M', 6:'J', 7:'J', 8:'A', 9:'S',
             10:'O', 11:'N', 12:'D'}
    min_date, max_date = (min(list_dates), max(list_dates))
    for year in range(min_date.year, max_date.year + 1):
        for month in range(1,13):
            tic_date = datetime.date(year, month, 1)
            if min_date < tic_date < max_date:
                annot_m[days_since_origin(tic_date, min_date)] = months[month]
                if month == 1:
                    annot_y[days_since_origin(tic_date, min_date)] = "%d" % (year)
    return (annot_m, annot_y)

if __name__ == '__main__':
    print(cumul([1, 3, 2, 1, 4, 3, 3, 2, 1]))

    ldates = [datetime.datetime(a, 6, 18) for a in range(1984, 1999)]
    print(list_days_since_origin(ldates))
