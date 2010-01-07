#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    
    def windowTitle(self):
         return '!!Assopy Indice'

    def main(self, root, **kwargs):
        top,client,bottom=self.publicPane(root,'!!Gestione - PyconIt')
        self.currTbl=None
        self.clientPane=client
        if not self.user:
            client.div('!!Non sei ancora un utente riconosciuto', _class='pbl_largemessage', 
                       margin='auto', margin_top='1em', margin_bottom='2em')
            self.menuButton( u'!!Entra','login.py')
            self.menuButton(u'!!Registrati','nuovo_utente.py')

        else:
            client.div(template='!!Benvenuto ^.nome_cognome', datasource='^_pbl.user_record', _class='pbl_largemessage', 
                       margin='auto', margin_top='1em', margin_bottom='2em')

            self.menuButton(u'!!Modifica profilo','modifica_utente.py')
            self.menuButton(u'!!Cambia password','cambio_password.py')
            self.menuButton(u'!!Donazione','donazione.py')
            self.menuButton(u'!!Biglietti Pycon2','iscrizione_pycon.py')
            self.menuButton(u'!!Sponsorizzazione','sponsorizzazione.py')
            self.menuButton(u'!!I miei talk','presenta_talk.py')
            self.menuButton(u'!!Gestione Partecipanti','gestione_partecipanti.py')
            self.menuButton(u'!!Area Admin','backoffice/index.py')
            self.menuButton(u'!!Esci','LOGOUT')
        
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
