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
        mydiv = root.div(nodeId='aaa',height='20ex',width='20em',border='1px solid black')
        root.button('Crea sul client',fire='build')
        root.dataController("page.buildOnClient()",_fired="^build")

            
                
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
