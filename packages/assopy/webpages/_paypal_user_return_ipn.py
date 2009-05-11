#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" _paypal_user_return_ipn.py """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    
    def windowTitle(self):
        return '!!Pagamento effettuato'

    def main(self, root,fromPage='index.py', **kwargs):
        root.data('fromPage',fromPage)
        top,client,bottom = self.publicPane(root, '!!Pagamento effettuato', height='230px')
        client.div(u"!!Il pagamento è stato ricevuto correttamente",_class='pbl_largemessage',_class='pbl_largemessage',
                                    margin_top='2em',margin='auto')
        client.div(u"!!Riceverai a breve una mail con il link al documento che potrai stampare.",_class='pbl_largemessage',_class='pbl_largemessage',
                                                                margin_top='2em',margin='auto')
        bottom.div('!!Torna al menu',connect_onclick='genro.gotoHome()',_class='pbl_button pbl_cancel',float='right',width='14em')
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
