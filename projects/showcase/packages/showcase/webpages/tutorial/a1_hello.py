#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.


class GnrCustomWebPage(object):
    def main_root(self, root, **kwargs):
        root.div('hello world!')
        root.div('^pippo',childname='pierozzo')
        root.textbox(value='^pippo')