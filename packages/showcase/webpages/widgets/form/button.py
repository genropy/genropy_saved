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

class GnrCustomWebPage(object):    
    css_requires='index,button'
    def main(self, root, **kwargs):
        root.dataFormula('font_size','Math.ceil(font)+umf',font='^font',umf='^um_font')
        root.data('icon','icnBaseOk')
        root.data('fontfam','Courier')
        
        root.dataFormula('width_calc','Math.ceil(w)+umw',w='^width',umw='^um_width')
        bc = root.borderContainer(height='100%')
        top = bc.contentPane(height='100px',region='top')
        top.button("Save it",action="FIRE msg='Saving!';",nodeId='cbtn',iconClass='^icon',
                   tooltip='click me',font_size='^font_size',width='^width_calc',font_family='^fontfam')
        center = bc.contentPane(region='center')
        titlepane = center.titlepane(title='Center')
        titlepane.div(height='200px',width='250px')
        center.dataController("""alert(msg);""",msg='^msg')
        self.makeDropDown(center,'Drop')
        self.checkBoxGroup(center,'First,Second,Third,Fourth,Fifth,Sixth')
        
    def makeDropDown(self,pane,label):
        dropdown=pane.dropdownbutton(label)
        dmenu=dropdown.menu()
        dmenu.menuline('Open...',action="FIRE msg='Opening!';")
        dmenu.menuline('Close',action="FIRE msg='Closing!';")
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
        
