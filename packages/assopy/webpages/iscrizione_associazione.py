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
    py_requires='basecomponent:Public'
    
    def windowTitle(self):
         return '!!Assopy Diventa Socio'

    def main(self, root,fromPage='index.py', **kwargs):
        root.data('fromPage',fromPage)
        top,client,bottom = self.publicPane(root, 'Iscrizione Associazione', height='230px', align='center', valign='middle')
        bottom.div('Torna al menu',connect_onclick='genro.gotoURL("index.py")',_class='pbl_button pbl_cancel',float='right',width='9em')
    


