# -*- coding: UTF-8 -*-

# th_staff.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@anagrafica_id.nome', name='!!Name', width='8%')
        r.fieldcell('@anagrafica_id.cognome', name='!!Surname', width='8%')
        r.fieldcell('@anagrafica_id.email', name='!!Personal email', width='14%')
        r.fieldcell('@anagrafica_id.telefono', name='!!Personal phone', width='8%')
        r.fieldcell('@anagrafica_id.codice_fiscale', name='!!Personal tax code', width='10%')
        r.fieldcell('@anagrafica_id.partita_iva', name='!!Personal VAT', width='7%')
        r.fieldcell('@anagrafica_id.fax', name='!!Personal fax', width='7%')
        r.fieldcell('interno', width='6%')
        r.fieldcell('ruolo', width='7%')
        r.fieldcell('@anagrafica_id.note', name='!!Personal notes', width='9%')
        
    def th_order(self):
        return '@anagrafica_id.cognome'
        
    def th_query(self):
        return dict(column='@anagrafica_id.cognome', op='contains', val='', runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pass
        #pane = form.record
        #fb = pane.formbuilder(cols=2,border_spacing='6px',fld_width='15em',lbl_color='teal')
        #fb.field('@anagrafica_id.nome')
        #fb.field('@anagrafica_id.cognome')
        #fb.field('@anagrafica_id.email',
        #          validate_email=True,validate_email_error='!!Formato email non corretto')
        #fb.field('@anagrafica_id.telefono', ghost='esempio: 347/1212123')
        #fb.field('@anagrafica_id.codice_fiscale',
        #          validate_case='u')
        #fb.field('@anagrafica_id.partita_iva')
        #fb.field('@anagrafica_id.fax')
        #fb.field('interno', ghost='esempio: 202')
        #fb.field('@anagrafica_id.note', tag='textarea', colspan=2, width='100%')
        #fb.field('ruolo',tag='combobox', lbl='Ruolo nell\'azienda',
        #          values='dipendente, libero professionista, manager')
        
#class NisoView(BaseComponent):
#    def th_struct(self,struct):
#        r = struct.view().rows()
#        r.fieldcell('@anagrafica_id.nome', width='8%')
#        r.fieldcell('@anagrafica_id.cognome', width='8%')
#        
#    def th_order(self):
#        return '@anagrafica_id.cognome'
#        
#    def th_query(self):
#        return dict(column='@anagrafica_id.nome', op='contains', val='')