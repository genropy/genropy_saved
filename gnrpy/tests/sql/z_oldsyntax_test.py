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


import os
import datetime

import py.test
import logging

gnrlogger = logging.getLogger('gnr')
hdlr = logging.FileHandler('logs.log')
gnrlogger.addHandler(hdlr)

from gnr.sql.gnrsql import GnrSqlDb
from gnr.sql.gnrsqldata import SqlQuery

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

    #-----------------------query as method---------------------------------------------------------
    # this is not the recommended way to use query the other params of query are tested into e_query_test
    def test_querymode_json(self):
        # query with mode params return a resolver
        result = self.db.query('video.movie',
                               columns='*',
                               where='$title=:title',
                               title='Scoop', mode='json')()
        assert result == '[{"pkey": 1, "description": null, "title": "Scoop", "year": 2006, "genre": "COMEDY", "nationality": "USA,UK", "id": 1}]'


    def test_querymode_dictlist(self):
        # query with mode params return a resolver
        sqlresolver = self.db.query('video.movie',
                                    columns='*',
                                    where='$title=:title',
                                    title='Scoop',
                                    mode='dictlist')
        mylist = sqlresolver()
        assert isinstance(mylist, list)
        assert isinstance(mylist[0], dict)


    def test_querymode_list(self):
        # query with mode params return a resolver
        sqlresolver = self.db.query('video.movie',
                                    columns='*',
                                    where='$title=:title',
                                    title='Scoop',
                                    mode='list')
        mylist = sqlresolver()
        assert isinstance(mylist, list)
        assert isinstance(mylist[0], list)


    def test_querymode_bag(self):
        # query with mode params return a resolver
        sqlresolver = self.db.query('video.movie',
                                    columns='*',
                                    where='$title=:title',
                                    title='Scoop',
                                    mode='bag')
        mylist = sqlresolver()
        assert isinstance(mylist, Bag)


    def test_where_statement(self):
        result = self.db.query('video.movie', columns='title', where="$id=:id",
                               sqlparams={'id': 0}, mode='list')
        assert result[0][0] == "Match point"

    def test_in_statement(self):
        result = self.db.query('video.movie',
                               where='$year IN :years',
                               sqlparams={'years': (2005, 2006)},
                               mode='list')
        assert len(result) == 4

    def test_sqlparams_date(self):
        result = self.db.query('video.dvd',
                               columns='$purchasedate',
                               where='$purchasedate BETWEEN :d1 AND :d2',
                               sqlparams={'d1': datetime.date(2005, 4, 1), 'd2': datetime.date(2005, 4, 30)},
                               mode='list')
        assert result[0][0] == datetime.date(2005, 4, 7)


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
    
