#!/usr/bin/env python
# encoding: utf-8
"""
importer.py

Created by Filippo Astolfi on 2011-11-23
Copyright (c) 2011 Softwell. All rights reserved
"""

from gnr.core.gnrbag import Bag, BagResolver, BagCbResolver, DirectoryResolver
from gnr.app.gnrapp import GnrApp

def importPerson(db, dataBag):
    tblObj = db.table('showcase.person')
    for item in dataBag['person']:
        record = {}
        record['number'] = item.getAttr('id')
        record['name'] = item.getAttr('name')
        record['b_year'] = item.getAttr('b_year')
        record['d_year'] = item.getAttr('d_year')
        record['nationality'] = item.getAttr('nationality')
        tblObj.insert(record)

def importMusic(db, dataBag):
    tblObj = db.table('showcase.music')
    for item in dataBag['music']:
        record = {}
        record['number'] = item.getAttr('id')
        record['title'] = item.getAttr('title')
        record['genre'] = item.getAttr('genre')
        record['year'] = item.getAttr('year')
        record['op'] = item.getAttr('op')
        tblObj.insert(record)

def importPersonMusic(db, dataBag):
    tblObj = db.table('showcase.person_music')
    music = db.table('showcase.music').query(columns='$id').fetch()
    person = db.table('showcase.person').query(columns='$id').fetch()
    for item in dataBag['person_music']:
        record = {}
        record['person_id'] = person[int(item.getAttr('person_id'))]['id']
        record['music_id'] = music[int(item.getAttr('music_id'))]['id']
        tblObj.insert(record)

if __name__ == '__main__':
    db = GnrApp('testgarden').db
    dataBag = Bag('data.xml')
    importPerson(db, dataBag)
    importMusic(db, dataBag)
    importPersonMusic(db, dataBag)
    db.commit()