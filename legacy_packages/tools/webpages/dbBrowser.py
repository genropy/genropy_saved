#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" dbBrowser"""

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        sp=root.splitContainer()
        ac=sp.accordionContainer(sizeShare=30)
        sp_right=sp.contentPane(sizeShare=70).splitContainer(orientation='vertical')
        self.tablesPane(ac,title='Tables')
        self.columnsPane(ac,title='Columns',datapath='curr.query')
        self.queryPane(ac,title='Query',datapath='curr.query')
        self.extraPane(ac,title='Extra')
        self.listPane(sp_right.contentPane(sizeShare=30),datapath='curr.table')
        self.formPane(sp_right.contentPane(sizeShare=70),datapath='curr.form')

    def tablesPane(self,where,**kwargs):
        pane=where.accordionPane(**kwargs)
        pane.dataRemote('tabletree.tree','app.getTablesTree')
        pane.dataScript('curr.selectedTable',"SET curr.selectedPkey = '';return table",table='^tabletree.selectedTable')
        
        pane.tree(storepath='tabletree.tree', labelAttribute='caption',
                                                    isTree=False,inspect='shift',
                                                    selected_tableid='tabletree.selectedTable')
    
    def columnsPane(self,where,**kwargs):
        pane=where.accordionPane(**kwargs)
        struct=Bag()
        r=struct.child('view').child('rows')
        r.child('cell',field='col',width='60%',name='Column' )
        r.child('cell',field='as',width='30%',name='As' )
        r.child('cell',field='width',width='10%',name='Width' )
        
        pane.data('.colgrid.structure',struct)
        
        pane.data('.colgrid.data',Bag())
        pane.staticGrid(storepath='.colgrid.data',structpath='.colgrid.structure',identifier='col')

    def queryPane(self,where,**kwargs):
        pane=where.accordionPane(**kwargs)
        fb=pane.formbuilder(cols=1,labelpos='T')
        fb.numberTextBox(lbl='Limit',width='4em',value='^.limit',default=20)
        fb.textBox(lbl='Columns',width='20em',value='^.columns')
        fb.textBox(lbl='Where',width='20em',value='^.where')
        fb.textBox(lbl='Order by',width='20em',value='^.order_by')
        fb.textBox(lbl='Group by',width='20em',value='^.group_by')
        fb.checkBox(label='Distinct',value='^.distinct')
        fb.textBox(lbl='Having',width='20em',value='^.having')
        #fb.toggleButton(label='Stopped',iconClass="dijitRadioIcon",value='^.stopped',value=True)
       
    def extraPane(self,where,**kwargs):
        pane=where.accordionPane(**kwargs)
    
    def listPane(self,where,**kwargs):
        pane=where.contentPane(**kwargs)
        pane.dataSelection('.selection',table='^curr.selectedTable',columns='^curr.query.columns',
                                         where="^curr.query.where",order_by="^curr.query.order_by",
                                         distinct="^curr.query.distict",group_by="^curr.query.group_by",
                                         having="^curr.query.having",limit='^curr.query.limit',
                                         structure=True)
        
        grid=pane.staticGrid(gnrId='lstgrid',structpath=".selection.structure",
                       storepath='.selection.data',clientSort=True,
                       selectedId='curr.selectedPkey')
 

    
    def formPane(self,where,**kwargs):
        lc=where.layoutContainer(height='100%',**kwargs)
        lc.dataRecord('.record',table='^curr.selectedTable',pkey='^curr.selectedPkey',  _if='pkey&&table')
        top=lc.contentPane(layoutAlign='top',height='2.4em',border='1px solid silver',margin='2px')
        top.button('Save record')
        client=lc.contentPane(layoutAlign='client',border='1px solid silver',
                              margin='2px',datapath='.record',
                              remote='getInputForm', remote_table='^curr.selectedTable')
    
    def rpc_getInputForm(self,table='',columns=''):
        pane=self.newSourceRoot()
        fb = pane.formbuilder(cols=2,dbtable=table)
        tblobj=self.db.table(table)
        if not columns:
            columns = [colname for colname, col in tblobj.columns.items() if not col.isReserved and not col.dtype=='X'and not col.dtype=='Z']
        elif isinstance(fields, basestring):
            columns = splitAndStrip(columns)
        fb.placeFields(','.join(columns))
        return pane
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()





