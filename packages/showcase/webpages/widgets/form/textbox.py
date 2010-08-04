#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        #   dateTextBox - DEFAULT parameters:
        #       popup=True      --> show calendar dialog
        
        fb = root.formbuilder(datapath='form',cols=2)
        root.dataController("console.log('load record '+code)",code="^code")
        fb.textBox(value='^.r0.name',lbl='Name')
        fb.textBox(value='^.r0.surname',lbl='Surname')
        fb.div('date format: GG/MM/AAAA')
        fb.dateTextBox(value='^.r0.birthday',lbl='Birthday')
        fb.numberTextBox(value='^.r0.age',lbl='Age')
        fb.dateTextBox(value='^.r0.date',popup=False,lbl='Date (no popup)')
        
        root.div('- In magic box the sixth character is written onto the box with \"Text\" label')
        fb.textbox(value='^code',lbl='Magic box',connect_onkeyup="""if($1.target.value.length==5){
                                                        var form = $1.target.form;
                                                        var pos = dojo.indexOf(form.elements,$1.target)
                                                        form.elements[pos+1].focus();
                                                    }""")
                                                    
        fb.textBox(value='^.r0.text',width='5em',lbl='Text')