#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" dbSelect """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrstring import templateReplace, splitAndStrip, countOf

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=3, border_spacing='6px',datapath='myform')
        fb.dbSelect(dbtable='showcase.person',columns='$name',value='^.person',
                   lbl='Star')
        fb.dbSelect(dbtable='showcase.cast',columns='@movie_id.title',value='^.movie',
                    condition='$person_id =:p',condition_p='=.person',auxColumns='$role,$prizes',
                    rowcaption='@movie_id.title',selected_role='.role')
        fb.div('^.role')
        

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()