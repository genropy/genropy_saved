#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """
import datetime
import os
import hashlib

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='publicsite:SiteLayout'
    def main(self, root,**kwargs):
        layout = root.borderContainer(_class='site_body')
        header = layout.contentPane(region='top',_class='site_header')
        self.site_header(header)
        footer = layout.contentPane(region='bottom',_class='site_footer')
        
        left=layout.borderContainer(region='left',_class='site_left')
        left.contentPane(_class='site_pane',height='100%')
        
        right=layout.borderContainer(region='right',_class='site_right')
        right.contentPane(_class='site_pane')        
        self.center(layout.contentPane(region='center',_class='site_pane'))
    

    def center(self,pane):
        pane.div(_class='logobig')
    