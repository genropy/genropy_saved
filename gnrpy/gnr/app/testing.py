#!/usr/bin/python
# -*- coding: UTF-8 -*-
import codecs
import os.path
import sys
import unittest
import yaml
from gnr.core.gnrbag import Bag
from gnr.app.gnrapp import GnrApp
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.NOTSET)

class TestError(Exception):
    pass

APP_CACHE = {}

class TestCase(unittest.TestCase):

    # Subclasses should redefine these variables
    instance=''
    load_data=[] # data files to load
    load_preferences=None
    preferences=None

    # Set to False to rebuild the app for each test, set to True to have one app for each TestCase subclass.
    persistent_app = True

    def loadApp(self):
        if not self.instance:
            raise TestError("Please specify an instance name")
        self.app = GnrApp(self.instance, forTesting=True)
        base_dir = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        # Load preferences
        if self.load_preferences:
            fullname = os.path.join(base_dir, self.load_preferences)
            if not os.path.isfile(fullname):
                raise TestError("Missing preferences file: %s" % fullname)
            self.loadPreferences(fullname)
        # Load data files
        for datafile in self.load_data:
            fullname = os.path.join(base_dir, datafile)
            if not os.path.isfile(fullname):
                raise TestError("Missing data file: %s" % fullname)
            basename, ext = os.path.splitext(fullname)
            if ext == '.yaml':
                self.loadYamlDataFile(fullname)
            elif ext == '.xml':
                self.loadXmlDataFile(fullname)
            elif ext == '.sql':
                self.loadSqlDataFile(fullname)
            else:
                raise TestError("Unknown data file format: %s" % fullname)

    @property
    def db(self):
        return self.app.db

    def setUp(self):
        global APP_CACHE
        if self.persistent_app:
            self.app = APP_CACHE.get(self.__class__, None)
        if not self.app:
            self.loadApp()
        if self.persistent_app:
            APP_CACHE[self.__class__] = self.app

    def tearDown(self):
        del self.app

    def loadPreferences(self, filename):
        basename, ext = os.path.splitext(filename)
        if ext == '.yaml':
            preferences = Bag(yaml.load(codecs.open(filename,'rt','utf-8')))
        else:
            preferences = Bag(filename)
        for package, prefs in preferences.items():
            self.db.packages[package].setPreference('', prefs)
#            self.db.packages[package].getPreference = lambda path, default=None: prefs.get(path, default)
#            self.db.packages[package].setPreference = lambda path, value: prefs.setItem(path, value)

    def loadYamlDataFile(self, fullname):
        data = yaml.load(open(fullname,'rt'))
        for pkgname, tables in data.items():
            for tablename, records in tables.items():
                tbl = self.db.table(tablename, pkgname)
                for label, rec in records.items():
                    tbl.insert(rec)

    def loadXmlDataFile(self, fullname):
        raise NotImplementedError("XML data files: Not yet implemented")

    def loadSqlDataFile(self, fullname):
        raise NotImplementedError("SQL data files: Not yet implemented")
