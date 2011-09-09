#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  index.py


""" index.py """

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url='/manage/struttura.py'
    
    def windowTitle(self):
        return '!!Website'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
