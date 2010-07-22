#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        #   horizontalSlider - DEFAULT parameters:
        #       minimum=0, maximum=100, intermediateChanges=False
        
        fb=root.formbuilder(cols=4)
        fb.data('icon','icnBaseOk')
        fb.data('fontfam','Courier')
        fb.dataFormula('width_calc','w+umw',w='^width',umw='^um_width')
        fb.dataFormula('font_size','font+umf',font='^font',umf='^um_font')
        
        fb.horizontalSlider(lbl='!!Width button',value='^width',width='200px',
                            default=8,minimum=3,intermediateChanges=True)
        fb.numberTextBox(value='^width',width='4em')
        fb.comboBox(width='5em',value='^um_width',values='em,px,%',default='em')
        fb.br()
        
        fb.horizontalslider(lbl='!!Width font',value='^font',width='200px',default=11,
                            minimum=4,discreteValues=97,intermediateChanges=True)
        fb.numberTextBox(value='^font',width='4em')
        fb.comboBox(width='5em',values='pt,px',value='^um_font',default='pt')
        fb.filteringSelect(width='8em',value='^fontfam',lbl='Font',
                           values='Verdana:Verdana,Courier:Courier,mono:Mono,"Comic Sans MS":Comic')
        fb.filteringSelect(width='5em',value='^icon',colspan=4,lbl='icon',
                           values='icnBaseAdd:Add,icnBaseCancel:Cancel,icnBaseDelete:Delete,icnBaseOk:Ok')                  
        root.button("Save it",action="alert('Saving!')",iconClass='^icon',tooltip='click me',
                    font_size='^font_size',width='^width_calc',font_family='^fontfam')