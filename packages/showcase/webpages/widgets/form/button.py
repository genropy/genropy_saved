#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
from gnr.web.gnrwsgisite import cache
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):    
    css_requires='index,button'
    def main(self, root, **kwargs):
        root.dataFormula('font_size','Math.ceil(font)+umf',font='^font',umf='^um_font')
        root.data('icon','icnBaseOk')
        root.data('fontfam','Courier')
        
        root.dataFormula('width_calc','Math.ceil(w)+umw',w='^width',umw='^um_width')
        bc = root.borderContainer(height='100%')
        top = bc.contentPane(height='400px',region='top')
        top.button("Save it",action="alert('Saving!')",nodeId='cbtn',iconClass='^icon',
                   tooltip='click me',font_size='^font_size',width='^width_calc',font_family='^fontfam')
        center = bc.contentPane(region='center')
        titlepane = center.titlepane(title='pippo')
        titlepane.div(height='200px',width='250px')
        
        fb = center.formbuilder(cols=3,margin_top='10px')
        fb.button('!!Calcola', action='FIRE ^calcola')
        fb.textbox(value='^risultato')
        fb.dataRpc('risultato','calcola',_fired='^calcola')
        fb.br()
        fb.horizontalslider(lbl='!!width', value = '^width', width='200px', 
                                         minimum=3, maximum=50,intermediateChanges=True)
        fb.numberTextBox(value ='^width',width='5em')
        fb.comboBox(width='5em',values='em,px,%',value='^um_width',default='em')
        fb.horizontalslider(lbl='!!font', value = '^font', width='200px', 
                                         minimum=4, maximum=50,intermediateChanges=True)
        fb.numberTextBox(value = '^font',width='5em')
        
        fb.comboBox(width='5em',values='pt,px',value='^um_font',default='pt')
        fb.filteringSelect(width='15em',value='^icon',colspan=3,lbl='Icon',
                           values='icnBaseAdd:Add,icnBaseCancel:Cancel,icnBaseDelete:Delete,icnBaseOk:Ok')
    
        fb.filteringSelect(width='15em',value='^fontfam',colspan=3,lbl='Font',
                           values='Verdana:Verdana,Courier:Courier,mono:Mono,"Comic Sans MS":Comic')
        
    def makeDropDown(self,fb,label):
        dropdown=fb.dropdownbutton(label)
        dmenu=dropdown.menu()
        dmenu.menuline('Open...',action="alert('Opening...')")
        dmenu.menuline('Close',action="alert('Closing...')")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this',action="alert('Doing this...')")
        submenu.menuline('Or to do that',action="alert('Doing that...')")       
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")
        
    def checkBoxGroup(self,pane,labels,cols=1):
        labels=labels.split(',')
        pane=pane.formbuilder(cols=cols)
        for label in labels:
            pane.checkbox(label) 
        
    @cache.cached_call()
    def rpc_calcola(self):
        for i in range(1000000):
            j=i*2
        return j
