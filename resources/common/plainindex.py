# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
import os
from gnr.core.gnrbag import DirectoryResolver

class PlainIndex(BaseComponent):
    def onMain(self):
        if 'adm' in self.packages.keys():
            self.mixinComponent('frameindex')

    def main(self,root):
        currdir = os.path.dirname(self.filepath)
        folder = DirectoryResolver(currdir,cacheTime=10,
                            include='*.py', 
                            exclude='_*,.*,%s' %self.filename,dropext=True,
                            readOnly=False)
        if not folder.keys():
            root.div('No pages')
        else:
            root.div('Folder content')
            for p in folder:
                root.a(p.attr['file_name'],href=p.attr['rel_path'])

