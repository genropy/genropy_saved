#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from gnr.core.gnrbag import Bag

from gnrtestutils import AppTesting

class TestTablePrefrences(AppTesting):

    
    def testGetEmptyPreference(self):
        tbl = self.db.table('adm.preference')
        p = tbl.getPreference('empty_preference')
        assert p is None
    
    def testSetPreference(self):
        tbl = self.db.table('adm.preference')
        p = tbl.getPreference('something')
        assert p is None
        b = Bag(dict(param0='zero', param1='one'))
        tbl.setPreference('something',b)
        p = tbl.getPreference('something')
        assert len(p) == 2
        assert p['param0'] == 'zero'
        assert p['param1'] == 'one'
        