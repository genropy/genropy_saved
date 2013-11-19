# -*- coding: UTF-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-29.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''

    def windowTitle(self):
        return ''

    def main(self, root, **kwargs):
        root.div('not existing')
        return