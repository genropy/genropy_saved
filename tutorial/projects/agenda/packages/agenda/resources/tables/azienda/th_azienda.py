# -*- coding: UTF-8 -*-

# th_azienda.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('@anagrafica_id.ragione_sociale', name='!!Name', width='18%')
        r.fieldcell('@anagrafica_id.telefono', name='!!Phone', width='6%')
        r.fieldcell('@anagrafica_id.email', name='!!E-mail', width='12%')
        r.fieldcell('tipologia', width='6%')
        r.fieldcell('@anagrafica_id.indirizzo', name='!!Address', width='12%')
        r.fieldcell('@anagrafica_id.cap', name='!!Postcode', width='4%')
        r.fieldcell('@anagrafica_id.localita', name='!!Location', width='7%')
        r.fieldcell('@anagrafica_id.partita_iva', name='!!VAT', width='7%')
        r.fieldcell('@anagrafica_id.fax', name='!!Fax', width='6%')
        r.fieldcell('@anagrafica_id.www', name='!!Web Site', width='13%')
        r.fieldcell('@anagrafica_id.note', name='!!Notes', width='9%')
        
    def th_order(self):
        return '@anagrafica_id.ragione_sociale'
        
    def th_query(self):
        return dict(column='@anagrafica_id.ragione_sociale', op='contains', val='', runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2,border_spacing='6px',lbl_width='6em',
                              fld_width='15em',width='40em',lbl_color='teal')
        fb.field('@anagrafica_id.ragione_sociale',colspan=2,
                  lbl='!!Name',width='100%',
                  validate_notnull=True,
                  validate_notnull_error='!!Required field')
        fb.field('@anagrafica_id.email',
                  lbl='!!Email',
                  validate_email=True,
                  validate_email_error='!!Uncorrect email format',colspan=2)
        fb.field('@anagrafica_id.telefono',lbl='!!Phone')
        fb.field('@anagrafica_id.fax',lbl='!!Fax')
        fb.field('@anagrafica_id.indirizzo',lbl='!!Address',
                  validate_case='capitalize',tag='simpletextarea',lbl_vertical_align='top',width='100%',colspan=2)
        fb.field('@anagrafica_id.cap',lbl='!!Postcode')
        fb.field('@anagrafica_id.localita',lbl='!!Location')
        fb.field('@anagrafica_id.partita_iva',lbl='!!VAT')
        fb.field('tipologia',lbl='!!Type',tag='combobox',values='customer, supplier')
        fb.field('@anagrafica_id.www',lbl='!!Web site',colspan=2)
        fb.field('@anagrafica_id.note',lbl='!!Notes',
                  tag='simpletextarea',lbl_vertical_align='top',width='100%',colspan='2')
                  