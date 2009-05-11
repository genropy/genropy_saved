#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('ordine_riga',  pkey='id',name_long='!!Riga ordine',name_plural='!!Righe Ordine', rowcaption='numero_riga,tipo,prezzo: %s %s:%s')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('ordine_id', size='22',name_long='!!Ordine').relation('assopy.ordine.id', mode='foreignkey')
        tbl.column('numero_riga','L', name_long='!!Numero riga')
        tbl.column('tariffa_id', size='22',name_long='!!Tariffa', group='_').relation('assopy.tariffa.id', mode='foreignkey')
        tbl.column('tariffa_codice', size=':12',name_long='!!Codice Tariffa')
        tbl.column('tariffa_descrizione', size=':40',name_long='!!Descrizione Tariffa')
        tbl.column('testo_riga', name_long='!!Testo Riga')
        tbl.column('importo','R',name_long='!!Prezzo')
        tbl.column('aliquota_iva',size='2',name_long='!!IVA')
        tbl.aliasTable('partecipante', '@assopy_partecipante_ordine_riga_id')

    def trigger_onDeleting(self, record_data):
        self.db.table('assopy.partecipante').deleteSelection('ordine_riga_id', record_data[self.pkey])

    def recordLoader(self, data):
        pass
    
    def recordRecipe(self, data):
        """
            <id>dfsduuyiutr</id>
            <ordine_id>sdfghjk345678</ordine_id>
            <numero_riga _T='L'>0</numero_riga>
            <tariffa_id>45678909876rtyuio</tariffa_id>
            <tariffa_codice>LATESTU08</tariffa_codice>
            <tariffa_descrizione>Studenti Late</tariffa_descrizione>
            <testo_riga>Studenti Late: Francesco</testo_riga>
            <importo _T='R'>100.0</importo>
            <aliquota_iva >20</aliquota_iva>
            <partecipante _table='assopy.partecipante'>
                <cognome ></cognome>
            </partecipante>
        """
        pass
    
    