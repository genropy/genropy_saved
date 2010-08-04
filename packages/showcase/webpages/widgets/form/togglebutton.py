#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, rootBC, **kwargs):
        fb=rootBC.contentPane(title='Buttons',datapath='buttons').formbuilder(cols=3,border_spacing='10px')
        
        fb.checkbox(value='^.checkbox',label='checkbox')
        fb.toggleButton(value='^.toggle1',iconClass="dijitRadioIcon",label='Toggle')
        fb.toggleButton(value='^.toggle2',iconClass="dijitRadioIcon")
        
        fb.radiobutton(value='^.radio.jazz',group='genre1',label='Jazz')
        fb.radiobutton(value='^.radio.rock',group='genre1',label='Rock')
        fb.radiobutton(value='^.radio.blues',group='genre1',label='Blues')
        
        fb.div('Sex')
        fb.radiobutton(value='^.sex.male',group='genre2',label='M')
        fb.radiobutton(value='^.sex.female',group='genre2',label='F')