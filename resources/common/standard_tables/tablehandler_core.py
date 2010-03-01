#!/usr/bin/env python
# encoding: utf-8
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import concat, jsquote
        
class ListToolbarOptions(BaseComponent):
    py_requires = 'gnrcomponents/selectionhandler'

class TableHandlerToolbox(BaseComponent):
    def lstToolbox(self,bc):
        if self.tblobj.logicalDeletionField:
            delprefpane = bc.contentPane(region='bottom',height='20px',background_color='lightgray', _class='pbl_roundedGroup', margin='3px')
            delprefpane.checkbox(value='^aux.showDeleted', label='!!Show hidden records')
            delprefpane.checkbox(value='^list.tableRecordCount', label='!!Show total count',margin_left='5px')
            delprefpane.dataController("""SET list.excludeLogicalDeleted = showDeleted? 'mark':true;""",showDeleted='^aux.showDeleted')
        self.toolboxFields(bc.contentPane(region='top',height='50%',splitter=True))
        tc = bc.tabContainer(region='center', selected='^list.selectedLeft',margin='5px',margin_top='10px')
        self.toolboxQueries(tc.borderContainer(title='',tip='!!Queries',iconClass='icnBaseLens'))
        self.toolboxViews(tc.borderContainer(title='',tip='!!Views',iconClass='icnBaseView'))
        self.toolboxActions(tc.borderContainer(title='',tip='!!Actions',iconClass='icnBaseAction'))
        tc.contentPane(title='',tip='!!Mail',iconClass='icnBaseEmail')
        tc.contentPane(title='',tip='!!Print',iconClass='icnBasePrinter')
        
    def toolboxFields(self,pane):
        treediv=pane.div(_class='treeContainer')
        treediv.tree(storepath='gnr.qb.fieldstree',persist=False,
                     inspect='shift', labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True,
                     getIconClass='if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}',
                     dndController="dijit._tree.dndSource",
                     onDndDrop="function(){this.onDndCancel();}::JS",
                     checkAcceptance='function(){return false;}::JS',
                     checkItemAcceptance='function(){return false;}::JS')
        
        #left.accordionPane(title='!!Campi collegati')
         #action="""FIRE list.query.loadQuery=$1.pkey;
             
    def toolboxActions(self, container):
        self.actionsController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.actions.actions_menu', persist=False, inspect='shift',
                          labelAttribute='caption',hideValues=True,
                          _class='queryTree')
    
    def actionsController(self, pane):
        pane.dataRemote('list.actions.actions_menu', 'list_actions', tbl=self.maintable, cacheTime=10)
        

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
    def treePane(self, pane):
        client = pane.borderContainer(region = 'center')
        client.data('hv_conf', self.hierarchicalViewConf())
        client.dataRemote('.tree_view.tree', 'selectionAsTree', selectionName='^.selectionName' )
        leftpane = client.contentPane(region = 'center', overflow='auto')
        leftpane.dataRecord('.tree_view.current_record', self.maintable, pkey='^.tree_view.selected_id')
        leftpane.tree(storepath ='.tree_view.tree',
                     selected_pkey ='.tree_view.selected_id',
                     isTree =False,
                     hideValues=True,
                     selected_rec_type = '.tree_view.current_rec_type',
                     inspect ='shift',
                     labelAttribute ='caption',
                     fired ='^.queryEnd')
        infocontainer = client.borderContainer(region = 'right', width='40%', splitter=True)
        infopane_top= infocontainer.contentPane(region = 'top', height='50%',
                                                          splitter=True,_class='infoGrid',padding ='6px')
        infopane_top.dataScript('.tree_view.info_table',
                            """var current_rec_type= current_record.getItem('rec_type');
                               var result = new gnr.GnrBag();
                               var fields = info_fields.getNodes()
                               for (var i=0; i<fields.length; i++){
                                   var fld_rec_types = fields[i].getAttr('rec_types',null);
                                   var fld_label = fields[i].getAttr('label');
                                   if (fld_rec_types){
                                       fld_rec_types=fld_rec_types.split(',');
                                   }
                                   var fld_val_path = fields[i].getAttr('val_path');
                                   var fld_show_path = fields[i].getAttr('show_path');
                                   
                                   var fld_value = current_record.getItem(fld_val_path);
                                   var fld_show = current_record.getItem(fld_show_path);
                                   if (!fld_rec_types || dojo.indexOf(fld_rec_types, current_rec_type)!=-1){
                                       result.setItem('R_'+i,
                                                       null,
                                                      {'lbl':fld_label, 'val':fld_value,'show':fld_show})
                                   }
                               }
                               return result""",
                               info_fields = '=hv_conf',
                               current_record='=.tree_view.current_record',
                               fired='^.tree_view.current_record.id')
        infopane_top.includedView(storepath='.tree_view.info_table', struct=self._infoGridStruct())
        infoStackContainer = infocontainer.stackContainer(region = 'center',
                                                          selected='^.tree_view.stack.selectedPage')
        infoStackContainer.contentPane()
        callbacks = [(x.split('_')[1],x) for x in dir(self) if x.startswith('infoPane_')]
        infoStackContainer.data('rec_types', ','.join([x[0] for x in callbacks]))
        infoStackContainer.dataController("""rec_types = rec_types.split(',');
                                             var n = dojo.indexOf(rec_types,rec_type);
                                             if (n!=-1){SET list.tree_view.stack.selectedPage=n+1;};""",
                                           rec_types = '=rec_types',
                                           rec_type = '^.tree_view.current_rec_type')
        for cb in callbacks:
            getattr(self, cb[1])(infoStackContainer.contentPane(padding ='6px',
                                                                _class='pbl_roundedGroup',
                                                                datapath='.tree_view.current_record'))


    def savedViewController(self, pane):
        pane.dataRemote('list.view.saved_menu', 'list_view', tbl=self.maintable, cacheTime=10)
        pane.dataRpc('list.view.structure', 'load_view', id='^list.view.selectedId', _if='id',
                    _onResult='genro.viewEditor.colsFromBag();')
        pane.dataRpc('list.view.structure', 'new_view', _reason='^list.view.new',
                    _onResult="""
                                //genro.viewEditor.colsFromBag(); 
                                SET list.view.selectedId=null;
                                """ ,filldefaults=True)

    def toolboxViews(self, container):
        self.savedViewController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.view.saved_menu',persist=False, inspect='shift',
                          labelAttribute='caption', connect_ondblclick='FIRE list.runQuery = true;',
                          selected_pkey='list.view.selectedId', selected_code='list.view.selectedCode',
                          _class='queryTree',hideValues=True,
                          _reload='^list.view.reload')
                          
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
        
