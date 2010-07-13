#!/usr/bin/env python
# encoding: utf-8
"""
importer.py

Created by Saverio Porcari on 2008-07-28.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from gnr.core.gnrbag import Bag, BagResolver, BagCbResolver, DirectoryResolver
from gnr.app.gnrapp import GnrApp

def importPeople(db,dataBag):
    tblObj = db.table('showcase.person')
    
    for item in dataBag['people']:
        record = {}
        record['name'] = item.getAttr('name')
        record['year'] = item.getAttr('year')
        record['nationality'] = item.getAttr('nationality')
        record['number'] = item.getAttr('id')
        tblObj.insert(record)
        
def importMovie(db,dataBag):
    tblObj = db.table('showcase.movie')
    for item in dataBag['movie']:
        record = {}
        record['title'] = item.getAttr('title')
        record['year'] = item.getAttr('year')
        record['nationality'] = item.getAttr('nationality')
        record['number'] = item.getAttr('id')
        record['genre'] = item.getAttr('genre')
        tblObj.insert(record)
        
def importCast(db,dataBag):
    tblObj = db.table('showcase.cast')
    movies = db.table('showcase.movie').query(columns='$id').fetch()
    people = db.table('showcase.person').query(columns='$id').fetch()
    for item in dataBag['cast']:
        record = {}
        record['person_id'] = people[int(item.getAttr('person_id'))]['id']
        record['movie_id'] = movies[int(item.getAttr('movie_id'))]['id']
        record['role'] = item.getAttr('role')
        record['prizes'] = item.getAttr('prizes')
        tblObj.insert(record)
        
if __name__ == '__main__':
    db = GnrApp('/Users/michele/newsites/showcase/instance').db    
    dataBag = Bag('/Users/michele/genro/gnrpy/packages/showcase/lib/data.xml')
    importPeople(db,dataBag)
    importMovie(db,dataBag)
    importCast(db,dataBag)
    db.commit()