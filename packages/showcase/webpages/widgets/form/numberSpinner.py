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
from gnr.core.gnrstring import templateReplace, splitAndStrip, countOf

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    css_requires='index.css'   
    def main(self, root, **kwargs):
        cont = root.div(_class='fieldcontainer',margin='1em',padding='10px',datapath='table')
        tbl=cont.table()
        r=tbl.tr()
        r.td('Year')
        r.td().numberSpinner(value='^.year')
        r.td('fieldspinner')
        r.td().field('showcase.person.year',tag='numberSpinner')

        
        
        


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()