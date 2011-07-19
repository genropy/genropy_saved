#!/usr/bin/env python
# encoding: utf-8
"""
index.py

Created by Filippo Astolfi on 2011-07-19.
Copyright (c) 2011 Softwell. All rights reserved.
"""
        
class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url = 'indexcontent.html'
    
    def windowTitle(self):
        return '!!Invoice'
        
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'