class LstUserObjects(BaseComponent):
    def lstEditors_main(self,topStackContainer):
        extendedQueryPane = topStackContainer.contentPane(onEnter='FIRE list.runQuery=true;')
        self.editorPane('query', extendedQueryPane, datapath='list.query.where')
        ve_editpane = topStackContainer.contentPane()
        fb = ve_editpane.dropdownbutton('', hidden=True, nodeId='ve_colEditor', datapath='^vars.editedColumn').tooltipdialog().formbuilder(border_spacing='3px', font_size='0.9em', cols=1)
        fb.textbox(lbl='Name', value='^.?name') 
        fb.textbox(lbl='Width', value='^.?width')
        fb.textbox(lbl='Color', value='^.?color')
        fb.textbox(lbl='Background', value='^.?background_color')
        self.editorPane('view', ve_editpane, datapath='list.view.structure')
        
    def editorPane(self, restype, pane, datapath):
        parentdatapath, resname = datapath.rsplit('.', 1)
        top = pane.div(_class='st_editor_bar', datapath=parentdatapath)    
        top.div(_class='icnBase10_Doc buttonIcon',float='right',
                                connect_onclick=" SET list.%s.selectedId = null ;FIRE .new=true;" %restype, 
                                margin_right='5px', margin_top='2px', tooltip='!!New %s' % restype);
        top.div(_class='icnBase10_Save buttonIcon', float='right',margin_right='5px', margin_top='2px',
                connect_onclick="""var currentId = GET list.%s.selectedId; 
                                   SET #userobject_dlg.pars.objtype = '%s';
                                   SET #userobject_dlg.pars.title = 'Edit %s';
                                   SET #userobject_dlg.pars.data = GET %s;
                                   FIRE #userobject_dlg.pkey = currentId?currentId:"*newrecord*";
                                   """%(restype,restype,restype,datapath),
                tooltip='!!Save %s' % restype);
        top.dataController("FIRE list.%s.reload; SET list.%s.selectedId = savedId;" %(restype,restype),
                            savedId="=#userobject_dlg.savedPkey",
                            objtype='=#userobject_dlg.pars.objtype',
                            restype=restype,_if='objtype==restype',
                            _fired='^#userobject_dlg.saved')
        top.div(_class='icnBase10_Trash buttonIcon', float='right',
                connect_onclick=""" SET #deleteUserObject.pars.pkey= GET .%s?id; 
                                    SET #deleteUserObject.pars.title= "Delete %s"
                                    FIRE #deleteUserObject.show;""" %(resname,restype),
                margin_left='5px', margin_right='15px',
                margin_top='2px', tooltip='!!Delete %s' % restype,
                visible='^.%s?id' % resname)
        top.dataController("FIRE list.%s.reload; FIRE list.%s.new;"%(restype,restype),
                            _fired="^#deleteUserObject.deleted",restype=restype,
                            objtype='=#userobject_dlg.pars.objtype',
                            _if='objtype==restype')
        top.div(content='^.%s?code' % resname, _class='st_editor_title')
        pane.div(_class='st_editor_body st_editor_%s' % restype, nodeId='%s_root' % restype, datapath=datapath)

     
