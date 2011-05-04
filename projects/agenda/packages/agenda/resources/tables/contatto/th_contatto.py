# -*- coding: UTF-8 -*-

# th_contatto.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@anagrafica_id.nome', width='8%')
        r.fieldcell('@anagrafica_id.cognome', width='8%')
        r.fieldcell('@anagrafica_id.email', name='!!Mail personale', width='12%')
        r.fieldcell('@anagrafica_id.telefono', name='!!Telefono personale', width='7%')
        r.fieldcell('@anagrafica_id.codice_fiscale', width='10%')
        r.fieldcell('@anagrafica_id.partita_iva', name='!!P.IVA personale', width='7%')
        r.fieldcell('@anagrafica_id.fax', name='!!Fax personale', width='7%')
        r.fieldcell('interno', width='4%')
        r.fieldcell('@azienda_id.@anagrafica_id.ragione_sociale', zoom=True, width='18%')
        r.fieldcell('ruolo', width='10%')
        r.fieldcell('@anagrafica_id.note', name='!!Note personali', width='9%')
        return struct
        
    def th_order(self):
        return '@anagrafica_id.cognome'
        
    def th_query(self):
        return dict(column='@anagrafica_id.cognome', op='', val='', runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, pane):
        pane.dataFormula("form.title", '"Scheda contatto: " + nome + " " + cognome',
                        nome='^.@anagrafica_id.nome', cognome='^.@anagrafica_id.cognome',
                        _if='nome && cognome',_else='"Scheda contatto: nuovo contatto"')
        fb = pane.formbuilder(cols=2,border_spacing='6px',fld_width='15em',lbl_color='teal')
        fb.field('@anagrafica_id.nome',validate_case='c')
        fb.field('@anagrafica_id.cognome',validate_case='c')
        fb.field('@anagrafica_id.email',validate_email=True,
                  validate_email_error='!!Formato email non corretto')
        fb.field('@anagrafica_id.telefono')
        fb.field('@anagrafica_id.codice_fiscale',validate_case='u')
        fb.field('@anagrafica_id.partita_iva')
        fb.field('@anagrafica_id.fax')
        fb.field('interno')
        fb.field('azienda_id',zoom=True)
        fb.button('Mostra dati azienda',action='genro.wdgById("info_azienda").show()',
                  visible='^aux.mostra_azienda')
        fb.field('ruolo',tag='combobox',lbl='Ruolo nell\'azienda',colspan=2,
                  values='dipendente,libero professionista,manager,titolare')
        fb.field('@anagrafica_id.note', tag='textarea', colspan=2, width='100%')
        
        pane.dataFormula("aux.mostra_azienda",'true',
                         _if='azienda_id',_else='false',azienda_id='^.azienda_id')
        self.showDialog(pane)
        
    def showDialog(self, pane):
        dlg = pane.dialog(nodeId='info_azienda',title='DATI AZIENDA',datapath='form.record')
        fb = dlg.formbuilder(cols=2,lbl_color='teal',margin='6px',fld_width='12em')
        fb.div('^.@azienda_id.@anagrafica_id.telefono', lbl='Telefono')
        fb.div('^.@azienda_id.@anagrafica_id.email', lbl='Mail')
        fb.div('^.@azienda_id.@anagrafica_id.indirizzo', lbl='Indirizzo')
        fb.div('^.@azienda_id.@anagrafica_id.cap', lbl='Cap')
        fb.div('^.@azienda_id.@anagrafica_id.localita', lbl='Località')
        fb.div('^.@azienda_id.tipologia', lbl='Tipologia')
        fb.div('^.@azienda_id.@anagrafica_id.partita_iva', lbl='P.IVA')
        fb.div('^.@azienda_id.@anagrafica_id.fax', lbl='Fax')
        fb.div('^.@azienda_id.@anagrafica_id.www', lbl='Sito web')
        fb.button('Chiudi',width='6em',action='genro.wdgById("info_azienda").hide()')