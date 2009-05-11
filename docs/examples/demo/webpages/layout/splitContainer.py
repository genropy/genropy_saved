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
        lc=root.splitContainer(height='100%',width='100%')
        left=lc.contentPane(sizeShare=50,background_color='blue')
        left.div('I am a blue content pane')
        right=lc.contentPane(sizeShare=50,background_color='yellow')
        right.iframe(src="http://www.apple.com",border='0px',height='100%',width='100%')

       
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
