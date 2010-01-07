#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os


class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        split = root.splitContainer(height='100%')
        tree = split.contentPane(sizeShare='30',background_color='smoke').tree(storepath='*D',
                                             inspect='shift',label="Data")
        tc = split.tabContainer(sizeShare='70',height='100%',margin='5px', datapath='test')
        self.textBox(tc)
        if False:
            self.numberTextBox(tc)
            self.currencyTextBox(tc)
            self.dateTextBox(tc)
            self.timeTextBox(tc)
            self.validationTextBox(tc)
            self.textArea(tc)
            #self.inLineEditBox(tc)
            self.buttons(tc)
        
    def textBox(self,tc):
        fb=tc.contentPane(title='Text', datapath='.textBox').formbuilder(cols=2,cellspacing='10')
        fb.TextBox(lbl="In Attribute",value='=.inattr?name',default='Pino')
        fb.TextBox(lbl="In Attribute Echo",value='^.inattr?name')

        fb.TextBox(lbl="Name",default='John Brown',value='=.name')
        fb.TextBox(lbl="Name echo",value='^.name')
        
        fb.TextBox(lbl="Name up",value='^.nameup', validate_case='upper')
        fb.TextBox(lbl="Name low",value='^.namelow', validate_case='lower')
        fb.TextBox(lbl="Name capitalize",value='^.namecap', validate_case='capitalize', invalidMessage="Hai inserito minuscolo !!!!", promptMessage='tutto maiuscolo')
        fb.TextBox(lbl="Name 4",value='^.name4', validate_len=':4', required=True)
        fb.TextBox(lbl="Name notrim",value='^.namenotrim', trim=False)
        
        fb.TextBox(lbl="Name regex", value='^.nameregex', validate_regex='\D*', invalidMessage="Hai inserito numeri !!!!", promptMessage='Non inserire numeri')
        
        if False:
            fb.TextBox(lbl="Name call", value='^.namecall', validate_call="""
            if(this.textbox.value.indexOf('z') >=0){
                this.invalidMessage = 'Nooo Z !!!';
                return false;
            } else if(this.textbox.value.indexOf('x') >=0){
                this.invalidMessage = 'Nooo X !!!';
                return false;
            }
            return true;
            """, promptMessage='Non iniziare per z')
        
        fb.TextBox(lbl="Remote", value='^.remote', validate_remote="checkZ", remote_noletters='xyz')
        
        fb.TextBox(lbl="Email", value='^.email', validate_email=True)

        #fb.button('salva', fire="save_fire")
        #fb.button('salva2', disabled='^save_error')
        #fb.button('salva3', fire='save_fire3')
        #fb.dataScript('save_error', """return genro.dataValidate(dbag, btn);""", dbag='^test.textBox', btn='^save_fire')
        
        #fb.dataScript('save3', "alert('salva');", dbag='^test.textBox', btn='^save_fire3', 
        #             _if='(btn && (genro.dataValidate(dbag)))', _else='if(btn){genro.focusOnError(dbag)};')


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
       # fb.DateTextBox(lbl='Birthday',default='1980-03-30::D',value='^.birthday')
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
        
        
