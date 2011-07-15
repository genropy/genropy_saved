#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='task.task'
    py_requires="""public:TableHandlerMain,
                gnrcomponents/htablehandler:HTableHandlerBase"""

    def pageAuthTags(self, method=None, **kwargs):
        return 'user,read_only'
        
    def tableWriteTags(self):
        return 'user,!read_only'
        
    def tableDeleteTags(self):
        return 'user,!read_only'
        