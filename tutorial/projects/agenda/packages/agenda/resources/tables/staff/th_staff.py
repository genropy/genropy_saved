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
        
class FormValidations(BaseComponent):
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2,fld_width='15em',lbl_color='teal',datapath='.textbox')
        fb.div('validations on textbox',colspan=2)
        fb.textbox(value='^.validate_case_c',lbl='validate_case=\"c\"',validate_case='c',
                   validate_notnull=True,validate_notnull_error='!!Required field')
        fb.textbox(value='^.validate_case_u',lbl='validate_case=\"u\"',validate_case='u')
        fb.textbox(value='^.validate_case_l',lbl='validate_case=\"l\"',validate_case='l')
        fb.textbox(value='^.validate_case_t',lbl='validate_case=\"t\"',validate_case='t')
        fb.textbox(value='^.validate_email_1',lbl='validate_email + error',validate_email=True,
                   validate_email_error='!!Uncorrect email format')
        fb.textBox(value='^.validate_email_2',lbl="validate_email + onAccept",
                   validate_email=True,validate_onAccept='alert("Correct email format")')
        # LA VALIDATE ONACCEPT PARTE CON IL LOADING DELLA FORM!!! SBAGLIATO!!
        fb.textbox(value='^.validate_len_:10', lbl='validate_len=\":10\"',
                    validate_len=':10',
                    validate_len_error="""Wrong lenght: the field accept a string
                                          of maximum 10 characters""")
        fb.textBox(value='^.validate_len_5',lbl='validate_len=\'5\'',validate_len='5')
        fb.textBox(value='^.validate_len_6:',lbl='validate_len=\'6:\'',validate_len='6:',
                   validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
        fb.textbox(value='^.validate_notnull',lbl='validate_notnull',validate_notnull=True)
        fb.textbox(value='^.validate_regex',lbl='validate_regex (not \".\")',validate_regex='!\.',
                   validate_regex_error='!!Don\'t write any \".\" char in the expression')
        fb.numberTextbox(value='^.validate_call', lbl="smaller than 5",
                         validate_call="""if (value < 5){return true;}
                                          else {alert('Wrong number!!');
                                                return false;}""")
                         
        fb = pane.formbuilder(dbtable='agenda.validazione',cols=2,fld_width='15em',lbl_color='teal',datapath='.field')
        fb.div('validations on field',colspan=2)
        fb.field('validate_case_c',validate_case='c')
        fb.field('validate_case_u',validate_case='u')
        fb.field('validate_case_l',validate_case='l')
        fb.field('validate_case_t',validate_case='t')
        fb.field('validate_email_1',validate_case='t',validate_email=True,
                  validate_email_error='!!Uncorrect email format')
        fb.field('validate_email_2',validate_case='t',
                  validate_email=True,validate_onAccept='alert("Correct email format")')
        # LA VALIDATE ONACCEPT PARTE CON IL LOADING DELLA FORM!!! SBAGLIATO!!
        fb.field('validate_len_1', lbl='validate_len=\":10\"',
                  validate_len=':10',
                  validate_len_error="""Wrong lenght: the field accept a string
                                        of maximum 10 characters""")
        fb.field('validate_len_2',lbl='validate_len=\'5\'',validate_len='5')
        fb.field('validate_len_3',lbl='validate_len=\'6:\'',validate_len='6:',
                  validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
        fb.field('validate_notnull',lbl='validate_notnull',validate_notnull=True)
        fb.field('validate_regex',lbl='validate_regex (not \".\")',validate_regex='!\.',
                  validate_regex_error='!!Don\'t write any \".\" char in the expression')
        fb.field('validate_call',lbl="greater than 5",
                  validate_call="""if (value > 5){return true;}
                                   else {alert('Wrong number!!');
                                         return false;}""")
        
        # ADD:
        # validate_empty
        # validate_exist
        # validate_gridnodup
        # validate_max
        # validate_min
        # validate_nodup
        # validate_remote
        
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