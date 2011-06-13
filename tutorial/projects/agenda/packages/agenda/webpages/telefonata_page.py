# -*- coding: UTF-8 -*-

# telefonata_page.py
# Created by Filippo Astolfi on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

import datetime

class GnrCustomWebPage(object):
    maintable = 'agenda.telefonata'
    py_requires = """public:TableHandlerMain"""
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Calls'
        
    def barTitle(self):
        return '!!Calls'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def th_form(self,form,**kwargs):
        pane = form.record
        fb = pane.formbuilder(cols=3,fld_width='15em',lbl_color='teal')
        fb.field('giorno',readOnly=True,name='!!Day',
                  width='6em',tooltip='The field is not editable')
        fb.field('ora',readOnly=True,name='!!Hour',
                  width='6em',tooltip='The field is not editable')
        fb.field('username',readOnly=True,lbl='!!User',tooltip='The field is not editable')
        fb.field('contatto_id',zoom=True,lbl='!!Caller',colspan=2,
                  selected_azienda_id='.azienda_id',
                  validate_notnull=True,validate_notnull_error='!!Required field')
        pane.dataFormula("aux.mostra_contatto",'true',_if='contatto_id',_else='false',
                          contatto_id='^.contatto_id')
        fb.button('Show caller data',action='genro.wdgById("info_chiamante").show()',
                  visible='^aux.mostra_contatto')
        fb.field('destinatario_id',lbl='!!Receiver',colspan=2)
        pane.dataFormula("aux.mostra_destinatario",'true',_if='destinatario_id',_else='false',
                          destinatario_id='^.destinatario_id')
        fb.button('Show receiver data',action='genro.wdgById("info_destinatario").show()',
                  visible='^aux.mostra_destinatario')
        fb.field('descrizione',lbl='!!Description',lbl_vertical_align='top',
                  tag='simpletextarea',colspan=3,width='100%',height='60px')
        
        dlg = pane.dialog(nodeId='info_chiamante',title='CALLER INFO')
        fb = dlg.formbuilder(lbl_color='teal',margin='6px')
        fb.div('^.@contatto_id.@anagrafica_id.telefono',lbl='!!Personal phone')
        fb.div('^.@azienda_id.@anagrafica_id.ragione_sociale', lbl='!!Company name')
        fb.div('^.@contatto_id.@anagrafica_id.email', lbl='!!Personal email')
        fb.div('^.@azienda_id.@anagrafica_id.telefono', lbl='!!Company phone')
        fb.button('Close',action='genro.wdgById("info_chiamante").hide()',width='6em')
        
        dlg = pane.dialog(nodeId='info_destinatario',title='RECEIVER INFO',cols=2)
        fb = dlg.formbuilder(lbl_color='teal',margin='6px')
        fb.div('^.@destinatario_id.@anagrafica_id.email',lbl='!!Email')
        fb.div('^.@destinatario_id.@anagrafica_id.telefono',lbl='!!Phone')
        fb.div('^.@destinatario_id.@anagrafica_id.codice_fiscale',lbl='!!Tax code')
        fb.div('^.@destinatario_id.@anagrafica_id.partita_iva',lbl='!!VAT')
        fb.div('^.@destinatario_id.@anagrafica_id.ruolo',lbl='!!Role')
        fb.div('^.@destinatario_id.@anagrafica_id.note',lbl='!!Notes')
        
        fb.button('Close',action='genro.wdgById("info_destinatario").hide()',width='6em')
        
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['username'] = self.user
            record['giorno'] = self.workdate # alternativo a "record['giorno'] = str(datetime.datetime.now().date())"
            record['ora'] = datetime.datetime.now().time()
            