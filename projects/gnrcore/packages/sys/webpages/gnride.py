 # -*- coding: utf-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.app.gnrconfig import getGenroRoot
import os
import sys

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/gnride/gnride'
    pdb_ignore=True
    def main(self,root,**kwargs):
        with self.connectionStore() as store:
            gnride_page_id = store.getItem('_dev.gnride_page_id')
            if gnride_page_id:
                self.clientPublish(page_id=gnride_page_id,topic='closePage')
                store.setItem('_dev.gnride_page_id',self.page_id)
            else:
                store.setItem('_dev.gnride_page_id',self.page_id)
        root.attributes.update(overflow='hidden')
        root.gnrIdeFrame(datapath='main',debugEnabled=True)
        root.dataController("""window.focus();""",subscribe_bringToTop=True)

    def onClosePage(self):
        """TODO"""
        with self.connectionStore() as store:
            if store.getItem('_dev.gnride_page_id')==self.page_id:
                store.popNode('_dev.gnride_page_id')

     