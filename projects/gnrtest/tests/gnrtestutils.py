#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from gnr.app.gnrapp import GnrApp

import unittest

app = GnrApp('gnrtest',forTesting=True)

class AppTesting(unittest.TestCase):
    """Base class for GenroPy tests that require an application instance.
    """
    def setUp(self):
        # NOTE: it would be better to teardown and rebuild the app at every test,
        #       but it takes a lot of time.
        global app
        self.app = app
        self.db = self.app.db
    
    def tearDown(self):
        del self.db
        del self.app