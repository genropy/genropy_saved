#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
import cups
from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class UserObject(BaseComponent):
    py_requires='public:RecordHandler'
    def userObjectDialog(self):
        saveKwargs = dict(_onCalling="""
                                        var wherebag = GET list.query.where;
                                        $1.data.setItem('record.data',wherebag);
                                        """)
        self.recordDialog('%s.userobject' %self.package.name,'^.pkey',dlgId='userobject_dlg',
                            datapath='gnr.userobject',width='26em',height='22ex',#datapath='list.query'
                            title='!!Edit query',savePath='gnr.userobject.saved_query_id',
                             formCb=self._uo_edit_query_form,default_objtype='query',
                             default_pkg=self.package.name,default_tbl=self.maintable,
                             default_userid=self.user,saveKwargs=saveKwargs,
                             onSaved="""FIRE list.query.saved;""")

        
    def _uo_edit_query_form(self,parentContainer,disabled,table):
        pane = parentContainer.contentPane()
        fb = pane.formbuilder(cols=3, dbtable=table)
        fb.field('code',autospan=2)
        fb.field('inside_shortlist',lbl='',label='!!Shortlist')
        fb.simpleTextarea(lbl='!!Description' ,value='^.description', 
                    width='100%', border='1px solid gray',lbl_vertical_align='top',colspan=3)
        fb.field('authtags',autospan=2,lbl='!!Permissions')
        fb.field('private',lbl='',label='!!Private')
        
class ViewExporter(BaseComponent):
    def rpc_rpcSavedSelection(self, table, view=None, query=None, userid=None, out_mode='tabtext', **kwargs):
        tblobj = self.db.table(table)
        
        columns = tblobj.pkg.loadUserObject(code=view, objtype='view',  tbl=table, userid=userid)[0]
        where = tblobj.pkg.loadUserObject(code=query, objtype='query',  tbl=table, userid=userid)[0]
        
        selection = self.app._default_getSelection(tblobj=tblobj, columns=columns, where=where, **kwargs)
        return selection.output(out_mode)
        
    def savedQueryResult(self, table, view=None, query=None,
                                  order_by=None,group_by=None,
                                  having=None,distinct=False,
                                  excludeLogicalDeleted=True,
                                  **kwargs):
        tblobj = self.db.table(table)
        
        columnsBag = tblobj.pkg.loadUserObject(code=view, objtype='view',  tbl=table)[0]
        columns = self.app._columnsFromStruct(columnsBag)      
        whereBag = tblobj.pkg.loadUserObject(code=query, objtype='query',  tbl=table)[0]
        whereBag._locale = self.locale
        whereBag._workdate = self.workdate
        where, kwargs = tblobj.sqlWhereFromBag(whereBag, kwargs)
        
        query=tblobj.query(columns=columns,distinct=distinct, where=where,
                        order_by=order_by, group_by=group_by,having=having,
                        excludeLogicalDeleted=excludeLogicalDeleted,**kwargs)
        return query