#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Genro Dojo - Examples & Tutorial
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Examples & Tutorials """

#from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
import os

# ----- GnrWebPage subclass -----

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.dataRemote('tree','diskDirectory')
        root.dataFormula('selected.demopath',"'../'+p",p='^selected.page')
        root.dataRpc('demo.source','getSourceFile',linenumbers=1,demopath='^selected.demopath')
        layout = self.rootLayoutContainer(root,padding='2px',height='100%')
        layout = layout.layoutContainer(height='100%',_class='demoleft_container')
        top = layout.contentPane(layoutAlign='top').div('Page Browser', _class='demotitle')
        client = layout.contentPane(layoutAlign='client',padding='2px').splitContainer(height='100%')
        left = client.contentPane(_class='demoleft', sizeShare=15)
        tree = left.tree(storepath='tree',isTree=False,inspect='shift',selected_rel_path='selected.page')
        right = client.contentPane(sizeShare=85, _class='demoright')
        ac = right.accordionContainer(height='100%')
        demo = ac.accordionPane(title='Demo')
        demo.iframe(gnrId='rightpanedemo',border='0px', width='100%', height='100%',src='^selected.demopath')
        
        source=ac.accordionPane(title='Python Source')
        source.contentPane(gnrId='rightpanesrc',height='100%').div(value='^demo.source',_class='linecode')


# ------------  Rpc custom Calls ------------    
    def rpc_diskDirectory(self):
        return self.utils.dirbag('..',include='*.py',exclude='_*,.*,demobrowser.py')
    
    def rpc_getSourceFile(self,demopath='',linenumbers=0):
        result=self.utils.readFile(demopath)
        if not linenumbers:
            return result
        lines=result.split('\n')
        result="<table border='0' cellspacing='0' cellpadding='0' >%s</table>"
        rows=[]
        for j,line in enumerate (lines):
            rows.append("<tr><td class='linenum'>%i</td><td class='linecode r%i'>%s</td></tr>" % (j+1,j%2,line))
        result = result  % '\n'.join(rows)
        return result

#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
