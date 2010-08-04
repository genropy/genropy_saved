#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('icon','icnBaseOk')
        root.data('fontType','Courier')
        root.dataController("""alert(msg);""",msg='^msg')
        bc = root.borderContainer()
        fb = bc.formbuilder(cols=2)
        fb.div('button type')
        fb.button(action="FIRE msg='Saving!';",iconClass='^icon',
                   tooltip='click me!',font_family='^fontType',label='Save it')
        fb.div('checkbox type')
        self.checkBoxGroup(fb,'First,Second,Third,Fourth,Fifth,Sixth')
        self.makeDropDown(fb,'Menù')
        
    def makeDropDown(self,pane,label):
        pane.div('dropdownbutton type')
        ddb=pane.dropdownbutton(label)
        dmenu=ddb.menu()
        dmenu.menuline('Open...', action="FIRE msg='Opening!';")
        dmenu.menuline('Close', action="FIRE msg='Closing!';")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this', action="alert('Doing this...')")
        submenu.menuline('Or to do that', action="alert('Doing that...')")       
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")
        
    def checkBoxGroup(self,pane,labels,columns=1):
        labels=labels.split(',')
        pane=pane.formbuilder(cols=columns)
        for label in labels:
            pane.checkbox(label)