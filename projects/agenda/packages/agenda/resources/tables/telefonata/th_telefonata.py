# -*- coding: UTF-8 -*-

# th_telefonata.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
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
        
    def th_order(self):
        return '@anagrafica_id.cognome'
        
    def th_query(self):
        return dict(column='@anagrafica_id.cognome', op='contains', val='', runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
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