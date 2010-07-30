#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, rootBC, **kwargs):
        fb=rootBC.contentPane(title='Buttons',datapath='buttons').formbuilder(cols=3,border_spacing='10px')
        
        fb.checkbox('checkbox',value='^.checkbox')
        fb.toggleButton('Toggle',iconClass="dijitRadioIcon",value='^.toggle1')
        fb.toggleButton(iconClass="dijitRadioIcon",value='^.toggle2')
        
        fb.radiobutton('Jazz',value='^.radio.jazz',group='genre1')
        fb.radiobutton('Rock',value='^.radio.rock',group='genre1')
        fb.radiobutton('Blues',value='^.radio.blues',group='genre1')
        
        fb.div('Sex')
        fb.radiobutton('M',value='^.sex.male',group='genre2')
        fb.radiobutton('F',value='^.sex.female',group='genre2')