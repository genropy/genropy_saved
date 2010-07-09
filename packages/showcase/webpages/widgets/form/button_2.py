#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    css_requires='index'
    def main(self, root, **kwargs):
        root.data('icon','icnBaseOk')
        root.data('fontfam','Courier')
        root.dataFormula('width_calc','w + umw',w='^width',umw='^um_width')
        root.dataFormula('font_size','font + umf',font='^font',umf='^um_font')
        
        bc = root.borderContainer()
        top = bc.contentPane(region='top',background_color='orange')
        fb = top.formbuilder(cols=4, padding='10px')
        fb.horizontalslider(lbl='!!width',value='^width',width='200px',discreteValues='48',
                            minimum=3,maximum=50,intermediateChanges=True, default=8)
        fb.numberTextBox(value='^width', width='4em')
        fb.comboBox(width='5em',value='^um_width',values='em,px,%',default='em')
        fb.br()
        
        fb.horizontalslider(lbl='!!font',value='^font',width='200px',discreteValues='47',
                            minimum=4,maximum=50,intermediateChanges=True, default=11)
        fb.numberTextBox(value='^font',width='4em')
        fb.comboBox(width='5em',values='pt,px',value='^um_font',default='pt')
        fb.filteringSelect(width='8em',value='^fontfam',lbl='Font',
                           values='Verdana:Verdana,Courier:Courier,mono:Mono,"Comic Sans MS":Comic')
                           
        fb.filteringSelect(width='5em',value='^icon',colspan=4,lbl='icon',
                           values='icnBaseAdd:Add,icnBaseCancel:Cancel,icnBaseDelete:Delete,icnBaseOk:Ok')
                           
        center = bc.contentPane(height='200px',region='center')
        center.button("Save it", action="alert('Saving!')", iconClass='^icon', tooltip='click me',
                       font_size='^font_size', width='^width_calc', font_family='^fontfam')