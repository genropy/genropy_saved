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

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        data=Bag()
        data['r0.name']='John'
        data['r0.age']=26
        data['r1.name']='Frank'
        data['r1.age']=33
        #root.data('mydata',data)
        split = root.splitContainer(height='100%')
        tree = split.contentPane(sizeShare='30',background_color='smoke').tree(storepath='mydata',gnrId='mydataTree',
                                          inspect='shift',label="data")
        #tree = split.contentPane(sizeShare='30',background_color='smoke').tree(storepath='mydata',gnrId='mydataTree',
                                                                          #inspect='shift',label="data")
        split = split.splitContainer(sizeShare='70',height='100%',orientation='vertical')
        pane=split.contentPane(sizeShare='30')
        fb=pane.formbuilder(cols=2,cellspacing='4',datapath='mydata',margin='2em')
        fb.data(data)
        fb.textBox(lbl='Name', value='^.r0.name' )
        fb.numberTextBox(lbl='Age', value='^.r0.age')
        fb.textBox(lbl='Name2', value='^.r0.name' )
        fb.numberTextBox(lbl='Age2', value='^.r0.age' )
        fb.input(lbl='Name3', value='^.r0.name' )
        fb.span(lbl='Name4', value='^.r0.name', border='1px solid red',padding='1px',mask='the name is %s')
        fb.button( label='^.r0.name', mask='click on %s')
        fb.button('doit', action="genro.nodeById('mySpecialNode').updateContent({'pluto':'^mydata.r0.name'})")
        fb.checkBox(gnrId='cb1',lbl='cb1', value='^.r0.cb' ,default=True)
        fb.toggleButton(gnrId='tb1',lbl='tb1 (echo cb1)', label ='Xxxxx',iconClass="dijitRadioIcon",value='^.r0.cb' )
        fb.radioButton(gnrId='rb1',lbl='rb1', value='^.r0.cb' )
        
        fb.checkBox(gnrId='cb2',lbl='cb2', value='^.r0.tb' )
        fb.toggleButton(gnrId='tb2',lbl='tb2 (echo cb2)', label ='Xxxxx',iconClass="dijitRadioIcon", value='^.r0.tb' )
        fb.radioButton(gnrId='rb2',lbl='rb2', value='^.r0.cb' )
        
        
        gg = split.contentPane(sizeShare='70',nodeId='mySpecialNode').remote('content1', pippo=34, refresh='^mydata.r0.name')

    def rpc_content1(self, **kwargs):
        pane = self.newSourceRoot()
        t = datetime.datetime.now().strftime('%H:%M:%S')
        pane.h1(t)
        fb = pane.formbuilder(cols=2)
        fb.button('next', action="alert('hhhhh')")
        fb.div("received:" + str(kwargs))
        return pane
    
