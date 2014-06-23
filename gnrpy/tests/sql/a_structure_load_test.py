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
from gnr.core.gnrbag import Bag
from gnr.core import gnrstring

def setup_module(module):
    module.CONFIG = Bag('data/configTest.xml')
    module.SAMPLE_XMLSTRUCT = 'data/dbstructure_base.xml'
    module.SAMPLE_XMLSTRUCT_FINAL = 'data/dbstructure_final.xml'
    module.SAMPLE_XMLDATA = 'data/dbdata_base.xml'

class TestDbModelSrc(object):
    def setup_class(cls):
        cls.db_fromxml = GnrSqlDb()
        cls.db_fromcode = GnrSqlDb()

        cls.db_fromxml.loadModel(SAMPLE_XMLSTRUCT)
        package = cls.db_fromcode.packageSrc('video')
        configurePackage(package)

        tm = MyTblMixin()
        pm = MyPkgMixin()

        cls.db_fromcode.packageMixin('video', pm)
        cls.db_fromxml.packageMixin('video', pm)
        cls.db_fromcode.tableMixin('video.people', tm)
        cls.db_fromxml.tableMixin('video.people', tm)
        #cls.db_fromcode.model.src.save(SAMPLE_XMLSTRUCT)
        cls.db_fromcode.startup()
        cls.db_fromxml.startup()
        cls.db_fromcode.model.src.save(SAMPLE_XMLSTRUCT_FINAL)

    def test_modelSrcEqual(self):
        assert self.db_fromcode.model.src == self.db_fromxml.model.src

    def test_mixinPackage(self):
        assert self.db_fromxml.packageSrc('video').table('actor').column('id') != None
        assert 'this is video package' == self.db_fromxml.package('video').sayMyName()

    def test_mixinTable(self):
        assert 'foo' in self.db_fromxml.packageSrc('video').table('people')['columns'].keys()
        assert 'Hello Genro' == self.db_fromxml.table('video.people').sayHello('Genro')

    def test_package(self):
        assert self.db_fromxml.packageSrc('video').attributes['comment'] == 'video package'

    def test_externalPackage(self):
        assert self.db_fromxml.packageSrc('video').table('movie').externalPackage(
                'video') == self.db_fromxml.packageSrc('video')

    def test_table(self):
        assert self.db_fromxml.packageSrc('video').table('people').attributes['pkey'] == 'id'

    def test_table_upd(self):
        self.db_fromxml.packageSrc('video').table('movie', name_full='Movie')
        assert self.db_fromxml.packageSrc('video').table('movie').attributes['name_full'] == 'Movie'
        self.db_fromcode.packageSrc('video').table('movie', name_full='Movie')
        assert self.db_fromcode.packageSrc('video').table('movie').attributes['name_full'] == 'Movie'

    def test_column(self):
        assert self.db_fromcode.packageSrc('video').table('movie').column('description').attributes[
               'name_short'] == 'Dsc'

    def test_column_upd(self):
        self.db_fromxml.packageSrc('video').table('movie').column('genre', name_full='Genre')
        self.db_fromxml.packageSrc('video').table('movie')['columns.genre?name_full'] == 'Genre'
        self.db_fromcode.packageSrc('video').table('movie').column('genre', name_full='Genre')
        self.db_fromcode.packageSrc('video').table('movie')['columns.genre?name_full'] == 'Genre'

    def test_index(self):
        assert self.db_fromxml.packageSrc('video').table('movie').index(name='i_title').attributes['unique'] == 'y'

    def test_relation(self):
        assert self.db_fromxml.packageSrc('video').table('cast').column('person_id')[
               'relation?related_column'] == "people.id"

    def teardown_class(cls):
        pass

def teardown_module(module):
    print 'teardown sql_test'


def configurePackage(pkg):
    pkg.attributes.update(comment='video package', name_short='video', name_long='video', name_full='video')

    people = pkg.table('people', name_short='people', name_long='People',
                       rowcaption='name,year:%s (%s)', pkey='id')
    people.column('id', 'L')
    people.column('name', name_short='N.', name_long='Name')
    people.column('year', 'L', name_short='Yr', name_long='Birth Year')
    people.column('nationality', name_short='Ntl', name_long='Nationality')

    cast = pkg.table('cast', name_short='cast', name_long='Cast',
                     rowcaption='', pkey='id')
    cast.column('id', 'L')
    cast.column('movie_id', 'L', name_short='Mid',
                name_long='Movie id').relation('movie.id')
    cast.column('person_id', 'L', name_short='Prs',
                name_long='Person id').relation('people.id')
    cast.column('role', name_short='Rl.', name_long='Role')
    cast.column('prizes', name_short='Priz.', name_long='Prizes', size='40')

    movie = pkg.table('movie', name_short='Mv', name_long='Movie',
                      rowcaption='title', pkey='id')
    movie.column('id', 'L')
    movie.column('title', name_short='Ttl.', name_long='Title',
                 validate_case='capitalize', validate_len='3,40')
    movie.index('title', 'i_title', unique='y')
    movie.column('genre', name_short='Gnr', name_long='Genre',
                 validate_case='upper', validate_len='3,10', indexed='y')
    movie.column('year', 'L', name_short='Yr', name_long='Year', indexed='y')
    movie.column('nationality', name_short='Ntl', name_long='Nationality')
    movie.column('description', name_short='Dsc', name_long='Movie description')

    dvd = pkg.table('dvd', name_short='Dvd', name_long='Dvd', pkey='code')
    dvd_id = dvd.column('code', 'L')
    dvd.column('movie_id', name_short='Mid', name_long='Movie id').relation('movie.id')
    dvd.column('purchasedate', 'D', name_short='Pdt', name_long='Purchase date')
    dvd.column('available', name_short='Avl', name_long='Available')


class MyTblMixin(object):
    def config_db(self, pkg):
        t = pkg.table('people')
        t.column('foo')

    def sayHello(self, name):
        return 'Hello %s' % name

class MyPkgMixin(object):
    def config_db(self, pkg):
        pkg.table('actor', name_short='act', name_long='actor', pkey='id').column('id', 'L')

    def sayMyName(self):
        return 'this is %s package' % self.name
