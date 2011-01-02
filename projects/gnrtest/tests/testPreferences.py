#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from gnr.core.gnrbag import Bag
from gnrtestutils import AppTesting

class TestTablePrefrences(AppTesting):
    def setUp(self):
        super(TestTablePrefrences, self).setUp()
        self.package = self.app.db.packages['gnrtest']
        self.app.db.table('adm.preference').empty()

    def testEmptyPreference(self):
        p = self.package.getPreference('something')
        self.assertEqual(None, p, '(new) child preferences should be None.')

    def testSinglePreference(self):
        self.package.setPreference('something', 'else')
        self.assertEqual('else', self.package.getPreference('something'))

    def testAllPreferences(self):
        p = self.package.getPreference('')
        self.assertEqual(None, p)

        self.package.setPreference('', Bag(dict(something='else')))
        self.assertEqual('else', self.package.getPreference('something'))

        p = self.package.getPreference('')
        self.assertTrue(isinstance(p, Bag), 'should be a Bag')
        self.assertEqual(1, len(p))
        self.assertEqual(set(('something',)), set(p.keys()))
        self.assertEqual('else', p['something'])
