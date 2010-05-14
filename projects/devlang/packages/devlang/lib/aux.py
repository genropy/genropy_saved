#!/usr/bin/env python
# encoding: utf-8
"""
aux.py

Created by Jeff Edwards on 2010-05-13.
Copyright (c) 2010 Goodsoftware Pty Ltd. All rights reserved.
"""
import os
from gnr.app.gnrapp import GnrApp  # ask to import the app
from gnr.core.gnrbag import Bag
from gnr.core.gnrlist import GnrNamedList, readXLS, readCSV

def test2():
    from gnr.core.gnrsys import resolvegenropypath

    print resolvegenropypath('~/genropy/genro/projects/devlang/packages/devlang/lib/developers.txt')
    print resolvegenropypath('/genropy/genro/projects/devlang/packages/devlang/lib/developers.txt')
    print resolvegenropypath('genropy/genro/projects/devlang/packages/devlang/lib/developers.txt')


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

    def populatedevlang(frmSp,frmDb):
        if  temprecord[frmSp]:
            record_devlang = Bag()
            record_dev['id'] = tbl_devlang.newPkeyValue()
            record_devlang['developer_id'] = developer_id
            record_devlang['language_id'] = dict(lang_dict[frmDb])['pkey']
            record_devlang['level'] = int(temprecord[frmSp])
            tbl_devlang.insert(record_devlang)

    print "... developer import"
    path = '~/genropy/genro/projects/devlang/packages/devlang/lib/developers.txt'
    path = os.path.expanduser(path)
    f=file(path)
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
        populatedevlang('java','Java')
        populatedevlang('python','Python')
        populatedevlang('javascript','Javascript')
        populatedevlang('cplus','C++')
        populatedevlang('objectivec','Objective C')
        populatedevlang('html','html')
        populatedevlang('smalltalk','Smalltalk')
        populatedevlang('csharp','C#')
        if n%200==0:
            print '%s records' %(n,)

    db.commit()
    print "... developer import complete"


if __name__ == '__main__':
    test2()
    #populateDevelopers()
