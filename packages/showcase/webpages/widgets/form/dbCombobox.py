#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" dbCombobox """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrstring import templateReplace, splitAndStrip, countOf

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=1, dbtable='showcase.cast',datapath='xxx')
        #fb.field('showcase.cast.movie_id', lbl='field in fb',validate_notnull=True,validate_notnull_error='!!Required')
        fb.dbCombobox(dbtable='showcase.movie', value='^dbcombo.m1',  lbl='dbsel in fb',validate_onAccept='alert("aaa")')
        #fb.div(lbl='field con div', datapath='xxy').field('showcase.cast.movie_id')
        #fb.div(lbl='dbsel con div', datapath='xxz').dbselect(dbtable='showcase.movie', value='^dbselect.m2',  )
                           
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()