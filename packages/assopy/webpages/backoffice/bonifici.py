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
    py_requires='basecomponent:Public,utils:SendMail'
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'contabile'
        
    def main(self, root, **kwargs):
        root.dataRpc('dummy', 'confermaBonifico', bonifico='=bonifico', fired='^conferma', _onResult='alert("Pagamento Confermato");genro.setData("bonifico", null);')

        fb = root.formbuilder(cols=1, datapath='bonifico')
        fb.dbSelect(lbl='Codice', value='^.id', dbtable='assopy.pagamento', 
                    columns='@ordine_id.numero, @ordine_id.@anagrafica_id.ragione_sociale', auxColumns='$importo_richiesto',
                    condition='$data_pagamento IS NULL', selected_importo_richiesto='^.importo'
                )
        fb.numbertextbox(lbl='Importo', value='^.importo')
        fb.numbertextbox(lbl='Spese', value='^.spese')
        fb.button('Conferma pagamento', fire='conferma')
        
        
    def rpc_confermaBonifico(self, bonifico, **kwargs):
        ordine_id = self.db.table('assopy.pagamento').arrivoPagamento(id = bonifico['id'],
                                                          importo=bonifico['importo'], 
                                                          spese_pagamento=bonifico['spese'], 
                                                          netto=bonifico['netto'], 
                                                          data_pagamento=self.workdate,
                                                          data_fattura=self.workdate
                                                          )
        self.db.commit()
        
        self.inviaLinkDocumento(ordine_id)
        

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
