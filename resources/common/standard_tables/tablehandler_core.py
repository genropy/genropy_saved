#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip, toText, toJson, concat, jsquote
        
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
        
        
class ListViewHandler(BaseComponent):
    def savedViewController(self, pane):
        pane.dataRemote('list.view.saved_menu', 'list_view', tbl=self.maintable, cacheTime=10)
        pane.dataRpc('list.view.structure', 'load_view', id='^list.view.selectedId', _if='id',
                    _onResult='genro.viewEditor.colsFromBag();'
                  )        
        pane.dataController("FIRE list.view.saved",_fired="^#userobject_dlg.saved",
                            objtype='=#userobject_dlg.pars.objtype',_if='objtype=="view"')
                            
        pane.dataRpc('list.view.structure', 'new_view', _fired='^list.view.new', _deleted='^list.view.deleted',
                                    _onResult='genro.viewEditor.colsFromBag();' #filldefaults='^gnr.onStart'
                        )

    
    def saveViewButton(self, pane):
        dlg = pane.button('Save Views', iconClass='tb_button db_save',nodeId='save_view_btn', hidden=True,
                                  arrow=False,showLabel=False)

    def deleteViewButton(self, pane):
        dlg = pane.dropdownbutton(iconClass='icnBaseTrash', hidden=True, arrow=False,showLabel=False,nodeId='delete_view_btn').tooltipDialog(nodeId='delete_view_dlg', width='25em', datapath='list.view')
        msg = dlg.div( font_size='0.9em')
        msg.span('!!Do you really want to delete the query: ')
        msg.span('^.selectedCode')
        
        buttons = dlg.div(height='2em',  font_size='0.9em')
        buttons.button('!!Delete', fire='^.delete', iconClass='icnBaseTrash', float='right')
        buttons.button('!!Cancel', action='genro.wdgById("delete_view_dlg").onCancel();', iconClass='icnBaseCancel', float='right')        
        dlg.dataRpc('.deleteResult', 'delete_view', id='=list.view.selectedId',
                       _fired='^.delete', _onResult='genro.wdgById("delete_view_dlg").onCancel();FIRE .deleted = true')
    
    def rpc_new_view(self, filldefaults=False, **kwargs):
        if filldefaults:
            result=self.lstBase(self.newGridStruct())
        else:
            result = self.newGridStruct()
            result.view().rows()
        resultattr = dict(objtype='view', tbl=self.maintable)
        return result, resultattr
    
    def rpc_load_view(self, **kwargs):
        return self.rpc_loadUserObject(**kwargs)
    
    def rpc_save_view(self, userobject, userobject_attr):
        return self.rpc_saveUserObject(userobject, userobject_attr)
    
    def rpc_delete_view(self, id):
        return self.rpc_deleteUserObject(id)        
        
