#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url = 'indexcontent.html'
    
    def windowTitle(self):
        return 'Agenda'
        
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'