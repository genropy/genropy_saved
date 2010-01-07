#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """
from urllib import urlencode
import urllib2

import datetime
import time

from gnr.core.gnrlang import errorTxt

from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public,utils:SendMail'
    
    def rpc_IPNfromPayPal(self, **kwargs):
        try:
            body = '\n'.join(['%s: %s' % (k,str(v)) for k,v in kwargs.items()])
            self.application.sendmail('test_pp@softwell.it', 'fcavazza@softwell.it', 'richiesta IPN', body)
        
            t = time.time()
            conf = self.confirm_paypal(**kwargs)
            conftime = time.time() - t
            savetime = 0
            if conf:
                t = time.time()
                if kwargs['payment_status'] == 'Completed':
                    self._rpc_confermaBonifico(paypalData=kwargs)
                    savetime = time.time() - t
            body = '\n'.join(['%s: %s' % (k,str(v)) for k,v in kwargs.items()])
            body = '%s\n\n\nconferma: %.3f\nsalva: %.3f\nconfermato: %s' % (body, conftime, savetime, str(conf))
            self.application.sendmail('test_pp@softwell.it', 'fcavazza@softwell.it', 'conferma IPN', body)
        except:
            self.application.sendmail('test_pp@softwell.it', 'fcavazza@softwell.it', 'errore python IPN', errorTxt())

    def _rpc_confermaBonifico(self, paypalData, **kwargs):
        id = paypalData['custom']
        data_pagamento=self.workdate
        data_fattura=self.workdate
        importo=float(paypalData['mc_gross'])
        spese_pagamento= float(paypalData['mc_fee'])
        txn_id = paypalData['txn_id']
        dettagli = '\n'.join(['%s: %s' % (k,str(v)) for k,v in paypalData.items()])
                                                          
        ordine_id = self.db.table('assopy.pagamento').arrivoPagamento(id = id,
                                                                      data_pagamento=data_pagamento,
                                                                      data_fattura=data_fattura,
                                                                      importo=importo,
                                                                      spese_pagamento= spese_pagamento,
                                                                      txn_id = txn_id,
                                                                      dettagli = dettagli
                                                                      )
        self.db.commit()
        if ordine_id: # only if a new document is confirmed, paypal sends many IPN
            self.inviaLinkDocumento(ordine_id)
        

    
    def confirm_paypal(self, test_ipn=None, **kwargs):
        PP_URL = self.get_paypal_site(test_ipn) #"https://www.sandbox.paypal.com/cgi-bin/webscr"
        kwargs["cmd"]="_notify-validate"
        params = urlencode(kwargs)
        
        req = urllib2.Request(PP_URL)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        fo = urllib2.urlopen(PP_URL, params)
        ret = fo.read()
        if (ret == "VERIFIED"):
            return True
        else:
            body = ret + '\n\n\n' + '\n'.join(['%s: %s' % (k,str(v)) for k,v in kwargs.items()])
            self.application.sendmail('test_pp@softwell.it', 'fcavazza@softwell.it', 'errore IPN', body)
            

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index(method='IPNfromPayPal')
