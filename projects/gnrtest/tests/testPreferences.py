#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from gnr.core.gnrbag import Bag
from gnrtestutils import AppTesting

class TestPreferencesAPI(AppTesting):
    """Tests the public API of the preferences system"""
    
    
    #--------------------------------------------------------- Setup / TearDown
    
    def setUp(self):
        AppTesting.setUp(self)
        self.db.table('adm.preference').empty()
        self.pkg = self.db.packages['gnrtest']
    
    def tearDown(self):
        del self.pkg
        AppTesting.tearDown(self)

    #------------------------------------------------------ Preferences as bags
    
    def testGetPreference(self):
        p = self.pkg.getPreference('something')
        self.assertEqual(None, p, 'empty preferences should be None')
        

    def testSetPreference(self):
        self.pkg.setPreference('something','else')
        p = self.pkg.getPreference('something')
        self.assertEqual('else', p, 'getPreference() should return what we set')
    
    