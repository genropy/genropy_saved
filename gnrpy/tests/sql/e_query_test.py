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
this test module focus on SqlQuery's methods
"""

import os
import datetime

import py.test
import logging

gnrlogger = logging.getLogger('gnr')
hdlr = logging.FileHandler('logs.log')
gnrlogger.addHandler(hdlr)

from gnr.sql.gnrsql import GnrSqlDb
from gnr.sql.gnrsqldata import SqlQuery, SqlSelection
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

    def test_selection(self):
        query = self.db.query('video.movie', columns='title',
                              where="$id=:id", sqlparams={'id': 0})
        result = query.selection()
        assert isinstance(result, SqlSelection)

    def test_query(self):
        result = self.db.query('video.movie')
        assert isinstance(result, SqlQuery)

    def test_query_count(self):
        assert self.db.query('video.movie').count() == 11
        assert self.db.query('video.movie', where='$year=:y', sqlparams={'y': 2005}).count() == 2

    def test_query_fetch(self):
        fetch = self.db.query('video.movie',
                              columns='*',
                              where='$title=:title',
                              title='Scoop').fetch()
        assert fetch[0][0] == fetch[0]['id'] == 1

    def test_query_cursor(self):
        query = self.db.query('video.movie',
                              columns='*',
                              where='$title=:title',
                              sqlparams={'title': 'Scoop'})
        cursor = query.cursor()
        result = cursor.fetchall()
        assert result[0][0] == result[0]['id'] == 1

    def xtest_query_servercursor(self):
        # fix the adapter
        servercursor = self.db.query('video.movie',
                                     columns='*',
                                     where='$title=:title',
                                     title='Scoop').servercursor()
        result = servercursor.fetchall()
        assert result[0][0] == result[0]['id'] == 1

    def test_where_statement(self):
        query = self.db.query('video.movie',
                              columns='title',
                              where="$id=:id",
                              sqlparams={'id': 0})

        result = query.selection().output('list')
        assert result[0][0] == "Match point"

    def test_in_statement(self):
        query = self.db.query('video.movie',
                              where='$year IN :years',
                              sqlparams={'years': (2005, 2006)})
        result = query.count()
        assert result == 4

    def test_sqlparams_date(self):
        query = self.db.query('video.dvd',
                              columns='$purchasedate',
                              where='$purchasedate BETWEEN :d1 AND :d2',
                              sqlparams={'d1': datetime.date(2005, 4, 1), 'd2': datetime.date(2005, 4, 30)})
        result = query.selection().output('list')
        assert result[0][0] == datetime.date(2005, 4, 7)


    def test_joinSimple(self):
        tbl = self.db.table('video.dvd')
        #raise str(tbl.fields['@movie_id'].keys())
        result = tbl.query(columns='$title',
                           relationDict={'title': '@movie_id.title'},
                           where="$code = :code", code=0).fetch()
        assert result[0]['title'] == "Match point"

    def test_joinDistinct(self):
        result = self.db.query('video.dvd', columns='$year',
                               relationDict={'year': '@movie_id.year'},
                               distinct=True, order_by='$year').fetch()
        assert [r['year'] for r in result] == [1960, 1975, 1983, 1987, 1999, 2004, 2005, 2006]

    def test_joinGroupBy(self):
        result = self.db.query('video.dvd', columns='$nationality, count(*)',
                               relationDict={'nationality': '@movie_id.nationality'},
                               group_by='$nationality', order_by='$nationality').fetch()
        assert [(r[0], r[1]) for r in result] == [('UK', 6), ('USA', 6), ('USA,UK', 5)]

    def test_query_limit(self):
        result = self.db.query('video.cast', columns='person_id',
                               where="@person_id.id=:id",
                               sqlparams={'id': 1}, limit=1).fetch()
        assert len(result) == 1

    def test_query_offset(self):
        result = self.db.query('video.cast', columns='@person_id.name',
                               where="$role=:role", role="director",
                               limit=1, order_by='@person_id.year',
                               offset=1).fetch()
        assert result[0][0] == 'Stanley Kubrick'

    def _broken_test_query_groupBy(self):
        #also test the resolver use
        query = self.db.query('video.cast',
                              columns='@person_id.name, count($role) as nm',
                              group_by='@person_id.name',
                              order_by='@person_id.name')
        myresolver = query.resolver('list')
        assert myresolver[0][0] == 'Al Pacino'
        result = myresolver(having='count($role) > 1')
        assert result[0][0] == 'Brian De Palma'

    def test_query_namedCursor(self):
        cursor = self.db.query('video.movie', columns='$title',
                               where="$id=:id", sqlparams={'id': 0}).cursor()
        result = cursor.fetchall()
        assert result[0]['title'] == "Match point"

    def test_join_relationDict(self):
        tbl = self.db.table('video.dvd')
        #raise str(tbl.fields['@movie_id'].keys())
        result = self.db.query('video.dvd', columns='$title',
                               relationDict={'title': '@movie_id.title'},
                               where="$code = :code", code=0).fetch()
        assert result[0]['title'] == "Match point"

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
    
