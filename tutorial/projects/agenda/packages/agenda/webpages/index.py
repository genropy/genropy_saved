#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url = 'indexcontent.html'
    #showTabs = True (by default, showTabs is True)
    
    def windowTitle(self):
        return 'Agenda'
        
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'