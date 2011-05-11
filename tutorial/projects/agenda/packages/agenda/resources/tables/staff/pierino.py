# -*- coding: UTF-8 -*-

# th_staff.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@anagrafica_id.nome', width='8%')
        r.fieldcell('@anagrafica_id.cognome', width='8%')
        r.fieldcell('@anagrafica_id.email', name='!!Mail personale', width='14%')
        
    def th_order(self):
        return '@anagrafica_id.cognome'
        
    def th_query(self):
        return dict(column='@anagrafica_id.cognome', op='contains', val='', runOnStart=True)
        
class Paperino(BaseComponent):
    def th_form(self, form):
        pane = form.record
        pane.dataFormula("#FORM.title", '"Scheda contatto: " + nome + " " + cognome',
                        nome='^.@anagrafica_id.nome', cognome='^.@anagrafica_id.cognome',
                        _if='nome && cognome',_else='"Scheda contatto: nuovo contatto"')
        fb = pane.formbuilder(cols=2,border_spacing='6px',fld_width='15em',lbl_color='teal')
        fb.field('@anagrafica_id.nome')
        fb.field('@anagrafica_id.cognome')
        fb.field('@anagrafica_id.email',
                  validate_email=True,validate_email_error='!!Formato email non corretto')
