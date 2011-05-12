# -*- coding: UTF-8 -*-

# th_azienda.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@anagrafica_id.ragione_sociale', width='18%')
        r.fieldcell('@anagrafica_id.telefono', width='6%')
        r.fieldcell('@anagrafica_id.email', width='12%')
        r.fieldcell('tipologia', width='6%')
        r.fieldcell('@anagrafica_id.indirizzo',width='12%')
        r.fieldcell('@anagrafica_id.cap', width='4%')
        r.fieldcell('@anagrafica_id.localita', width='7%')
        r.fieldcell('@anagrafica_id.partita_iva', width='7%')
        r.fieldcell('@anagrafica_id.fax', width='6%')
        r.fieldcell('@anagrafica_id.www', name='!!Sito web', width='13%')
        r.fieldcell('@anagrafica_id.note', width='9%')
        return struct
        
    def th_order(self):
        return '@anagrafica_id.ragione_sociale'
        
    def th_query(self):
        return dict(column='@anagrafica_id.ragione_sociale', op='contains', val='', runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        pane.dataFormula("#FORM.title", '"Scheda azienda: " + titolo',titolo='^.@anagrafica_id.ragione_sociale',
                        _if='titolo',_else='"Scheda azienda: nuova azienda"')
        fb = pane.formbuilder(cols=2,border_spacing='6px',lbl_width='6em',
                              fld_width='15em',width='40em',lbl_color='teal')
        fb.field('@anagrafica_id.ragione_sociale',colspan=2,width='100%',
                  validate_notnull=True,
                  validate_notnull_error='!!Campo obbligatorio')
        fb.field('@anagrafica_id.email',validate_email=True,
                  validate_email_error='!!Formato email non corretto',colspan=2)
        fb.field('@anagrafica_id.telefono')
        fb.field('@anagrafica_id.fax')
        fb.field('@anagrafica_id.indirizzo',validate_case='capitalize',
                  tag='textarea',lbl_vertical_align='top',width='100%',colspan=2)
        fb.field('@anagrafica_id.cap')
        fb.field('@anagrafica_id.localita')
        fb.field('@anagrafica_id.partita_iva')
        fb.field('tipologia',tag='combobox',values='cliente, fornitore')
        fb.field('@anagrafica_id.www',lbl='Sito web',colspan=2)
        fb.field('@anagrafica_id.note',tag='textarea',lbl_vertical_align='top',width='100%',colspan='2')
        
class FormFull(BaseComponent):
    def th_form(self, form):
        tc = form.center.tabContainer()
        self.mainInfoAzienda(tc.contentPane(title='Info base',datapath='.record',nodeId='aziendaRecord'))
        pane = tc.contentPane(title='Contatti')
       #th = pane.dialogTableHandler(table='agenda.contatto',condition='$azienda_id=:azienda_id',condition_azienda_id='^#FORM.pkey',
       #                       formResource=':FormFromAzienda',viewResource=':ViewFromAzienda',dialog_height='200px',dialog_width='400px')
       #th.form.store.handler('load',default_azienda_id='^#aziendaRecord.id')
        pane.dialogTableHandler(relation='@contatti',
                                formResource=':FormFromAzienda',
                                viewResource=':ViewFromAzienda',
                                dialog_height='200px',dialog_width='400px')
                                 
    def mainInfoAzienda(self,pane):
        pane.dataFormula("#FORM.title", '"Scheda azienda: " + titolo',titolo='^.@anagrafica_id.ragione_sociale',
                        _if='titolo',_else='"Scheda azienda: nuova azienda"')
        fb = pane.formbuilder(cols=2,border_spacing='6px',lbl_width='6em',
                              fld_width='15em',width='40em',lbl_color='teal')
        fb.field('@anagrafica_id.ragione_sociale',colspan=2,width='100%',
                  validate_notnull=True,
                  validate_notnull_error='!!Campo obbligatorio')
        fb.field('@anagrafica_id.email',validate_email=True,
                  validate_email_error='!!Formato email non corretto',colspan=2)
        fb.field('@anagrafica_id.telefono')
        fb.field('@anagrafica_id.fax')
        fb.field('@anagrafica_id.indirizzo',validate_case='capitalize',
                  tag='textarea',lbl_vertical_align='top',width='100%',colspan=2)
        fb.field('@anagrafica_id.cap')
        fb.field('@anagrafica_id.localita')
        fb.field('@anagrafica_id.partita_iva')
        fb.field('tipologia',tag='combobox',values='cliente, fornitore')
        fb.field('@anagrafica_id.www',lbl='Sito web',colspan=2)
        fb.field('@anagrafica_id.note',tag='textarea',lbl_vertical_align='top',width='100%',colspan='2')
            