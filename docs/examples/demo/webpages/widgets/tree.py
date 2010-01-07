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
        split=root.splitContainer(height='100%')
        tree=split.contentPane(sizeShare='30',background_color='smoke').tree(storepath='mytable',gnrId='mytableTree',
                                         inspect='shift',selected='mytree.selection',label="mytable Tree")
        fb=split.contentPane(sizeShare='70').formbuilder(cols=4,value='mytable')

       #for k in range(1):
       #    fb.textBox(lbl='Value', value='.r%i.value' % k)
       #    fb.button(lbl='Button', label='^.r%i.btn' % k)
       #    fb.checkBox(lbl='Do it', value='.r%i.cb' % k)
       #    fb.textBox(lbl='sex', value='.r%i.sex' % k)

    def tableData(self):
        mytable=Bag()
        mytable['r0.value'] = 'John'
        mytable['r0.btn'] = 'Button 0'
        mytable['r0.cb'] = True
        mytable['r0.sex'] = 'M'
        mytable.setItem('r1.value','pierone', _attributes=dict(validate_server='validPiero'))
        mytable.setItem('r1.cb',False)
        mytable['r1.sex'] = 'M'
        mytable['r2.value'] = 'name 2'
        mytable['r2.btn'] = 'Button 2'
        mytable['r2.cb'] = True
        mytable['r1.sex'] = 'M'
        mytable['r3.value'] = 'name 3'
        mytable['r4.value'] = 'name 4'
        return mytable

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
