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

from gnr.sql.gnrsql import GnrSqlDb
from gnr.sql.gnrsqlmodel import DbPackageObj, DbModelObj, DbTableObj, DbColumnObj, DbTableListObj, DbColumnListObj, DbIndexListObj
from gnr.core.gnrbag import Bag

def setup_module(module):
    module.CONFIG = Bag('data/configTest.xml')
    module.SAMPLE_XMLSTRUCT = 'data/dbstructure_base.xml'
    module.SAMPLE_XMLDATA = 'data/dbdata_base.xml'

class TestSqlStructure(object):
    def setup_class(cls):
        cls.db = GnrSqlDb()
        cls.db.loadModel(SAMPLE_XMLSTRUCT)
        cls.db.startup()

    def test_modelObj(self):
        assert isinstance(self.db.model.obj, DbModelObj)
        assert self.db.packages.keys() == ['video']

    def test_SqlPackageObj(self):
        pkg = self.db.package('video')
        assert isinstance(pkg, DbPackageObj)
        assert isinstance(pkg.tables, DbTableListObj)
        assert pkg.tables.keys() == ['people', 'cast', 'movie', 'dvd']
        tbl = pkg.table('movie')
        assert isinstance(tbl, DbTableObj)
        assert pkg.tableSqlName(tbl) == 'video_movie'
        assert pkg.sqlschema == 'main'

    def test_SqlTableObj(self):
        tbl = self.db.model.table('video.movie')
        assert tbl.pkg == self.db.package('video')
        assert tbl.fullname == 'video.movie'
        assert tbl.sqlschema == 'main'
        assert tbl.sqlname == 'video_movie'
        assert tbl.sqlfullname == 'main.video_movie'
        assert tbl.pkg.name == self.db.package('video').name
        assert isinstance(tbl.columns, DbColumnListObj)
        assert tbl.columns.keys() == ['id', 'title', 'genre', 'year', 'nationality', 'description']
        assert isinstance(tbl.indexes, DbIndexListObj)
        assert isinstance(tbl.db, GnrSqlDb)
        col = tbl.column('title')
        assert isinstance(col, DbColumnObj)


    def test_SqlTableObj_indexes(self):
        tbl = self.db.model.table('video.movie')
        indexes = tbl.indexes.keys()
        indexes.sort()
        indexes == ['i_title', 'movie_genre_key', 'movie_year_key']

    def test_SqlTableObj_rel_one(self):
        tbl = self.db.model.table('video.cast')
        assert tbl.relations_one['person_id'] == 'video.people.id'

    def test_SqlTableObj_rel_many(self):
        tbl = self.db.model.table('video.movie')
        assert tbl.relations_many['video.dvd.movie_id'] == 'id'

    def test_SqlTableObj_rel_column(self):
        tbl = self.db.model.table('video.cast')
        relcol = tbl.column('@movie_id.title')
        assert isinstance(relcol, DbColumnObj)
        #i metodi di query sono testati in un altro modulo

    def test_SqlColumnObj(self):
        pkg = self.db.package('video')
        tbl = pkg.table('cast')
        col = tbl.column('person_id')
        assert col.dtype == 'L'
        assert col.isReserved == False
        assert col.readonly == False
        assert col.pkg.name == 'video'
        assert col.table.name == 'cast'
        assert col.sqlfullname == 'main.video_cast.person_id'
        assert col.relatedTable() == pkg.table('people')
        assert col.relatedColumn() == pkg.table('people').column('id')
        col = tbl.column('prizes')
        assert col.dtype == 'A'

    def teardown_class(cls):
        pass


def teardown_module(module):
    print 'teardown sql_test'
    
