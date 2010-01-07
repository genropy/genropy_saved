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

from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        #root = self.rootLayoutContainer(root)
        root.data('mydata.disk',remote='diskDirectory',sync=False)
        #tree=root.tree(storepath='mydata.disk',gnrId='diskTree',label="Disk Directory")
        root.textBox(lbl='path',width='40em',value='test.path',default='mydata.disk.data.sites')
        root.button('getdata',lbl='',action="genro.testdata('@test.path');")
        
    def rpc_diskDirectory(self):
        return  DirectoryResolver('/usr/local/genro')()
        
