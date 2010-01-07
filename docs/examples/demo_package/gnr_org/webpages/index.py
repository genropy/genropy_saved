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

class GnrCustomWebPage(object):
    
    py_requires = 'public:Public'
    
    def windowTitle(self):
         return '!!Genropy.org'
    
    def pageAuthTags(self, method=None, **kwargs):
        return None
    
    def main(self, root, **kwargs):
        top,client,bottom=self.publicPane(root,'!!Genropy Demo')
        self.currTbl=None
        self.clientPane=client

        client.div(template='!!Benvenuto ^.firstname', datasource='^_pbl.user_record', _class='pbl_largemessage', 
                   margin='auto', margin_top='1em', margin_bottom='2em')
        self.menuButton(u'!!Showcase','../showcase/index.py')
        self.menuButton(u'!!Heroscape','../heroscape/index.py')
        self.menuButton(u'!!Cambia password','../adm/change_password.py')
        self.menuButton(u'!!Esci','LOGOUT')
        
    
