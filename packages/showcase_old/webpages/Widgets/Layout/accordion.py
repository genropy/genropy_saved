#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os

from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        ac = root.accordionContainer(margin='1em')
        ac.accordionPane(title='Pane one')
        ac.accordionPane(title='Pane two')
        ac.accordionPane(title='Pane three')


                
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
