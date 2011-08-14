# -*- coding: UTF-8 -*-

# th_contatto.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
        
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@anagrafica_id.nome', name='!!Name', width='8%')
        r.fieldcell('@anagrafica_id.cognome', name='!!Surname', width='8%')
        r.fieldcell('@anagrafica_id.email', name='!!Personal email', width='12%')
        r.fieldcell('@anagrafica_id.telefono', name='!!Personal phone', width='7%')
        r.fieldcell('@anagrafica_id.codice_fiscale', name='!!Tax code', width='10%')
        r.fieldcell('@anagrafica_id.partita_iva', name='!!Personal VAT', width='7%')
        r.fieldcell('@anagrafica_id.fax', name='!!Personal fax', width='7%')
        r.fieldcell('interno', width='4%')
        r.fieldcell('@azienda_id.@anagrafica_id.ragione_sociale', name='!!Company name', width='18%')
        r.fieldcell('ruolo', width='10%')
        r.fieldcell('@anagrafica_id.note', name='!!Personal notes', width='9%')
        
    def th_order(self):
        return '@anagrafica_id.cognome'
        
    def th_query(self):
        return dict(column='@anagrafica_id.nome', op='contains', val='', runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2,border_spacing='6px',fld_width='15em',lbl_color='teal')
        fb.field('@anagrafica_id.nome',lbl='!!Name',validate_case='c')
        fb.field('@anagrafica_id.cognome',lbl='!!Surname',validate_case='c')
        fb.field('@anagrafica_id.email',lbl='!!Personal email',validate_email=True,
                  validate_email_error='!!Formato email non corretto')
        fb.field('@anagrafica_id.telefono',lbl='!!Personal phone')
        fb.field('@anagrafica_id.codice_fiscale',lbl='!!Personal tax code',validate_case='u')
        fb.field('@anagrafica_id.partita_iva',lbl='!!Personal VAT')
        fb.field('@anagrafica_id.fax',lbl='!!Personal fax')
        fb.field('interno')
        fb.field('azienda_id',lbl='!!Company name')
        fb.button('Show company data',action='genro.wdgById("info_azienda").show()',
                  visible='^aux.mostra_azienda')
        fb.field('ruolo',tag='combobox',lbl='Personal company role',colspan=2,
                  values='employee, freelancer, manager, owner')
        fb.field('@anagrafica_id.note',lbl='!!Notes', tag='simpletextarea', colspan=2, width='100%')
        
        pane.dataFormula("aux.mostra_azienda",'true',
                         _if='azienda_id',_else='false',azienda_id='^.azienda_id')
        self.showDialog(pane)
        
    def showDialog(self,pane):
        dlg = pane.dialog(nodeId='info_azienda',title='COMPANY DATA')
        fb = dlg.formbuilder(cols=2,lbl_color='teal',margin='6px',fld_width='12em')
        fb.div('^.@azienda_id.@anagrafica_id.telefono', lbl='Phone')
        fb.div('^.@azienda_id.@anagrafica_id.email', lbl='Email')
        fb.div('^.@azienda_id.@anagrafica_id.indirizzo', lbl='Address')
        fb.div('^.@azienda_id.@anagrafica_id.cap', lbl='Postcode')
        fb.div('^.@azienda_id.@anagrafica_id.localita', lbl='Location')
        fb.div('^.@azienda_id.tipologia', lbl='Type')
        fb.div('^.@azienda_id.@anagrafica_id.partita_iva', lbl='VAT')
        fb.div('^.@azienda_id.@anagrafica_id.fax', lbl='Fax')
        fb.div('^.@azienda_id.@anagrafica_id.www', lbl='Web site')
        fb.button('Close',width='6em',action='genro.wdgById("info_azienda").hide()')