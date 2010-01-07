#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  GenroDbExplorer - Just a little database explorer
#
#  Created by Giovanni Porcari on 2007-03-07.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Database Explorer"""

from gnr.core.gnrbag import Bag




class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        return None
    
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root,padding='2px', padding_bottom='4px', overflow='hidden')
        root.script("genro.currentTable='';genro.changeTable=function(tablename){genro.currentTable=tablename};")
        
        layout = root.layoutContainer(name='form', height='100%')
        layout.contentPane(name='top', layoutAlign='top'
                           ).div('GenroDbExplorer - Just a little database explorer...', _class='demotitle')
        
        client = layout.contentPane(name='client', layoutAlign='client', padding='2px'
                                    ).splitContainer(name='split', sizerWidth=2, height='100%')
        tablesmenu = self.menubar.data('Tables',self.app.getTablesTree(), 
                               action="function(attributes){genro.changeTable(attributes.tableid)}")
        
        self.leftColumn(client)
        self.mainPane(client)
        bottom = layout.contentPane(name='bottom', layoutAlign='bottom', height='2em;')
        self.adminBottom(bottom)
        
    def adminBottom(self, pane):
        pass
        
    def leftColumn(self, pane):
        left = pane.contentPane(name='left', sizeShare=25, overflow='auto')
     
    
        tableTree = left.tree(name='fieldsTree',
                                      datasource='menubar.Tables', gnrId='fieldsTree',overflow_y='auto' )
        tableTree.subscribe(tableTree, event='onSelect', func="""function(treenode){
                                                                    var tid=genro.getDataAttr(treenode,'tableid');
                                                                    genro.changeTable(tid)}""" )
 
    def mainPane(self, pane):
        right = pane.contentPane(name='main', sizeShare=85, _class='demoright', subscribe='genro/changeTable:*updateContent')
        right.remote('getClientPane', dbtable='=genro.currentTable')
        
    def rpc_getClientPane(self, dbtable, **kwargs):
        root = self.newSourceRoot()
        if dbtable:
            lc = root.splitContainer(gnrId='split', height='100%', width='100%', sizerWidth=7, orientation='orizontal', closable=True)
            self.dbform.topPane(lc.contentPane(sizeShare=30), dbtable=dbtable)
            self.dbform.bodyPane(lc.contentPane(sizeShare=70), dbtable=dbtable)
        return root

        