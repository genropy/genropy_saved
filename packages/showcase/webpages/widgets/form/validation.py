#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" GnrDojo Hello World """
import os

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        tc = root.tabContainer(height='100%',margin='5px',formId='testform', datapath='test')
        self.genroValidation(tc)
        tc2 = tc.tabContainer(title='Dojo Validation')
        self.numberTextBox(tc2)
        self.currencyTextBox(tc2)
        self.dateTextBox(tc2)
        self.timeTextBox(tc2)
        self.validationTextBox(tc2)
        self.textArea(tc2)
        #self.buttons(tc2)
        
    def genroValidation(self,tc):
        tc.dataController("""var b = new gnr.GnrBag();
                             b.setItem('name','pippo');
                             b.setItem('notnull', true);
                             b.setItem('iswarning', true);
                             b.setItem('len', '2:4');
                             b.setItem('case', 'upper');
                             b.setItem('min', 10);
                             b.setItem('max', 100);
                             SET test.textBox=b;""", nodeId='testform_loader')
        tc.dataController("var result = GET test;alert(result.toXml());", nodeId='testform_saver')
        fb=tc.contentPane(title='Genro Validation', datapath='.textBox').formbuilder(cols=2,cellspacing='10')
        
        tc.dataController('genro.formById("testform").load(true);', _fired='^doload',
                           _onstart='^gnr.onStart')
        fb.button('Load', fire='doload')
        fb.button('Save', action='genro.formById("testform").save()',
                  disabled='== !(_changed && _valid)', 
                  _changed='^gnr.forms.testform.changed', 
                  _valid='^gnr.forms.testform.valid')
        fb.button('Set Value', action='SET .name="giangino"')
        
        fb.TextBox(lbl="Len",value='^.len') 
        fb.TextBox(lbl="Set case validation",value='^.case') 
        
        fb.TextBox(lbl="Name", value='^.name', validate_len='4:', nodeId='name', 
                                        validate_onReject='alert("troppo corto: "+value)',
                                        validate_onAccept='alert("giusto: "+value)')
        fb.TextBox(lbl="Name echo",value='^.name') 
        fb.TextBox(lbl="Name up",value='^.nameup', validate_case='upper')
        fb.TextBox(lbl="Name low",value='^.namelow', validate_case='lower')
        fb.TextBox(lbl="Name case",value='^.namecap', validate_case='^.case')
        fb.TextBox(lbl="Name 4",value='^.name4', validate_len='^.len', validate_len_max='much too long!', validate_len_min='too short !')
        
        fb.checkbox(lbl="notnull",value='^.notnull') 
        fb.TextBox(lbl="Name notrim notnull",value='^.namenotrim', trim=False, 
                   validate_notnull='^.notnull', validate_notnull_error='required!')
        fb.TextBox(lbl="Email", value='^.email', validate_email=True, validate_email_iswarning='^', 
                        validate_email_warning='Email non corretta')
        
        fb.checkbox(lbl="iswarning",value='^.iswarning') 
        fb.TextBox(lbl="contains abc", value='^.nameregex', colspan=2, 
                        validate_regex='abc', 
                        validate_regex_iswarning='^.iswarning', 
                        validate_regex_error='MUST contain "abc"',
                        validate_regex_warning='SHOULD contain "abc"')
        fb.span('Validation using Callback and Remote function',colspan=2, color='== _email ? "red" : "green"', _email='^.email')
        
        fb.NumberTextBox(lbl="Min",value='^.min') 
        fb.NumberTextBox(lbl="Max",value='^.max') 
        
        fb.NumberTextBox(lbl="between min and max", value='^.namecall', 
                        validate_max='^.max', validate_min='^.min',
                        validate_call="""   
                                       if (value < min){
                                           return 'min';
                                       } else if (value > max){
                                           return 'max';
                                       }""",
                    validate_call_min='!! small!', validate_call_max='!!Big!')
        
        fb.TextBox(lbl="remote Name up", value='^.nameremote', 
                    validate_remote="nameremote", validate_name='^.name', 
                    validate_remote_error='different from the name field value entered')
        
    def rpc_nameremote(self, value=None, name=None, **kwargs):
        if not value:
            return
        if value.lower() == name.lower():
            result = Bag()
            result['value'] = value.upper()
            return result
        else:
            return 'nameremote'
        
    def rpc_checkZ(self, value, noletters, **kwargs):
        for letter in noletters:
            if letter in value:
                return False
        return True
        
    def numberTextBox(self,tc):
        fb=tc.contentPane(title='Number',datapath='.numberTextBox').formbuilder(cols=2,cellspacing='10')
        fb.NumberTextBox(lbl="Age",default=36,value='^.age')
        fb.NumberTextBox(lbl="Age echo",value='^.age')
        
    def currencyTextBox(self,tc):
        fb=tc.contentPane(title='CurrencyTextBox',datapath='.currencyTextBox').formbuilder(cols=2,cellspacing='10')
        fb.CurrencyTextBox(lbl="Amount",default=1123.34, currency='EUR', locale='it',value='^.amount')
        fb.CurrencyTextBox(lbl="Amount echo", currency='EUR', locale='it',value='^.amount')
        
    def dateTextBox(self,tc):
        fb=tc.contentPane(title='DateTextBox',datapath='.dateTextBox').formbuilder(cols=2,cellspacing='10')
        fb.DateTextBox(lbl='Birthday echo',value='^.birthday')
        
    def timeTextBox(self,tc):
        fb=tc.contentPane(title='TimeTextBox',datapath='.timeTextBox').formbuilder(cols=2,cellspacing='10')
        fb.TimeTextBox(lbl='Meeting Time',value='^.meetingAt')
        fb.TimeTextBox(lbl='Meeting Time echo',value='^.meetingAt')
        
    def validationTextBox(self,tc):
        fb=tc.contentPane(title='ValidationTextBox',datapath='.validationTextBox').formbuilder(cols=2,cellspacing='10')
        fb.ValidationTextBox(lbl='Email',default='john.brown@somewhere.com',value='^.email')
        fb.ValidationTextBox(lbl='Email echo',value='^.email')
        
    def textArea(self,tc):
        fb=tc.contentPane(title='TextArea',datapath='.textArea').formbuilder(cols=2,cellspacing='10')
        fb.textArea(lbl='Remarks',value='^.remarks')
        fb.textArea(lbl='Remarks echo',value='^.remarks')
        
    def inLineEditBox(self,tc):
        fb=tc.contentPane(title='InLineEditBox',datapath='.inLineEditBox').formbuilder(cols=2,cellspacing='10')
        fb.inlineEditBox(lbl='EditThis',onChange="function(x){alert('xxxx')}::JS").div(value='^.ed1')
        fb.inlineEditBox(lbl='EditThat',onChange="function(x){alert('xxxx')}::JS",
                                   autoSave=False,buttonSave='OK',buttonCance='Cancel',
                                   editor="dijit.form.DateTextBox").div(value='^.ed2')
        
    def buttons(self,tc):
        fb=tc.contentPane(title='Buttons',datapath='.buttons').formbuilder(cols=2,cellspacing='10')
        fb.button("Load me", action="alert('No way...')",fire='^.button1')
        fb.toggleButton('Toggle',iconClass="dijitRadioIcon",value='^.toggle1')
        fb.checkBoxGroup("Rugby,Soccer,Baseball,Tennis",cols=1,border='1px solid silver',padding='5px',value='^.cb')
        fb.radioGroup('Jazz,Rock,Punk,Metal','genre',cols=4,border='1px solid red',padding='5px',value='^.rb')