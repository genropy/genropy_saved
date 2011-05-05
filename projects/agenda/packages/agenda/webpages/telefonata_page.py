# -*- coding: UTF-8 -*-

# telefonata_page.py
# Created by Niso on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

import datetime

class GnrCustomWebPage(object):
    maintable = 'agenda.telefonata'
    py_requires = """public:TableHandlerMain
                     """
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Telefonate'
        
    def barTitle(self):
        return '!!Telefonate'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def th_form(self,form,**kwargs):
        pane = form.record
        fb = pane.formbuilder(cols=3,fld_width='15em',lbl_color='teal')
        fb.field('giorno',readOnly=True,width='6em',tooltip='Campo non modificabile')
        fb.field('ora',readOnly=True,width='6em',tooltip='Campo non modificabile')
        fb.field('username',readOnly=True,lbl='Utente',tooltip='Campo non modificabile')
        fb.field('contatto_id',zoom=True,lbl='Chiamante',colspan=2,
                  selected_azienda_id='.azienda_id',
                  validate_notnull=True,validate_notnull_error='!!Campo obbligatorio')
        pane.dataFormula("aux.mostra_contatto",'true',_if='contatto_id',_else='false',
                          contatto_id='^.contatto_id')
        fb.button('Mostra dati chiamante',action='genro.wdgById("info_chiamante").show()',
                  visible='^aux.mostra_contatto')
        fb.field('destinatario_id',lbl='!!Destinatario',colspan=2)
        pane.dataFormula("aux.mostra_destinatario",'true',_if='destinatario_id',_else='false',
                          destinatario_id='^.destinatario_id')
        fb.button('Mostra dati destinatario',action='genro.wdgById("info_destinatario").show()',
                  visible='^aux.mostra_destinatario')
        fb.field('descrizione',tag='textarea',colspan=3,width='100%',height='60px')
        
        dlg = pane.dialog(nodeId='info_chiamante',title='INFO CHIAMANTE')
        fb = dlg.formbuilder(lbl_color='teal',margin='6px')
        fb.div('^.@contatto_id.@anagrafica_id.telefono',lbl='Telefono personale')
        fb.div('^.@azienda_id.@anagrafica_id.ragione_sociale', lbl='Azienda')
        fb.div('^.@contatto_id.@anagrafica_id.email', lbl='Mail personale')
        fb.div('^.@azienda_id.@anagrafica_id.telefono', lbl='Telefono azienda')
        fb.button('Chiudi',action='genro.wdgById("info_chiamante").hide()',width='6em')
        
        dlg = pane.dialog(nodeId='info_destinatario',title='INFO DESTINATARIO',cols=2)
        fb = dlg.formbuilder(lbl_color='teal',margin='6px')
        fb.div('^.@destinatario_id.@anagrafica_id.email',lbl='email')
        fb.div('^.@destinatario_id.@anagrafica_id.telefono',lbl='telefono')
        fb.div('^.@destinatario_id.@anagrafica_id.codice_fiscale',lbl='codice fiscale')
        fb.div('^.@destinatario_id.@anagrafica_id.partita_iva',lbl='partita IVA')
        fb.div('^.@destinatario_id.@anagrafica_id.ruolo',lbl='ruolo')
        fb.div('^.@destinatario_id.@anagrafica_id.note',lbl='note')
        
        fb.button('Chiudi',action='genro.wdgById("info_destinatario").hide()',width='6em')
        
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['username'] = self.user
            record['giorno'] = self.workdate # alternativo a "record['giorno'] = str(datetime.datetime.now().date())"
            record['ora'] = datetime.datetime.now().time()
            