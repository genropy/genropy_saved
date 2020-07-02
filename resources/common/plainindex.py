# -*- coding: utf-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
import os
from gnr.core.gnrbag import DirectoryResolver

class PlainIndex(BaseComponent):
    def main(self,root,**kwargs):
        self.plainIndex(root,**kwargs)

    def plainIndex(self,root,**kwargs):
        currdir = os.path.dirname(self.filepath)
        folder = DirectoryResolver(currdir,cacheTime=10,
                            include='*.py', 
                            exclude='_*,.*,%s' %self.filename,dropext=True,
                            readOnly=False)()
        root.div('Package:%s' % self.package.name,margin='20px',font_size='18px',color='#145698')
        box = root.div(margin='20px',border='2px solid #AFCBEC',rounded=6,
                                padding='10px',color='#444',font_weight='bold',_class='treecont')
        if not folder.keys():
            box.div('No pages in this package: create one in folder "webpages"')
        else:
            root.style('.treecont .dijitTreeLabel{cursor:pointer;} .treecont .dijitTreeLabel:hover{text-decoration:underline} ')
            root.data('directoryIndex.root',folder)
            root.data('directoryIndex',folder)
            box.tree(storepath='directoryIndex',
                cursor='pointer',
                connect_onClick="""
                            var attr = $1.attr;
                            if(attr.file_ext=='py'){
                                if($2.__eventmodifier=='Shift'){
                                    window.open((window.location.pathname+'/'+attr.rel_path).replace('//','/'));
                                }else{
                                    genro.gotoURL((window.location.pathname+'/'+attr.rel_path).replace('//','/'));
                                }
                                
                            }
                            """,
                                labelAttribute='caption',hideValues=True)
