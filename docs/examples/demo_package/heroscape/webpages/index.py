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
    
    py_requires = 'public:Public'
    
    def windowTitle(self):
         return '!!Heroscape'
    
    def pageAuthTags(self, method=None, **kwargs):
        return None
    
    def main(self, root, **kwargs):
        top,client,bottom=self.publicPane(root,'!!Gestione - Heroscape')
        self.currTbl=None
        self.clientPane=client

        client.div(template='!!Benvenuto ^.firstname', datasource='^_pbl.user_record', _class='pbl_largemessage', 
                   margin='auto', margin_top='1em', margin_bottom='2em')
        self.menuButton(u'!!Unità','gestione_unita.py')
        self.menuButton(u'!!Cambia password','../adm/change_password.py')
        self.menuButton(u'!!Esci','LOGOUT')
        
    
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
