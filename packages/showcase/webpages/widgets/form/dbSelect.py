#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" dbSelect """
import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root,cache=False, **kwargs):
        if cache:
            root.script('genro.cache_dbselect = true;')
        fb = root.formbuilder(cols=3, border_spacing='6px',datapath='myform')
        fb.dbSelect(dbtable='showcase.person',columns='$name',value='^.person',
                   lbl='Star')
        fb.data('.person','jQ6gVT1AOb6nmc0pMzCiaA')
                   
        fb.dbSelect(dbtable='showcase.cast',columns='@movie_id.title',value='^.movie',
                    condition='$person_id =:p',condition_p='=.person',auxColumns='$role,$prizes',
                    rowcaption='@movie_id.title',selected_role='.role')
        fb.div('^.role')