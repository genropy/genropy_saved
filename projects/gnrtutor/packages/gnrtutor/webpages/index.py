#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
"""
index.py

Created by Jeff Edwards on 2009-10-01.
Copyright (c) 2012 Softwell. All rights reserved.
"""


# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    index_url='indexcontent.html'
    #showTabs=True
    authTags='user'
    def windowTitle(self):
        return '!!Genropy Tutor'



