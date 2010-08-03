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
   #    tc.dataController("""var bag = new gnr.GnrBag();
   #                         bag.setItem('name','pippo');
   #                         bag.setItem('notnull',true);
   #                         bag.setItem('iswarning',true);
   #                         bag.setItem('len','2:4');
   #                         bag.setItem('case','upper');
   #                         bag.setItem('min',10);
   #                         bag.setItem('max',100);
   #                         SET test.textBox=bag;""", nodeId='testform_loader')
   #    tc.dataController("var result = GET test;alert(result.toXml());", nodeId='testform_saver')
        fb=tc.contentPane(title='Genro Validation',datapath='.textBox').formbuilder(cols=2,border_spacing='10px')
   #    
   #    tc.dataController('genro.formById("testform").load();',_fired='^test.doload')
   #    fb.button('Load',fire='^test.doload')
   #    
   #    fb.button('Save',action='genro.formById("testform").save()',disabled='== !(_changed && _valid)', 
   #              _changed='^gnr.forms.testform.changed',_valid='^gnr.forms.testform.valid')
        fb.button('Set Value',action='SET .name="John"',colspan=2)
        fb.textBox(lbl="Len",value='^.len',tooltip='Here you define the size of \'Name(Len)\' textbox. (Format --> 4:7)')
        fb.textBox(lbl="Name (Len)",value='^.name4',validate_len='^.len',
                   validate_len_min='alert("too much short!")',validate_len_max='alert("too much long!")')
   #    fb.textBox(lbl="Set case validation",value='^.case',colspan=2)
        fb.textBox(lbl="Name",value='^.name',validate_len='4:',tooltip='Insert 4 or more characters',
                   validate_onReject='alert("The name "+"\'"+value+"\'"+" is too short")',
                   validate_onAccept='alert("correct lenght of "+"\'"+value+"\'")')
        fb.textBox(lbl="Name echo",value='^.name') 
        fb.textBox(lbl="Name up",value='^.nameup',validate_case='upper')
        fb.textBox(lbl="Name low",value='^.namelow',validate_case='lower')
        fb.textBox(lbl="Name capitalized",value='^.namecap',validate_case='capitalize')
   #    fb.checkbox(lbl="notnull",value='^.notnull')
   #    fb.textBox(lbl="Name notrim notnull",value='^.namenotrim',trim=False,
   #               validate_notnull='^.notnull',validate_notnull_error='required!')
        fb.textBox(lbl="Email",value='^.email',validate_email=True,validate_email_iswarning='^',
                        validate_email_warning='uncorrected e-mail format')
        fb.textBox(lbl="contains abc",value='^.nameregex',validate_regex='abc',validate_regex_iswarning='^.iswarning')
        fb.checkbox(lbl="iswarning",value='^.iswarning',tooltip='if selected, the error in \'contains abc\' box is a warning, not an error') 
        fb.span('Validation using Callback and Remote function',colspan=2,color='== _email ? "red" : "green"',_email='^.email')
        
        fb.numberTextBox(lbl="Min",value='^.min') 
        fb.numberTextBox(lbl="Max",value='^.max') 
        fb.numberTextBox(lbl="between min and max",value='^.minmax', 
                        validate_min='^.min',validate_max='^.max',
                        validate_call="""   
                                       if (value < min){
                                           return 'the value inserted is too small';
                                       } else if (value > max){
                                           return 'the value inserted is too large';
                                       }""")
        fb.textBox(lbl="remote Name",value='^.remote', 
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
        fb.numberTextBox(lbl="Age",default=36,value='^.age')
        fb.numberTextBox(lbl="Age echo",value='^.age')
        
    def currencyTextBox(self,tc):
        fb=tc.contentPane(title='currencyTextBox',datapath='.currencyTextBox').formbuilder(cols=2,border_spacing='10px')
        fb.currencyTextBox(lbl="Age",default=1123.34, currency='EUR', locale='it',value='^.amount')
        fb.currencyTextBox(lbl="Age echo", currency='EUR', locale='it',value='^.amount')
        
    def dateTextBox(self,tc):
        fb=tc.contentPane(title='dateTextBox',datapath='.dateTextBox').formbuilder(cols=2,border_spacing='10px')
        fb.dateTextBox(lbl='Birthday',value='^.birthday')
        fb.dateTextBox(lbl='Birthday echo',value='^.birthday')
        
    def timeTextBox(self,tc):
        fb=tc.contentPane(title='timeTextBox',datapath='.timeTextBox').formbuilder(cols=2,border_spacing='10px')
        fb.timeTextBox(lbl='Meeting Time',value='^.meetingAt')
        fb.timeTextBox(lbl='Meeting Time echo',value='^.meetingAt')
        
    def textArea(self,tc):
        fb=tc.contentPane(title='textArea',datapath='.textArea').formbuilder(cols=2,border_spacing='10px')
        fb.textArea(lbl='Remarks',value='^.remarks')
        fb.textArea(lbl='Remarks echo',value='^.remarks')