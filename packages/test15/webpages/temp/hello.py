# -*- coding: UTF-8 -*-

# hello.py
# Created by Francesco Porcari on 2010-08-19.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
        return ''
         
    def main_root(self, root, **kwargs):
        root.div('hello')