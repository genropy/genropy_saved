#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url = '/myindex.py'
    showTabs = True
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return 'Agenda'