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
        root.div('Hello assopy', font_size='40pt', 
                        border='3px solid yellow', padding='20px')
        root.button('aaa')
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
