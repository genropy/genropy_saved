#!/usr/bin/env python
# encoding: utf-8
# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrbag : an advanced data storage system
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
this test module focus on SqlSelection's methods
"""

import os
import datetime

import py.test

from gnr.sql.gnrsql import GnrSqlDb
from gnr.sql.gnrsqldata import SqlQuery
from gnr.sql.gnrsqlmodel import DbPackageObj, DbModelObj, DbTableObj, DbColumnObj,\
    DbTableListObj, DbColumnListObj, DbIndexListObj
from gnr.sql.adapters._gnrbaseadapter import GnrDictRow
from gnr.core.gnrbag import Bag
from gnr.core import gnrstring

def setup_module(module):
    module.CONFIG = Bag('data/configTest.xml')
    module.SAMPLE_XMLSTRUCT = 'data/dbstructure_base.xml'
    module.SAMPLE_XMLDATA = 'data/dbdata_base.xml'

# this module test all the post-process methods on selection resolver

class BaseDb(object):
    def setup_class(cls):
        cls.init()
        # create database (actually create the DB file or structure)
        cls.db.createDb(cls.dbname)
        # read the structure of the db from xml file: this is the recipe only
        cls.db.loadModel(SAMPLE_XMLSTRUCT)
        # build the python db structure from the recipe
        cls.db.startup()
        cls.db.checkDb(applyChanges=True)
        cls.db.importXmlData(SAMPLE_XMLDATA)
        cls.db.commit()

        cls.myquery = cls.db.query('video.cast', columns="""$id,@person_id.name AS person,
                                                            @movie_id.title AS movie,
                                                            role
                                                            """)
        #create a base selection
        cls.mysel = cls.myquery.selection()

    def test_sort(self):
        self.mysel.sort('movie', 'role:d', 'person')
        result = self.mysel.output('list', columns='movie,role,person')
        assert result[0] == [u'Barry Lindon', u'director', u'Stanley Kubrick']
        assert result[1][2] == 'Marisa Berenson'
        self.mysel.sort('id')
        assert self.mysel.output('list', columns='id')[0][0] == 0

    def test_outputMode(self):
        assert isinstance(self.mysel.output('list'), list) and\
               isinstance(self.mysel.output('list')[0], list)
        assert isinstance(self.mysel.output('dictlist'), list) and\
               isinstance(self.mysel.output('dictlist')[0], dict)
        assert isinstance(self.mysel.output('dictlist'), list) and\
               isinstance(self.mysel.output('dictlist')[0], dict)
        fromjson = gnrstring.fromJson(self.mysel.output('json'))
        assert isinstance(self.mysel.output('json'), basestring) and\
               isinstance(fromjson, list) and isinstance(fromjson[0], dict)
        assert isinstance(self.mysel.output('pkeylist'), list) and\
               self.mysel.output('pkeylist')[0] == 0
        assert isinstance(self.mysel.output('bag'), Bag)

    def test_filter(self):
        self.mysel.filter(lambda r: r['person'].endswith('cino'))
        result = self.mysel.output('list', columns='person')
        assert result[0][0] == 'Al Pacino'
        self.mysel.filter()

    def test_freeze(self):
        self.mysel.freeze('data/myselection')
        sel = self.db.table('cast').frozenSelection('data/myselection')
        assert self.mysel.data == sel.data

    def xtest_formatSelection(self):
        sel = self.db.query('video.dvd', columns='$purchasedate, @movie_id.title AS title').selection()
        assert sel.output('list')[0][1] == 'Match point'
        assert sel.output('list', formats={'title': 'Title: - %s - '},
                          dfltFormats={datetime.date: 'full'},
                          locale='it')[0][1] == 'Title: - Match point - '
        print sel.output('bag', formats={'title': 'Titolo: - %s - '},
                         dfltFormats={datetime.date: 'full'},
                         locale='it')['#0.title'] == 'Title: - Match point - '

    def teardown_class(cls):
        cls.db.closeConnection()
        cls.db.dropDb(cls.dbname)


class TestGnrSqlDb_sqlite(BaseDb):
    def init(cls):
        cls.name = 'sqlite'
        cls.dbname = CONFIG['db.sqlite?filename']
        cls.db = GnrSqlDb(dbname=cls.dbname)

    init = classmethod(init)

class TestGnrSqlDb_postgres(BaseDb):
    def init(cls):
        cls.name = 'postgres'
        cls.dbname = CONFIG['db.postgres?dbname']
        cls.db = GnrSqlDb(implementation='postgres',
                          host=CONFIG['db.postgres?host'],
                          port=CONFIG['db.postgres?port'],
                          dbname=cls.dbname,
                          user=CONFIG['db.postgres?user'],
                          password=CONFIG['db.postgres?password']
                          )

    init = classmethod(init)
    