class ListQueryHandler(BaseComponent):
    def editorPane(self, restype, pane, datapath):
        parentdatapath, resname = datapath.rsplit('.', 1)
        top = pane.div(_class='st_editor_bar', datapath=parentdatapath)    
        top.div(_class='icnBase10_Doc buttonIcon',float='right',
                                connect_onclick=" SET list.query.selectedId = null ;FIRE .new=true;",
                                margin_right='5px', margin_top='2px', tooltip='!!New %s' % restype);
        top.div(_class='icnBase10_Save buttonIcon', float='right',margin_right='5px', margin_top='2px',
                connect_onclick="""var currentId = GET list.%s.selectedId; 
                                   SET #userobject_dlg.pars.objtype = '%s';
                                   SET #userobject_dlg.pars.title = 'Edit %s';
                                   SET #userobject_dlg.pars.data = GET %s;
                                   FIRE #userobject_dlg.pkey = currentId?currentId:"*newrecord*";
                                   """%(restype,restype,restype,datapath),
                tooltip='!!Save %s' % restype);
        top.div(_class='icnBase10_Trash buttonIcon', float='right',
                                                onCreated="genro.dlg.connectTooltipDialog($1,'delete_%s_btn')" % restype,
                                                margin_left='5px', margin_right='15px',
                                                margin_top='2px', tooltip='!!Delete %s' % restype,
                                                visible='^.%s?id' % resname)
        top.div(content='^.%s?code' % resname, _class='st_editor_title')
        pane.div(_class='st_editor_body st_editor_%s' % restype, nodeId='%s_root' % restype, datapath=datapath)
        self.deleteQueryButton(pane)

    def savedQueryController(self, pane):
        pane.dataRemote('list.query.saved_menu', 'list_query', tbl=self.maintable, cacheTime=10)
        pane.dataRpc('list.query.where', 'load_query', id='^list.query.selectedId', _if='id',
                  _onResult='genro.querybuilder.buildQueryPane();')
        pane.dataController("FIRE list.query.saved",_fired="^#userobject_dlg.saved",
                            objtype='=#userobject_dlg.pars.objtype',_if='objtype=="query"')
        pane.dataRpc('list.query.where', 'new_query', filldefaults=True, _onStart=True, sync=True)
        pane.dataRpc('list.query.where', 'new_query', _fired='^list.query.new', _deleted='^list.query.deleted',
                        _onResult='genro.querybuilder.buildQueryPane(); SET list.view.selectedId = null;')
        
    def rpc_getSqlOperators(self):
        result = Bag()
        listop=('equal','startswith','wordstart','contains','startswithchars','greater','greatereq','less','lesseq','between','isnull','nullorempty','in','regex')
        optype = dict(alpha=['contains','startswith','equal','wordstart',
                            'startswithchars','isnull','nullorempty','in','regex'],
                      date=['equal','in','isnull','greater','greatereq','less','lesseq','between'],
                      number=['equal','greater','greatereq','less','lesseq','isnull','in'],
                      others=['equal','greater','greatereq','less','lesseq','in'])
        
        wt = self.db.whereTranslator
        for op in listop:
            result.setItem('op.%s' % op,  None, caption='!!%s' % wt.opCaption(op))
        for optype,values in optype.items():
            for operation in values:
                result.setItem('op_spec.%s.%s' % (optype,operation), operation, caption='!!%s' % wt.opCaption(operation))
        result.setItem('op_spec.unselected_column.x',None,caption='!!Please select the column')
            
            
        result.setItem('jc.and', None, caption='!!AND')
        result.setItem('jc.or', None, caption='!!OR')
        
        result.setItem('not.yes', None, caption='&nbsp;')
        result.setItem('not.not', None, caption='!!NOT')
        
        return result
        
    def rpc_relationExplorer(self, table, prevRelation='', prevCaption='', omit='',quickquery=False, **kwargs):
        def buildLinkResolver(node, prevRelation, prevCaption):
            nodeattr = node.getAttr()
            if not 'name_long' in nodeattr:
                raise Exception(nodeattr) # FIXME: use a specific exception class
            nodeattr['caption'] = nodeattr.pop('name_long')
            nodeattr['fullcaption'] = concat(prevCaption, self._(nodeattr['caption']), ':')
            if nodeattr.get('one_relation'):
                nodeattr['_T'] = 'JS'
                if nodeattr['mode']=='O':
                    relpkg, reltbl, relfld = nodeattr['one_relation'].split('.')
                else:
                    relpkg, reltbl, relfld = nodeattr['many_relation'].split('.')
                jsresolver = "genro.rpc.remoteResolver('relationExplorer',{table:%s, prevRelation:%s, prevCaption:%s, omit:%s})"
                node.setValue(jsresolver % (jsquote("%s.%s" % (relpkg, reltbl)), jsquote(concat(prevRelation, node.label)), jsquote(nodeattr['fullcaption']), jsquote(omit)))
        result = self.db.relationExplorer(table=table, 
                                         prevRelation=prevRelation,
                                         omit=omit,
                                        **kwargs)
        result.walk(buildLinkResolver, prevRelation=prevRelation, prevCaption=prevCaption)
        if quickquery:
            result.addItem('-',None)
            jsresolver = "genro.rpc.remoteResolver('getQuickQuery',null,{cacheTime:'5'})"
            result.addItem('custquery',jsresolver,_T='JS',caption='!!Custom query',action='FIRE list.query_id = $1.pkey;')
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
        

    def rpc_new_query(self, filldefaults=False, **kwargs):
        result = Bag()
        if filldefaults:
            querybase = self.queryBase()
        else:
            querybase = {'op':'equal'}
        op_not = querybase.get('op_not','yes')
        column = querybase.get('column')
        column_dtype = None
        if column:
            column_dtype = self.tblobj.column(column).getAttr('dtype')
        not_caption = '&nbsp;' if op_not=='yes' else '!!not'
        result.setItem('c_0', querybase.get('val'), 
                        {'op':querybase.get('op'),'column':column,
                         'op_caption':'!!%s' %self.db.whereTranslator.opCaption(querybase.get('op')),
                         'not':op_not,'not_caption': not_caption,
                         'column_dtype': column_dtype,
                         'column_caption' : self.app._relPathToCaption(self.maintable, column)})
        
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
        result = self.rpc_listUserObject(objtype='query', tbl=self.maintable,onlyQuicklist=True,**kwargs)
        return result
            
            
    def rpc_getQuickView(self,**kwargs):
        return Bag()