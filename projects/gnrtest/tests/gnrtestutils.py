#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import unittest

from gnr.app.gnrapp import GnrApp

class AppTesting(unittest.TestCase):
    """Base class for GenroPy tests that require an application instance."""

    # set 'reuse_app' to False in your subclasses, if you want to recreate the
    # app object for each test
    reuse_app = True
    instance_name = 'gnrtest'
    testing_data = None

    def __init__(self, *args, **kwargs):
        super(AppTesting, self).__init__(*args, **kwargs)
        self._app = None

    @property
    def app(self):
        if not self._app:
            self._app = GnrApp(self.instance_name,
                               forTesting=self.testing_data or True)
        return self._app

    def tearDown(self):
        if not self.reuse_app:
            del self._app
