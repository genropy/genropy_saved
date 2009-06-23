#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
import cups
class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return '!!'

    def main(self, root, **kwargs):
        connection = cups.Connection()
        root.data('printers',connection.getPrinters())
        root.tree(storepath='printers')

