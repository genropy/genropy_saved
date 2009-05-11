#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def main(self, root, **kwargs):
        top,client,bottom=self.publicPane(root,'!!Gestione - PyconIt')
        self.currTbl=None
        self.clientPane=client
        if not self.user:
            client.div('!!Non sei ancora un utente riconosciuto', _class='pbl_largemessage', 
                       margin='auto', margin_top='1em', margin_bottom='2em')
            self.menuButton(u'!!Entra','login.py')
            self.menuButton(u'!!Registrati','nuovo_utente.py')
        else:
            client.div(template='!!Benvenuto ^.nome_cognome', datasource='^_pbl.user_record', _class='pbl_largemessage', 
                       margin='auto', margin_top='1em', margin_bottom='2em')

            self.menuButton(u'!!Gestione Archivi','tables/index.py')
            self.menuButton(u'!!Gestione Bonifici','bonifici.py')
            self.menuButton(u'!!Valutazione Talk','tables/talk.py')
            self.menuButton(u'!!Valutazione Talk per socio','valutazioniSoci.py')
            self.menuButton(u'!!Menu iniziale','HOME')

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
