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
this test module focus on SqlTable's methods
"""

import os
import datetime

import py.test
import logging

gnrlogger = logging.getLogger('gnr')
hdlr = logging.FileHandler('logs.log')
gnrlogger.addHandler(hdlr)

from gnr.sql.gnrsql import GnrSqlDb

from gnr.core.gnrbag import Bag
from a_structure_load_test import configurePackage


def setup_module(module):
    logging.getLogger('gnr.sql.gnrsql').setLevel(logging.INFO)
    module.CONFIG = Bag('data/configTest.xml')
    module.SAMPLE_XMLSTRUCT = 'data/dbstructure_base.xml'
    module.SAMPLE_XMLDATA = 'data/dbdata_base.xml'

class BaseSql(object):
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

    #------------setup test-----------------------------------------
    def test_modelSrc(self):
        assert self.db.model.src['packages.video.tables.people?pkey'] == 'id'

    def test_modelObj(self):
        assert self.db.packages.keys() == ['video']
        tbl = self.db.table('video.dvd')

    def test_noStructDiff(self):
        assert not self.db.checkDb()

    def test_execute1(self):
        result = self.db.execute('SELECT 1;').fetchall()
        assert result[0][0] == 1

    #------------table test-----------------------------------------
    def test_insert(self):
        tbl = self.db.table('video.movie')
        tbl.insert({'id': 11, 'title': 'Forrest Gump'})
        result = tbl.record(columns='*',
                            where="$id = :id", id=11, mode='bag')
        self.db.commit()
        assert result['title'] == 'Forrest Gump'
        tbl.delete(result)
        self.db.commit()

    def test_update(self):
        self.db.table('video.movie').update({'id': 10, 'nationality': 'TIBET'})
        self.db.commit()
        result = self.db.query('video.movie', columns='$title, $nationality',
                               where="$id = :id", id=10).fetch()
        assert result[0][1] == 'TIBET'
        self.db.table('video.movie').update({'id': 10, 'nationality': 'USA'})
        self.db.commit()

    def test_insertExisting(self):
        py.test.raises(self.db.connection.IntegrityError,
                       self.db.table('video.movie').insert,
                       {'id': 10, 'title': 'The Departed'})
        self.db.connection.rollback()

    def test_executeAfterRollback(self):
        result = self.db.query('video.movie', columns='title', where="$id=:id", id=0).fetch()
        assert result[0][0] == "Match point"

    def test_insertNoId(self):
        today = datetime.date.today()
        self.db.table('video.dvd').insert({'movie_id': 2, 'purchasedate': today})
        result = self.db.query('video.dvd', columns='$title',
                               relationDict={'title': '@movie_id.title'},
                               where="$purchasedate = :today", today=today).fetch()
        self.db.commit()
        assert result[0][0] == 'Munich'

    def test_createStructureFromCode(self):
        configurePackage(self.db.packageSrc('video'))
        self.db.saveModel('dbstructure.xml')
        assert self.db.model.src['packages.video.tables.people?pkey'] == 'id'

    def test_record(self):
        result = self.db.table('video.dvd').record(1, mode='bag')
        assert result['@movie_id.title'] == 'Scoop'
        assert result['purchasedate'] == datetime.date(2006, 3, 2)

    def test_recordKwargs(self):
        result = self.db.table('video.movie').record(title='Munich', mode='bag')
        print result
        assert result['genre'] == 'DRAMA'

    def test_record_modeDict(self):
        result = self.db.table('video.dvd').record(1, mode='dict')
        assert isinstance(result, dict)

    def test_createStructureFromCode(self):
        configurePackage(self.db.packageSrc('video'))
        self.db.saveModel('dbstructure.xml')
        assert self.db.model.src['packages.video.tables.people?pkey'] == 'id'

    def teardown_class(cls):
        cls.db.closeConnection()
        cls.db.dropDb(cls.dbname)


class TestGnrSqlDb_sqlite(BaseSql):
    def init(cls):
        cls.name = 'sqlite'
        cls.dbname = CONFIG['db.sqlite?filename']
        cls.db = GnrSqlDb(dbname=cls.dbname)

    init = classmethod(init)


class TestGnrSqlDb_postgres(BaseSql):
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

def teardown_module(module):
    print 'teardown sql_test'
    
