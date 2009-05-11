#!/usr/bin/env python
# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        
        tbl =  pkg.table('pagamento',  pkey='id',name_long='!!Pagamento', name_plural='!!Pagamenti',rowcaption='codice,data_inserimento')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('data_inserimento', 'D', name_long='!!Data inserimento')
        tbl.column('data_pagamento', 'D', name_long='!!Data pagamento')
        tbl.column('ordine_id', size='22',name_long='!!Ordine').relation('assopy.ordine.id', mode='foreignkey')
        tbl.column('importo_richiesto','R', name_long='!!Importo Richiesto')
        tbl.column('importo','R', name_long='!!Importo Pagato')
        tbl.column('spese_pagamento','R', name_long='!!Spese pagamento')
        tbl.column('netto','R', name_long='!!Importo Netto')
        tbl.column('mezzo', size=':12',name_long='!!Mezzo')
        tbl.column('txn_id', size=':60',name_long='!!ID Transazione')
        tbl.column('dettagli', 'T',name_long='!!Dettagli Transazione')

    def arrivoPagamento(self, id, data_pagamento, data_fattura, importo, spese_pagamento=None, netto=None, txn_id=None, dettagli=None):
        record = self.record(id, mode='record')
        if not record['data_pagamento']:
            record['data_pagamento'] = data_pagamento
            record['importo'] = importo
            record['spese_pagamento'] = spese_pagamento or 0
            record['netto'] = netto or (importo - (spese_pagamento or 0))
            record['txn_id'] = txn_id
            record['dettagli'] = dettagli
            self.update(record)
            
            self.db.table('assopy.ordine').pagamentoRicevuto(id_pagamento=id, 
                                                             id_ordine=record['ordine_id'], 
                                                             data_pagamento=data_pagamento, importo=importo, 
                                                             data_fattura=data_fattura)
            return record['ordine_id']

     