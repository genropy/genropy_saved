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
        root = self.rootLayoutContainer(root)
        lc=root.TabContainer(height='100%')
        first=lc.contentPane(title='First',background_color='blue')
        first.div('I am a blue content pane')
        second=lc.contentPane(title='Second',background_color='yellow')
        second.div('I am an yellow content pane')
       

       
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
