#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip, toText, toJson, concat


# --------------------------- GnrWebPage subclass ---------------------------
class UserObject(BaseComponent):
    py_requires='foundation/recorddialog'
    def userObjectDialog(self):
        saveKwargs = dict(_onCalling="""
                                        var wherebag = GET list.query.where;
                                        $1.data.setItem('record.data',wherebag);
                                        """,changesOnly=False,saveAlways=True)
        self.recordDialog('%s.userobject' %self.package.name,'^.pkey',dlgId='userobject_dlg',
                            datapath='gnr.userobject',width='26em',height='22ex',
                            title='!!Edit query',savePath='gnr.userobject.saved_query_id',
                             formCb=self._uo_edit_query_form,default_objtype='query',
                             default_pkg=self.package.name,default_tbl=self.maintable,
                             default_userid=self.user,saveKwargs=saveKwargs,
                             onSaved="""FIRE list.query.saved;""")
        
    def _uo_edit_query_form(self,parentContainer,disabled,table):
        pane = parentContainer.contentPane()
        fb = pane.formbuilder(cols=3, dbtable=table)
        fb.field('code',autospan=2)
        fb.field('quicklist',lbl='',label='!!Quicklist')
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
        
class ListQueryHandler(BaseComponent):
    def rpc_getSqlOperators(self):
        result = Bag()
        listop=('equal','startswith','wordstart','contains','startswithchars','greater','greatereq','less','lesseq','between','isnull','nullorempty','in','regex')
        wt = self.db.whereTranslator
        for op in listop:
            result.setItem('op.%s' % op, None, caption='!!%s' % wt.opCaption(op))
            
        for op in ('startswith','wordstart','contains','regex'):
            result.setAttr('op.%s' % op, onlyText=True)
            
        result.setItem('jc.and', None, caption='!!AND')
        result.setItem('jc.or', None, caption='!!OR')
        
        result.setItem('not.yes', None, caption='&nbsp;')
        result.setItem('not.not', None, caption='!!NOT')
        
        return result
        
    def rpc_relationExplorer(self, table, prevRelation='', prevCaption='', omit='',quickquery=False, **kwargs):
        def buildLinkResolver(node, prevRelation, prevCaption):
            nodeattr = node.getAttr()
            if not 'name_long' in nodeattr:
                raise str(nodeattr)
            nodeattr['caption'] = nodeattr.pop('name_long')
            nodeattr['fullcaption'] = concat(prevCaption, self._(nodeattr['caption']), ':')
            if nodeattr.get('one_relation'):
                nodeattr['_T'] = 'JS'
                if nodeattr['mode']=='O':
                    relpkg, reltbl, relfld = nodeattr['one_relation'].split('.')
                else:
                    relpkg, reltbl, relfld = nodeattr['many_relation'].split('.')
                jsresolver = "genro.rpc.remoteResolver('relationExplorer',{table:'%s.%s', prevRelation:'%s', prevCaption:'%s', omit:'%s'})"
                node.setValue(jsresolver % (relpkg, reltbl, concat(prevRelation, node.label), nodeattr['fullcaption'], omit))
        result = self.db.relationExplorer(table=table, 
                                         prevRelation=prevRelation,
                                         omit=omit,
                                        **kwargs)
        result.walk(buildLinkResolver, prevRelation=prevRelation, prevCaption=prevCaption)
        if quickquery:
            result.addItem('-',None)
            jsresolver = "genro.rpc.remoteResolver('getQuickQuery',null,{cacheTime:'5'})"
            result.addItem('custquery',jsresolver,_T='JS',caption='!!Custom query',action='FIRE list.query_id = $1.query_id;')

        return result
        
    def rpc_getQuickQuery(self,**kwargs):
        result = Bag()
        tbluserobject = self.db.table('%s.userobject' %self.package.name)
        f = tbluserobject.query(where='$tbl=:curr_tbl AND quicklist IS TRUE', 
                                curr_tbl=self.maintable).fetch()
        for r in f:
            result.setItem('%s' %r['code'], None,caption=r['description'],query_id=r['id'])
        return result
            
    def rpc_getQuickView(self,**kwargs):
        return Bag()
        