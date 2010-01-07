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

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.data('mytable',self.tableData())
        root.data('bottombar.servertime',remote='serverTime')
        root.data('foo.bar',remote='bar')
        root.data('mydata.disk',remote='diskDirectory',sync=False)
        root.data('mydata.dbstruct',remote='app.dbStructure',sync=False)
        root.data('split',Bag(dict(left_color='green',right_color='smoke')))
	
        split=root.splitContainer(height='100%')
        
# ================= Left Column ===================
        left=split.accordionContainer(sizeShare=25)
        # ----------- value Tree -------------
        tree=left.accordionPane(title='Page Data').tree(storepath='*D',gnrId='dataTree',label="Data Tree",inspect='shift')
        
        # ----------- Page Source Tree -------------
        tree=left.accordionPane(title='Page Source').tree(storepath='*S',gnrId='sourceTree', 
                                inspect='shift',label="Source Tree")
        

        # ----------- Disk Directory Tree -------------
        tree=left.accordionPane(title='Database').tree(storepath='mydata.dbstruct',gnrId='dbTree',
                                                       isTree=False, persist=False, inspect='shift')
        
        # ----------- Disk Directory Tree -------------
        tree=left.accordionPane(title='Disk Directory').tree(storepath='mydata.disk',gnrId='diskTree',inspect='shift',
                                                                persist=False, label="Disk Directory")
        
# ================= Right Column ===================
        rightsplit=split.splitContainer(sizeShare=75,orientation='vertical')
        # ----------- top  -------------
        topright=rightsplit.contentPane(sizeShare=25,background_color='^split.left_color')
        bottomright=rightsplit.contentPane(sizeShare=75,background_color='^split.right_color')
        fb=topright.formbuilder(cols=4)
        fb.textBox(lbl='path',width='40em',value='^test.path',default='mydata.disk.root.data.sites')
        fb.button('getdata',lbl='',action="genro.testdata('^test.path');")
        fb=bottomright.formbuilder(cols=4,datapath='mytable')
        for k in range(5):
            fb.textBox(lbl='Name', value='^.r%i.value' % k)
            fb.button(label='^:r%i.btn' % k,default_label='Button %i'%k)
            fb.checkBox('Do it', value='^.r%i.cb' % k)
            fb.textBox(lbl='Sex', value='^.r%i.sex' % k)

    def tableData(self):
        mytable=Bag()
        mytable['r0.value']='John'
        mytable['r0.btn']='Uh!'
        mytable['r0.cb']=True
        mytable['r0.sex']='M'
        mytable.setItem('r1.value','pierone', _attributes=dict(validate_server='validPiero'))
        mytable.setItem('r1.cb',False)
        mytable['r1.sex']='M'
        mytable['r2.value']='name 2'
        mytable['r2.btn']='Doh!'
        mytable['r2.cb']=True
        mytable['r1.sex']='M'
        mytable['r3.value']='name 3'
        mytable['r4.value']='name 4'
        return mytable
    
    def rpc_serverTime(self):
        return  datetime.datetime.now().strftime('%H:%M:%S')
        
    def rpc_diskDirectory(self):
        return  DirectoryResolver('/usr/local/genro')()
    
    def rpc_bar(self):
        return  'hello _ now is :'+datetime.datetime.now().strftime('%H:%M:%S')
        

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
