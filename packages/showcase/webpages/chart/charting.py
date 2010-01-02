#!/usr/bin/env pythonw
# -*- codin

g: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

import os

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        pass

    
def index(req, **kwargs):
    page = GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs)
    tplfile = page.getResource('chart_test.tpl')
    return page.index(mako=tplfile)
    