class LstQueryHandler(BaseComponent):
    def rpc_getSqlOperators(self):
        result = Bag()
        listop=('equal','startswith','wordstart','contains','startswithchars','greater','greatereq',
                    'less','lesseq','between','isnull','istrue','isfalse','nullorempty','in','regex')
        optype_dict = dict(alpha=['contains','startswith','equal','wordstart',
                            'startswithchars','isnull','nullorempty','in','regex',
                            'greater','greatereq','less','lesseq'],
                      date=['equal','in','isnull','greater','greatereq','less','lesseq','between'],
                      number=['equal','greater','greatereq','less','lesseq','isnull','in'],
                      boolean=['istrue','isfalse','isnull'],
                      others=['equal','greater','greatereq','less','lesseq','in'])
        
        wt = self.db.whereTranslator
        for op in listop:
            result.setItem('op.%s' % op,  None, caption='!!%s' % wt.opCaption(op))
        for optype,values in optype_dict.items():
            for operation in values:
                result.setItem('op_spec.%s.%s' % (optype,operation), operation, caption='!!%s' % wt.opCaption(operation))
        customOperatorsHandlers=[(x[12:],getattr(self,x)) for x in dir(self) if x.startswith('customSqlOp_') ]
        for optype,handler in customOperatorsHandlers:
            operation,caption=handler(optype_dict=optype_dict)
            result.setItem('op_spec.%s.%s' % (optype,operation), operation, caption=caption)
            result.setItem('op.%s' % operation,  None, caption=caption)
            
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
                          hideValues=True,_reload='^list.query.reload')
                          
    def savedQueryController(self, pane):
        pane.dataRemote('list.query.saved_menu', 'list_query', tbl=self.maintable, cacheTime=3)
        
        pane.dataRpc('list.query.where', 'load_query', id='^list.query.selectedId', _if='id',
                  _onResult='genro.querybuilder.buildQueryPane();')
        pane.dataRpc('list.query.where', 'new_query', filldefaults=True, _onStart=True, sync=True)
        pane.dataRpc('list.query.where', 'new_query', _reason='^list.query.new',
                        _onResult="""genro.querybuilder.buildQueryPane(); 
                                    SET list.view.selectedId = null;
                                    """,
                        filldefaults=True)
        

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
    
    def rpc_list_query(self, **kwargs):
        return self.rpc_listUserObject(objtype='query', **kwargs)
        
    def rpc_list_view(self, **kwargs):
        return self.rpc_listUserObject(objtype='view', **kwargs)

    def rpc_getQuickQuery(self,**kwargs):        
        result = self.rpc_listUserObject(objtype='query', tbl=self.maintable,onlyQuicklist=True,**kwargs)
        return result
            
            
    def rpc_getQuickView(self,**kwargs):
        return Bag()
        
