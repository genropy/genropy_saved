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
    
    def main(self, root,cols='3', **kwargs):
        root = self.rootLayoutContainer(root)
        fb=root.formbuilder(cols=cols,lblpos='T')

        fb.button("Save it", tooltip='This is a nice help', action="alert('Saving!')", iconClass="confirmIcon")
        fb.button("Load me", action="alert('No way...')").tooltip("Please don't push me...")
        fb.toggleButton('Toggle',iconClass="dijitRadioIcon", value='^tog', gnrId='tog')
        self.makeDropDown(fb,"I'm a dropdownbutton")
        pane=fb.div(border='1px solid silver',padding='5px',lbl='Sport')
        self.checkBoxGroup(pane,"Rugby,Soccer,Baseball,Tennis",cols=1)
        
        pane=fb.div(border='1px solid silver',padding='5px',lbl='Selections')
        self.checkBoxGroup(pane,['%i'%i for i in range (10)],cols=3)
    
        pane=fb.div(border='2px solid red',padding='5px',lbl='Colors',action='function(item,e){alert("color selected:"+item.label)}').formbuilder(cols=2)
        pane.radioButton('red',group='color',label_color='red')
        pane.radioButton('green',group='color',label_color='green',connect_onClick="alert('greeeeeeeen')")
        pane.radioButton('pink',group='color',label_color='pink',action="alert('Pink ?????')")
        pane.radioButton('brown',group='color',label_color='brown')
        
        pane=fb.div(border='2px solid navy',padding='5px',action='function(item,e){alert(item.label)}')
        self.radioGroup(pane,'Jazz,Rock,Punk,Metal','genre',cols=4)
        
        pane=fb.div(border='2px solid navy',padding='5px',action='function(item,e){alert(item.label)}')
        self.radioGroup(pane,['%i'%i for i in range (60)],'sel',cols=6)
        
        u=fb.div(border='5px solid green',padding='5px',action="function(item,e){alert('pressed: '+item.label+' shift:'+e.shiftKey)}").formbuilder(cols=5,lblpos='T')                  
        for k in range (5):
            for j in range(5):
                u.button('%i-%i'%(k,j))
                
    def makeDropDown(self,pane,label):
        dropdown=pane.dropdownbutton(label)
        dmenu=dropdown.menu()
        dmenu.menuline('Open...',action="alert('Opening...')")
        dmenu.menuline('Close',action="alert('Closing...')")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this',action="alert('Doing this...')")
        submenu.menuline('Or to do that',action="alert('Doing that...')")       
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")
        
    def radioGroup(self,pane,labels,group,cols=1):
        if isinstance(labels,basestring):
            labels=labels.split(',')
        pane=pane.formbuilder(cols=cols)
        for label in labels:
            pane.radioButton(label,group=group)
        
    def checkBoxGroup(self,pane,labels,cols=1):
        if isinstance(labels,basestring):
            labels=labels.split(',')
        pane=pane.formbuilder(cols=cols)
        for label in labels:
            pane.checkbox(label) 
            
