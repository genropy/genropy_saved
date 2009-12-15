#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):    
    def main(self, root, **kwargs):
        box = root.div(datapath='pluto')
        box.textbox(value='^.pippo')
        box.data('.pippo','antonio')
        box.textbox(value='^.pippo?color')
        