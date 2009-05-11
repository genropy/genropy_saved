#!/usr/bin/env python
# encoding: utf-8
"""
track.py

Created by Saverio Porcari on 2008-01-31.

"""

class Table(object):
   
    def config_db(self, pkg):
        
        tbl =  pkg.table('track',  pkey='id',name_long='Track', name_plural='!!tracks',rowcaption='titolo')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('codice',size=':12',name_long='Codice')
        tbl.column('titolo',size=':25',name_long='Titolo')


