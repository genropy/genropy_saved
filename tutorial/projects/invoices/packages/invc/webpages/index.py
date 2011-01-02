#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def windowTitle(self):
        return '!!Fatture'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def main(self, rootBC, **kwargs):
        pane = rootBC.contentPane(**kwargs)
        pane.h1('Index Fatture')