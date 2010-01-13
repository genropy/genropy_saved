#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip, toText, toJson, concat
        
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
    py_requires='foundation/userobject:UserObject'
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
        
    def toolboxQueries(self, container):
        self.savedQueryController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.query.saved_menu',persist=False, inspect='shift',
                          labelAttribute='caption',connect_ondblclick='FIRE list.runQuery = true;',
                          selected_pkey='list.query.selectedId', selected_code='list.query.selectedCode',
                          _class='queryTree',
                          hideValues=True,
                          _saved='^list.query.saved', _deleted='^list.query.deleted')
        
        #btnpane = container.contentPane(region='top', height='30px').toolbar()
        self.saveQueryButton(treepane)
        self.deleteQueryButton(treepane)
        #btnpane.button('Add new query', iconClass='tb_button db_add', fire='list.query.new',showLabel=False)

    def savedQueryController(self, pane):
        pane.dataRemote('list.query.saved_menu', 'list_query', tbl=self.maintable, cacheTime=10)
        pane.dataRpc('list.query.where', 'load_query', id='^list.query.selectedId', _if='id',
                  _onResult='genro.querybuilder.buildQueryPane();')
        
        pane.dataRpc('list.query.where', 'new_query', filldefaults=True, _init=True, sync=True)
        pane.dataRpc('list.query.where', 'new_query', _fired='^list.query.new', _deleted='^list.query.deleted',
                                    _onResult='genro.querybuilder.buildQueryPane();')

    def rpc_new_query(self, filldefaults=False, **kwargs):
        result = Bag()
        if filldefaults:
            querybase = self.queryBase()
        else:
            querybase = {'op':'equal'}
        op_not = querybase.get('op_not','yes')
        not_caption = '&nbsp;' if op_not=='yes' else '!!not'
        result.setItem('c_0', querybase.get('val'), 
                        {'op':querybase.get('op'), 'column':querybase.get('column'),
                          'op_caption':'!!%s' % self.db.whereTranslator.opCaption(querybase.get('op')),
                          'not':op_not,'not_caption': not_caption,
                          'column_caption' : self.app._relPathToCaption(self.maintable, querybase.get('column'))})
        
        resultattr = dict(objtype='query', tbl=self.maintable)
        return result, resultattr

    def rpc_load_query(self, **kwargs):
        return self.rpc_loadUserObject(**kwargs)
    
    def rpc_save_query(self, userobject, userobject_attr):
        return self.rpc_saveUserObject(userobject, userobject_attr)
    
    def rpc_delete_query(self, id):
        return self.rpc_deleteUserObject(id)
    
    def rpc_list_query(self, **kwargs):
        return self.rpc_listUserObject(objtype='query', **kwargs)
        
    def rpc_list_view(self, **kwargs):
        return self.rpc_listUserObject(objtype='view', **kwargs)
        
    def saveQueryButton(self, pane):
        pane.button('Save Query', iconClass='tb_button db_save',action='FIRE #userobject_dlg.pkey = "*newrecord*";',hidden=True,showLabel=True)

    def deleteQueryButton(self, pane):
        dlg = pane.dropdownbutton('Delete query', nodeId='delete_query_btn',iconClass='icnBaseTrash',
                                hidden=True, arrow=False,showLabel=False).tooltipDialog(nodeId='delete_query_dlg', width='25em', datapath='list.query')
        dlg.div('!!Delete query',_class='tt_dialog_top')
        msg = dlg.div(font_size='0.9em',_class='pbl_roundedGroup',height='3ex',padding='10px')
        msg.div('!!Do you really want to delete the query: ')
        msg.span('^.selectedCode')
        
        buttons = dlg.div(font_size='0.9em', _class='tt_dialog_bottom')
        buttons.button('!!Delete', action='FIRE ^.delete', baseClass='bottom_btn', margin_right='5px',float='right')
        buttons.button('!!Cancel', action='genro.wdgById("delete_query_dlg").onCancel();',baseClass='bottom_btn', margin_right='5px',float='right')

        
        dlg.dataRpc('.deleteResult', 'delete_query', id='=list.query.selectedId',
                       _fired='^.delete', _onResult='genro.wdgById("delete_query_dlg").onCancel();FIRE .deleted = true')        
        

    def rpc_getQuickQuery(self,**kwargs):
        return self.rpc_listUserObject(objtype='query', onlyQuicklist=True,**kwargs)
            
    def rpc_getQuickView(self,**kwargs):
        return Bag()
        