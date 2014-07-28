#!/usr/bin/env python
# encoding: utf-8


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('localita', pkey='id', name_long='Localita', rowcaption='nome,@provincia.sigla:%s (%s)')
        tbl.column('id', size='22', group='_', readOnly=True, name_long='!!Id',unique=True)
        tbl.column('nome', size=':52', name_long='Nome', indexed=True)
        tbl.column('provincia', size='2', name_long='Provincia').relation('glbl.provincia.sigla', mode='foreignkey',
                                                                           onUpdate_sql='cascade', onDelete='raise',relation_name='localita')
        tbl.column('codice_istat', size='6', name_long='Codice Istat')
        tbl.column('codice_comune', size='4', name_long='Codice Comune')
        tbl.column('prefisso_tel', size='4', name_long='Prefisso Tel')
        tbl.column('cap', size='5', name_long='CAP', indexed=True)
        tbl.column('comune_id' ,size='22',name_long='!!Comune').relation('glbl.comune.id', mode='foreignkey',relation_name='localita')
        


    def allineaComune(self):
        comuni = self.db.table('glbl.comune').query(columns='*,lower(denominazione) AS den_low').fetchAsDict('den_low')
        def cb(row):
            if row['nome']:
                comune = comuni.get(row['nome'].lower())
                if comune:
                    row['comune_id'] = comune['id']
        self.batchUpdate(cb,where='$id IS NOT NULL')
