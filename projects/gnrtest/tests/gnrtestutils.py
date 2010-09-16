#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from gnr.app.gnrapp import GnrApp

class AppTesting(object):
    """Base class for GenroPy tests that require an application instance.
    
    You can change the instance_name or specify a path to an XML file with test data.
    """
    
    
    instance_name = 'gnrtest'
    testing_data = None # specify a path (relative to the subclass' file) to an XML file containing test data
    
    def setup_class(self):
        """Setups the app for testing."""
        self.app = GnrApp(self.instance_name, forTesting=self.testing_data or True)
        self.db = self.app.db