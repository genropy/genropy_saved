#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        
        tbl =  pkg.table('ordine',  pkey='id',name_long='!!Ordine',name_plural='!!Ordini',rowcaption='codice,data_inserimento')
        
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        
        tbl.column('numero', size=':12', name_long='!!Numero')
        tbl.column('tipo_protocollo', size=':2', name_long='!!Tipo Protocollo')
        tbl.column('tipo_ordine', size=':12', name_long='!!Tipo Ordine')
        tbl.column('data_inserimento', 'D', name_long='!!Data')
        tbl.column('data_conferma', 'D', name_long='!!Data conferma')
        tbl.column('data_pagamento', 'D', name_long='!!Data pagamento')
        tbl.column('evento_id', size='22',name_long='!!Id Evento').relation('assopy.evento.id', mode='foreignkey')
        tbl.column('anagrafica_id', size='22',name_long='Id Anagrafica').relation('assopy.anagrafica.id', mode='foreignkey')
        tbl.column('imponibile','R', name_long='!!Imponibile')
        tbl.column('iva','R', name_long='!!Iva')
        tbl.column('totale','R', name_long='!!Totale')
        tbl.column('cond_pagamento', size=':12',name_long='Condizioni di pagamento')
        tbl.column('fattura_num', size=':12',name_long='!!Fattura')
        tbl.column('fattura_data', 'D',name_long='!!Data fattura')
        tbl.column('cliente_rif', size=':30',name_long='!!Riferimento')
        tbl.column('cliente_atn', size=':30',name_long='!!Attenzione')
        tbl.aliasColumn('tariffa', relation_path='@assopy_ordine_riga_ordine_id.tariffa_codice', name_long='!!Tariffa')
        tbl.aliasColumn('mezzopagamento', relation_path='@assopy_pagamento_ordine_id.mezzo', name_long='!!Pagamento')
        
    def trigger_onDeleting(self, record_data):
        self.db.table('assopy.ordine_riga').deleteSelection('ordine_id', record_data[self.pkey])
                
    def get_numeroOrdine(self, date, code):
        return self.pkg.getCounter(name='ordini', code=code, date=date, codekey='$YY/$K',
                                          output='$K/$YY.$NNNN', phyear=False)
                                          
    def get_numeroFattura(self, date, code):
      return self.pkg.getCounter(name='fatture', code=code, date=date, codekey='$YY/$K',
                                        output='$K/$YY.$NNNN', phyear=False)
    
    def ordineCorrente(self, idAnagrafica, tipoOrdine):
        return self.record(where='$anagrafica_id = :anag AND $data_conferma IS NULL AND $tipo_ordine = :tipoOrdine', 
                           anag = idAnagrafica, tipoOrdine=tipoOrdine, ignoreMissing=True, mode='record')
        
    def getTipiOrdine(self):
        return {'TKT':{'PR_IVA':'A'}, 'DON':{'PR_IVA':None}, 'SPO':{'PR_IVA':'A'}, 'ASC':{'PR_IVA':None}}
        
    def pagamentoRicevuto(self, id_pagamento, id_ordine, data_pagamento, data_fattura, importo):
        record = self.record(id_ordine, mode='record')
        if record['totale'] != importo:
            pass
        
        tipo_fattura = self.getTipiOrdine().get(record['tipo_ordine'],{}).get('PR_IVA')
        if tipo_fattura:
            record['fattura_num'] = self.get_numeroOrdine(data_pagamento, code=tipo_fattura)
            record['fattura_data'] = data_fattura
        record['data_pagamento'] = data_pagamento
        self.update(record)
        
    
    def dboProcess(self, dbo, **kwargs):
        righe = dbo['children.ordine_riga'] 
        if righe:
            righeiva = {}
            for r in righe.values():
                if r['tariffa_id']:
                    rigaiva = righeiva.setdefault(r['aliquota_iva'], {'tot':0, 'imp':0, 'iva':0})
                    rigaiva['tot'] = rigaiva['tot'] + r['importo']
            tot_ordine = {'tot':0, 'imp':0, 'iva':0}
            for aliquota_iva, rigaiva in righeiva.items():
                ali = int(aliquota_iva)
                tot_cent = int(rigaiva['tot'] * 100)
                imp_cent = int(round(tot_cent * 100.0 / (100 + ali)))
                
                rigaiva['imp'] = imp_cent / 100.0
                rigaiva['iva'] = rigaiva['tot'] - rigaiva['imp'] 
                
                tot_ordine['tot'] = tot_ordine['tot'] + rigaiva['tot']
                tot_ordine['imp'] = tot_ordine['imp'] + rigaiva['imp']
                tot_ordine['iva'] = tot_ordine['iva'] + rigaiva['iva']
            tipoiva = dbo['related.anagrafica.tipo_iva']
            if tipoiva and tipoiva != '00':
                dbo['mainrecord.totale'] = tot_ordine['imp']
                dbo['mainrecord.iva'] = 0 
                dbo['mainrecord.imponibile'] = tot_ordine['imp']
            else:
                dbo['mainrecord.totale'] = tot_ordine['tot']
                dbo['mainrecord.iva'] = tot_ordine['iva'] 
                dbo['mainrecord.imponibile'] = tot_ordine['imp']
        
    def dboExecute(self, dbo, **kwargs):
        if not dbo['mainrecord.numero'] and dbo['mainrecord.data_conferma']:
            dbo['mainrecord.numero'] = self.get_numeroOrdine(dbo['mainrecord.data_conferma'], code=dbo['mainrecord.tipo_protocollo'])
        righe=dbo['children.ordine_riga']
        dbo.setItem('children.partecipante', Bag(), _table='assopy.partecipante')
        partecipanti = dbo['children.partecipante']
        
        for i,r in enumerate(righe):
            attr=r.getAttr()
            pkey=r.getAttr('_pkey')
            riga=r.getValue()
            riga['id'] = pkey
            riga['ordine_id'] = dbo['mainrecord.id']
            riga['numero_riga'] = i
            if pkey:
                if riga['tariffa_id']:
                    attr['_opcode']='U'
                else:
                    attr['_opcode']='D'
            elif riga['tariffa_id']:
                attr['_opcode']='I'
                riga['id'] = self.db.table('assopy.ordine_riga').newPkeyValue()
            row_op = attr.get('_opcode')
            if row_op in ('I','U','IU'):
                partecipante = riga.pop('partecipante')
                if partecipante:
                    if row_op in ('U','IU') and not partecipante['id']:
                        oldrec = self.db.table('assopy.partecipante').record(
                                                    ordine_riga_id = riga['id'], mode='record', ignoreMissing=True)
                        if oldrec:
                            partecipante['id'] = oldrec['id']
                    partecipante.pop('presenze')
                    partecipante['ordine_riga_id'] = riga['id']
                    partecipanti.setItem(r.label, partecipante, _opcode=attr['_opcode'])
        self.dboDoExecute(dbo, **kwargs)
        
    
    def dboLoad(self, pkey=None, record=None ,**kwargs):
        dbo = self.dboDoLoad(pkey=pkey,record=record,**kwargs)
        self.dboLoadRelated(dbo)
        getattr(self, 'dboLoadChildren_%s' % dbo['mainrecord.tipo_ordine'])(dbo)
        return dbo
    
    def dboCreate(self, **kwargs):
        dbo = self.dboDoCreate(**kwargs)
        self.dboLoadChildren(dbo)
        self.dboLoadRelated(dbo)
        return dbo
        
    def dboLoadRelated(self, dbo):
        dbo['related.anagrafica'] = self.db.table('assopy.anagrafica').record(dbo['mainrecord.anagrafica_id'], mode='record')
        
    def dboLoadChildren_TKT(self, dbo):
        self.dboLoadChildren(dbo)

    def dboLoadChildren_SPO(self, dbo):
        righe = self.db.query('assopy.ordine_riga', columns='*', order_by='numero_riga',
                              where='ordine_id = :idordine AND @tariffa_id.tipo != :spon', spon='SPO', 
                              idordine=dbo['mainrecord.id']).selection()
        
        dbo.setItem('children.ordine_riga', righe.output('recordlist'), _table='assopy.ordine_riga')
        
        for r in dbo['children.ordine_riga'].values():
            r.setItem('partecipante', self.db.table('assopy.partecipante').record(ordine_riga_id=r['id'], mode='record'), _table='assopy.partecipante')
            
        dbo.setItem('children.pagamento', Bag(), _table='assopy.pagamento')
        
        rigaspon = self.db.query('assopy.ordine_riga', columns='*', order_by='numero_riga',
                              where='ordine_id = :idordine AND @tariffa_id.tipo = :spon', spon='SPO', 
                              idordine=dbo['mainrecord.id']).selection().output('recordlist')
        
        dbo.setItem('sponsorizzazione', rigaspon['#0'], _pkey=rigaspon.getAttr('#0', '_pkey'))
        
        
        

    def dboLoadChildren_DON(self, dbo):
        self.dboLoadChildren(dbo)
        
    def dboLoadChildren(self, dbo):
        righe = self.db.query('assopy.ordine_riga', columns='*', order_by='numero_riga',
                              where='ordine_id = :idordine', idordine=dbo['mainrecord.id']).selection()
        
        dbo.setItem('children.ordine_riga', righe.output('recordlist'), _table='assopy.ordine_riga')
        
        for r in dbo['children.ordine_riga'].values():
            r.setItem('partecipante', self.db.table('assopy.partecipante').record(ordine_riga_id=r['id'], mode='record'), _table='assopy.partecipante')
            
        dbo.setItem('children.pagamento', Bag(), _table='assopy.pagamento')


    def aggiungiRiga(self, dbo, tariffa=None, importo=None, partecipante=None):
        tariffa = tariffa or Bag()
        if isinstance(tariffa, basestring):
            tariffa = self.db.table('assopy.tariffa').record(tariffa).output('bag')
        rnum = len(dbo['children.ordine_riga'])
        riga = self.db.table('assopy.ordine_riga').newrecord(True, 
                                                             ordine_id=dbo['mainrecord.id'],
                                                             numero_riga=rnum,
                                                             tariffa_id=tariffa['id'], 
                                                             tariffa_codice=tariffa['codice'], 
                                                             tariffa_descrizione=tariffa['descrizione'], 
                                                             importo = importo or tariffa['importo'],
                                                             aliquota_iva=tariffa['aliquota_iva'])
        if partecipante:
            riga.setItem('partecipante', partecipante, _table='assopy.partecipante')  
        dbo.setItem('children.ordine_riga.r_%i' % rnum, riga, _opcode='I')    
        
    def aggiungiRigaPagamento(self, dbo, data_inserimento, mezzo, importo_richiesto=None):
        riga = self.db.table('assopy.pagamento').newrecord(True, 
                                                            mezzo = mezzo,
                                                            data_inserimento=data_inserimento,
                                                            ordine_id=dbo['mainrecord.id'],
                                                            importo_richiesto = importo_richiesto or dbo['mainrecord.totale']
                                                        )
        rnum = len(dbo['children.pagamento'])
        dbo.setItem('children.pagamento.r_%i' % rnum, riga, _pkey=riga['id'], _opcode='I')
        

    def dbo(self, data):
        """
        <mainrecord>
            <id >sdfghjk345678</id> 
            <numero >V.2007/00023</numero> 
            <data_inserimento _T='D'>2007-12-23</data_inserimento>
            <data_conferma _T='D'>2007-12-23</data_conferma>
            <data_pagamento _T='D'>2007-12-23</data_pagamento>
            <evento_id>1234567890</evento_id>
            <anagrafica_id>09876543</anagrafica_id>
            <imponibile _T='R'>250.0</imponibile>
            <iva _T='R'>50.0</iva>
            <totale _T='R'>300.0</totale>
            <cond_pagamento _T='D'>paypal</cond_pagamento>
            <fattura_num _T='D'>F.2007/00045</data_conferma>
            <fattura_data _T='D'>2007-12-24</fattura_data>
        <mainrecord>
        <children>
            <ordine_riga _table='assopy.ordine_riga' >
                 <r_1 _pkey='dfsduuyiutr' >
                       assopy.riga_ordine.recordRecipe
                 </r_1>
                 <r_2 _pkey='ytryuiuyt'>
                       assopy.riga_ordine.recordRecipe
                 </r_2>        
            </ordine_riga>
        <children>
        """
        
        pass

    def query_test(self):
        b = Bag()
        b.setItem('c_01', None, column="fattura_num", op="ISNULL", rem='senza fattura')
        b.setItem('c_02', "MI,FI,TO", column="@anagrafica_id.provincia", op="IN", rem='senza fattura', jc='AND')
        
        b.setItem('c_03', None, jc='AND')
        b.setItem('c_03.c_04', '1000', column="totale", op="GT")
        b.setItem('c_03.c_05', '100', column="totale", op="LT", jc='OR')
        return b
        