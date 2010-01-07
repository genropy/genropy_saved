#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """
import os

from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    pagetemplate='assopy.tpl'
    def pageAuthTags(self, method=None, **kwargs):
        return 'superadmin'
        
    def main(self, root, **kwargs):
        top, pages = self.publicPagedPane(root, '!!Modifica profilo')
        self.pageForm(pages)
        self.pageSaving(pages)
        self.pageSaved(pages)

    def pageForm(self,pages):
        client, bottom = self.publicPage(pages, datapath='form')
    
    def pageSaving(self,pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Salvataggio in corso...", _class='pbl_largemessage', margin_top='1em',margin_right='3em',margin_left='3em')

    def pageSaved(self,pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Salvataggio effettuato",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Torna al menù', connect_onclick=self.cancel_url(),_class='pbl_button',float='right')

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
