#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('cliente', pkey='id', name_long='!!Cliente', name_plural='!!Cliente',caption_field='ragione_sociale')
        self.sysFields(tbl)
        tbl.column('ragione_sociale' ,size=':40',name_long='!!Ragione sociale',name_short='Rag. Soc.')
        tbl.column('indirizzo',name_long='!!Indirizzo')
        tbl.column('provincia',size='2',name_long='!!Provincia',name_short='Pr.').relation('glbl.provincia.sigla',relation_name='clienti',mode='foreignkey',onDelete='raise')
        tbl.column('comune_id',size='22' ,group='_',name_long='!!Comune').relation('glbl.comune.id',relation_name='clienti',mode='foreignkey',onDelete='raise')
        tbl.column('cliente_tipo_codice',size=':5',name_long='!!Tipo cliente',name_short='Tipo').relation('cliente_tipo.codice',relation_name='clienti',mode='foreignkey',onDelete='raise')
        tbl.column('pagamento_tipo_codice',size=':5',name_long='!!Tipo pagamento',name_short='Tipo pagamento').relation('pagamento_tipo.codice',relation_name='clienti',mode='foreignkey',onDelete='raise')
        tbl.column('note',name_long='!!Note')
        tbl.column('email',name_long='!!Email')
        tbl.formulaColumn('n_fatture',select=dict(table='fatt.fattura',
                                                  columns='COUNT(*)',
                                                  where='$cliente_id=#THIS.id'),
                                      dtype='L',name_long='N.Fatture')

        tbl.formulaColumn('tot_fatturato',select=dict(table='fatt.fattura',
                                                  columns='SUM($totale_fattura)',
                                                  where='$cliente_id=#THIS.id'),
                                      dtype='N',name_long='Tot.Fatturato')