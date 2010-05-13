#!/usr/bin/env python
# encoding: utf-8
"""
aux.py

Created by Jeff Edwards on 2010-05-13.
Copyright (c) 2010 Goodsoftware Pty Ltd. All rights reserved.
"""

import sys
import os
from gnr.app.gnrapp import GnrApp  # ask to import the app
from gnr.core.gnrbag import Bag
from gnr.core.gnrlist import GnrNamedList, readXLS, readCSV


def test():
    app=GnrApp('devlang') # create the app starting from the instance config
    db=app.db # app.db is the instance of the db
    tbl_developer = db.table('devlang.developer')
    tbl_devlang = db.table('devlang.dev_lang')
    tbl_lang = db.table('devlang.language')
    lang_dict = tbl_lang.query(columns='name').fetchAsDict(key='name')
    print dict(lang_dict['Python'])['pkey']
    print lang_dict
    for k, v in lang_dict.items():
        x = dict(v)
        print '%s : %s' %(k,x)
    
    
def populateDevelopers():
    app=GnrApp('devlang') # create the app starting from the instance config
    db=app.db # app.db is the instance of the db
    tbl_developer = db.table('devlang.developer')
    tbl_devlang = db.table('devlang.dev_lang')
    tbl_lang = db.table('devlang.language')
    lang_dict = tbl_lang.query(columns='name').fetchAsDict(key='name')
    

    print "... developer import"

    f=file('/Users/jeffedwa/genropy/genro/projects/devlang/packages/lib/developers.txt')
    rows = readCSV(f)
    
    for n, row in enumerate(rows):
        temprecord = Bag(dict(row))
        record_dev = Bag()
        
        developer_id = tbl_developer.newPkeyValue()
        record_dev['id'] = developer_id
        record_dev['first_name'] = temprecord['firstname']
        record_dev['last_name'] = temprecord['lastname']
        record_dev['email'] = temprecord['emailaddress']
        record_dev['address'] = '%s, %s %s %s' %(temprecord['streetaddress'],temprecord['suburb'],temprecord['state'],temprecord['postcode'])
        record_dev['country_code'] = 'AU'
        record_dev['country_name'] = 'Australia'
        record_dev['area'] = temprecord['state']
        record_dev['locality'] = temprecord['suburb']
        record_dev['thoroughfare'] = temprecord['streetaddress']
        record_dev['postal_code'] = temprecord['postcode']
        tbl_developer.insert(record_dev)
        
        # python	java	javascript	csharp	cplus	objectivec	smalltalk	html
        if  temprecord['java']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['Java'])['pkey']
            record_devlang['level'] = int(temprecord['java'])
            tbl_devlang.insert(record_devlang)
        
        if  temprecord['python']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['Python'])['pkey']
            record_devlang['level'] = int(temprecord['python'])
            tbl_devlang.insert(record_devlang)

        if  temprecord['javascript']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['Javascript'])['pkey']
            record_devlang['level'] = int(temprecord['javascript'])
            tbl_devlang.insert(record_devlang)

        if  temprecord['cplus']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['C++'])['pkey']
            record_devlang['level'] = int(temprecord['cplus'])
            tbl_devlang.insert(record_devlang)

        if  temprecord['objectivec']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['Smalltalk'])['pkey']
            record_devlang['level'] = int(temprecord['objectivec'])
            tbl_devlang.insert(record_devlang)

        if  temprecord['html']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['C#'])['pkey']
            record_devlang['level'] = int(temprecord['html'])
            tbl_devlang.insert(record_devlang)

        if  temprecord['smalltalk']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['Objective C'])['pkey']
            record_devlang['level'] = int(temprecord['smalltalk'])
            tbl_devlang.insert(record_devlang)

        if  temprecord['csharp']:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict['C#'])['pkey']
            record_devlang['level'] = int(temprecord['csharp'])
            tbl_devlang.insert(record_devlang)


    db.commit()
    print "... developer import complete"


if __name__ == '__main__':
    #test()
    populateDevelopers()
