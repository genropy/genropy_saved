#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        tc = root.tabContainer(margin='5px',formId='testform',datapath='test')
        self.genroValidation(tc)
        tc2 = tc.tabContainer(title='Dojo Validation')
        self.numberTextBox(tc2)
        self.currencyTextBox(tc2)
        self.dateTextBox(tc2)
        self.timeTextBox(tc2)
        self.textArea(tc2)
        
    def genroValidation(self,tc):
        tc.dataController("""var bag = new gnr.GnrBag();
                            bag.setItem('name','pippo');
                            bag.setItem('notnull',true);
                            bag.setItem('iswarning',true);
                            bag.setItem('len','2:4');
                            bag.setItem('case','upper');
                            bag.setItem('min',10);
                            bag.setItem('max',100);
                            SET test.textBox=bag;""", nodeId='testform_loader')
        tc.dataController("var result = GET test;alert(result.toXml());",nodeId='testform_saver')
        fb=tc.contentPane(title='Genro Validation',datapath='.textBox').formbuilder(cols=2,border_spacing='10px')
        
        tc.dataController('genro.formById("testform").load({sync:true});',_fired='^test.doload')
        fb.button(fire='^test.doload',label='Load')
        fb.button(action='genro.formById("testform").save()',disabled='== !(_changed && _valid)', 
                  _changed='^gnr.forms.testform.changed',_valid='^gnr.forms.testform.valid',label='Save')
                  
        fb.button(action='SET .name="John"',colspan=2,label='Set Value')
        fb.textBox(value='^.len',tooltip='Here you define the size of \'Name(Len)\' textbox. (Format --> 4:7)',lbl="Len")
        fb.textBox(value='^.name4',validate_len='^.len',
                   validate_len_min='alert("too much short!")',validate_len_max='alert("too much long!")',
                   lbl="Name (Len)")
   #    fb.textBox(value='^.case',colspan=2,lbl="Set case validation")
        fb.textBox(value='^.name',validate_len='4:',tooltip='Insert 4 or more characters',
                   validate_onReject='alert("The name "+"\'"+value+"\'"+" is too short")',
                   validate_onAccept='alert("correct lenght of "+"\'"+value+"\'")',lbl="Name")
        fb.textBox(value='^.name',lbl="Name echo") 
        fb.textBox(value='^.nameup',validate_case='upper',lbl="Name up")
        fb.textBox(value='^.namelow',validate_case='lower',lbl="Name low")
        fb.textBox(value='^.namecap',validate_case='capitalize',lbl="Name capitalized")
   #    fb.checkbox(value='^.notnull',lbl="notnull")
   #    fb.textBox(value='^.namenotrim',trim=False,validate_notnull='^.notnull',
   #               validate_notnull_error='required!',lbl="Name notrim notnull")
        fb.textBox(value='^.email',validate_email=True,validate_email_iswarning='^',
                        validate_email_warning='uncorrected e-mail format',lbl="Email")
        fb.textBox(value='^.nameregex',validate_regex='abc',validate_regex_iswarning='^.iswarning',lbl="contains abc")
        fb.checkbox(value='^.iswarning',tooltip='if selected, the error in \'contains abc\' box is a warning, not an error',lbl="iswarning") 
        fb.span('Validation using Callback and Remote function',colspan=2,color='== _email ? "red" : "green"',_email='^.email')
        
        fb.numberTextBox(value='^.min',lbl="Min") 
        fb.numberTextBox(value='^.max',lbl="Max") 
        fb.numberTextBox(value='^.minmax',lbl="between min and max",
                        validate_min='^.min',validate_max='^.max',
                        validate_call="""   
                                       if (value < min){
                                           return 'the value inserted is too small';
                                       } else if (value > max){
                                           return 'the value inserted is too large';
                                       }""")
        fb.textBox(value='^.remote',lbl="remote Name",
                   validate_remote="nameremote",validate_name='^.name', 
                   validate_remote_error='different from name field\'s value inserted')
                    
    def rpc_nameremote(self, value=None, name=None, **kwargs):
        if not value:
            return
        if value.lower() == name.lower():
            result = Bag()
            result['value'] = value.upper()
            return result
        else:
            return 'remote'
            
    def numberTextBox(self,tc):
        fb=tc.contentPane(title='numberTextBox',datapath='.numberTextBox').formbuilder(cols=2,border_spacing='10px')
        fb.numberTextBox(value='^.age',lbl="Age",default=36)
        fb.numberTextBox(value='^.age',lbl="Age echo")
        
    def currencyTextBox(self,tc):
        fb=tc.contentPane(title='currencyTextBox',datapath='.currencyTextBox').formbuilder(cols=2,border_spacing='10px')
        fb.currencyTextBox(value='^.amount',default=1123.34, currency='EUR', locale='it',lbl="Age")
        fb.currencyTextBox(value='^.amount',currency='EUR',locale='it',lbl="Age echo")
        
    def dateTextBox(self,tc):
        fb=tc.contentPane(title='dateTextBox',datapath='.dateTextBox').formbuilder(cols=2,border_spacing='10px')
        fb.dateTextBox(value='^.birthday',lbl='Birthday')
        fb.dateTextBox(value='^.birthday',lbl='Birthday echo')
        
    def timeTextBox(self,tc):
        fb=tc.contentPane(title='timeTextBox',datapath='.timeTextBox').formbuilder(cols=2,border_spacing='10px')
        fb.timeTextBox(value='^.meetingAt',lbl='Meeting Time')
        fb.timeTextBox(value='^.meetingAt',lbl='Meeting Time echo')
        
    def textArea(self,tc):
        fb=tc.contentPane(title='textArea',datapath='.textArea').formbuilder(cols=2,border_spacing='10px')
        fb.textArea(value='^.remarks',lbl='Remarks')
        fb.textArea(value='^.remarks',lbl='Remarks echo')