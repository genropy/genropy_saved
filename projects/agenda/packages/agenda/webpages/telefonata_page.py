#!/usr/bin/env python
# encoding: utf-8
"""
Created by Filippo Astolfi on 2011-01-25.
Copyright (c) 2011 Softwell. All rights reserved.
"""

import datetime

class GnrCustomWebPage(object):
    maintable = 'agenda.telefonata'
    py_requires = 'public:Public,standard_tables:TableHandler,public:IncludedView'
    
    ######################## STANDARD TABLE OVERRIDDEN METHODS ################
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def userCanWrite(self):
        return True
        
    def userCanDelete(self):
        return True
        
    def windowTitle(self):
        return '!!Telefonate'
        
    def barTitle(self):
        return '!!Telefonate'
        
    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell(field='giorno',width='5%')
        r.fieldcell('ora',width='3%')
        r.fieldcell('username', name='!!Utente', width='8%')
        r.fieldcell('destinatario', name='!!Chi ha cercato', width='9%')
        r.fieldcell('cognome', name='!!Chi ha chiamato', width='8%')
        r.fieldcell('@contatto_id.@anagrafica_id.telefono', name='!!Telefono personale', width='7%')
        r.fieldcell('@contatto_id.@anagrafica_id.email', name='Mail personale', width='12%')
        r.fieldcell('@azienda_id.@anagrafica_id.ragione_sociale', name='!!Azienda', width='18%')
        r.fieldcell('@azienda_id.@anagrafica_id.telefono', name='!!Telefono azienda', width='8%')
        r.fieldcell('descrizione', width='22%')
        return struct
        
    def printazioneBase(self):
        return True
        
    def exportazioneBase(self):
        return True
        
    def orderBase(self):
        return 'giorno'
        
    def queryBase(self):
        return dict(column='', op='', val='', runOnStart=True)
        
    ############################## FORM METHODS ##################################
        
    def formBase(self, parentBC, disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=3,fld_width='15em',
                              disabled=disabled,lbl_color='teal')
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
        
        self.showCallerDialog(parentBC)
        self.showReceiverDialog(parentBC)
        
    def showCallerDialog(self, pane):
        dlg = pane.dialog(nodeId='info_chiamante',title='INFO CHIAMANTE',datapath='form.record')
        fb = dlg.formbuilder(lbl_color='teal',margin='6px')
        fb.div('^.@contatto_id.@anagrafica_id.telefono',lbl='Telefono personale')
        fb.div('^.@azienda_id.@anagrafica_id.ragione_sociale', lbl='Azienda')
        fb.div('^.@contatto_id.@anagrafica_id.email', lbl='Mail personale')
        fb.div('^.@azienda_id.@anagrafica_id.telefono', lbl='Telefono azienda')
        fb.button('Chiudi',action='genro.wdgById("info_chiamante").hide()',width='6em')
        
    def showReceiverDialog(self, pane):
        dlg = pane.dialog(nodeId='info_destinatario',title='INFO DESTINATARIO',datapath='form.record',cols=2)
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
            