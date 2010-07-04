# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
"""
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import gnrImport

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
        self.toolboxQueries(tc.borderContainer(title_tip='!!Queries',iconClass='icnBaseLens',showLabel=False))
        self.toolboxViews(tc.borderContainer(title_tip='!!Views',iconClass='icnBaseView'))
        self.toolboxFromResources(tc.contentPane(title_tip='!!Actions',iconClass='icnBaseAction'),res_type='actions')
        self.toolboxFromResources(tc.contentPane(title_tip='Mails',iconClass='icnBaseEmail'),res_type='mail')
        self.toolboxFromResources(tc.contentPane(title_tip='Print',iconClass='icnBasePrinter'),res_type='print')

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
    
    def toolboxFromResources(self, parent,res_type=None):
        datapath = 'list.toolbox.%s' %res_type
        sc = parent.stackContainer(datapath=datapath,selectedPage='^.currentPage')
        sc.dataFormula(".currentPage","resource?'pars':'tree';",
                        resource="^.tree.path?resource")
        treestack = sc.contentPane(pageName='tree')
        treestack.dataRemote('.tree.store', 'tableResourceTree', tbl=self.maintable, cacheTime=10,res_type=res_type)
        treestack.tree(storepath='.tree.store', persist=False, 
                          labelAttribute='caption',hideValues=True,
                          _class='toolboxResourceTree',
                          selectedPath='.tree.path',
                          selectedLabelClass='selectedTreeNode',
                          tooltip_callback="return sourceNode.attr.description || sourceNode.label;")
        parsstack = sc.borderContainer(pageName='pars')
        top = parsstack.contentPane(region='top',_class='pbl_roundedGroupLabel').div('^.tree.path?caption')
        bottom = parsstack.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
        bottom.button('!!Confirm',
                     action='var selectedPath = GET .tree.path; console.log(selectedPath); SET .tree.path=null;',
                     float='right')
        bottom.button('!!Cancel',action='SET .tree.path=null;',float='right')

        parsstack.contentPane(region='center').remote('toolboxParsPane',
                                                              resource='^.tree.path?resource',
                                                              resultpath='.pars',
                                                            res_type=res_type)
    
    def remote_toolboxParsPane(self,pane,resource='',res_type=None,resultpath=None,**kwargs):
        pkgname,tblname = self.maintable.split('.')
        resource = resource.replace('.py','')
        cl=self.site.loadResource(pkgname,'tables',tblname,res_type,"%s:WebPage" %resource)
        self.mixin(cl)
  
        self.toolbox_askParameters(pane,resultpath=resultpath)

        #self.site.resource_loader.loadTableResource(resource,table=self.maintable)
        
        #center.div('^.tree.path?description')

        
        
    def rpc_tableResourceTree(self,tbl,res_type):
        pkg,tblname = tbl.split('.')
        result = Bag()
        resources = self.site.resource_loader.resourcesAtPath(pkg,'tables/%s/%s' %(tblname,res_type),'py')
        forbiddenNodes = []
        def cb(node,_pathlist=None):
            if node.attr['file_ext'] == 'py':
                resmodule = gnrImport(node.attr['abs_path'])
                tags = getattr(resmodule,'tags','') 
                if tags and not self.application.checkResourcePermission(tags, self.userTags):
                    if node.label=='_doc':
                        forbiddenNodes.append('.'.join(_pathlist))
                    return
                caption = getattr(resmodule,'caption',node.label)
                description = getattr(resmodule,'description','')
                if  node.label=='_doc':
                    result.setAttr('.'.join(_pathlist),dict(caption=caption,description=description,tags=tags))
                else:
                
                    result.setItem('.'.join(_pathlist+[node.label]),None,caption=caption,description=description,
                                    resource=node.attr['rel_path'][:-3])            
        resources.walk(cb,_pathlist=[])
        for forbidden in forbiddenNodes:
            result.pop(forbidden)
        return result
        

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
                    _onResult='genro.viewEditor.buildCols();',
                    _onCalling='genro.viewEditor.clearCols();')
        pane.dataController("""
                              genro.viewEditor.clearCols();
                              SET list.view.structure = genro._("list.view.pyviews."+viewName).deepCopy(); 
                              genro.viewEditor.buildCols();
                              SET list.view.selectedId=null;
                              """,
                            viewName='=list.view.pyviews?baseview',_fired='^list.view.new',
                            _onStart=True)

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
        save_action = """var currentId = GET list.%s.selectedId; 
                         SET #userobject_dlg.pars.objtype = '%s';
                         SET #userobject_dlg.pars.title = 'Edit %s';
                         SET #userobject_dlg.pars.data = GET %s;
                         FIRE #userobject_dlg.pkey = currentId?currentId:"*newrecord*";
                       """%(restype,restype,restype,datapath)
        if restype=='query':
            save_action = 'genro.querybuilder.cleanQueryPane(); %s' %save_action                          
        top.div(_class='icnBase10_Doc buttonIcon',float='right',
                                connect_onclick=" SET list.%s.selectedId = null ;FIRE .new=true;" %restype, 
                                margin_right='5px', margin_top='2px', tooltip='!!New %s' % restype);
        top.div(_class='icnBase10_Save buttonIcon', float='right',margin_right='5px', margin_top='2px',
                connect_onclick=save_action,tooltip='!!Save %s' % restype);
        top.dataController("FIRE list.%s.reload; SET list.%s.selectedId = savedId;" %(restype,restype),
                            savedId="=#userobject_dlg.savedPkey",
                            objtype='=#userobject_dlg.pars.objtype',
                            restype=restype,_if='objtype==restype',
                            _fired='^#userobject_dlg.saved')
        top.div(_class='icnBase10_Trash buttonIcon', float='right',
                connect_onclick=""" SET #deleteUserObject.pars.pkey= GET .%s?id; 
                                    SET #deleteUserObject.pars.title= "Delete %s"
                                    FIRE #deleteUserObject.open;""" %(resname,restype),
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
                            'greater','greatereq','less','lesseq','between'],
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
            
    def rpc_fieldExplorer(self,table=None,omit=None):
        result = self.rpc_relationExplorer(table=table,omit=omit)
        customQuery = self.listCustomCbBag('customQuery_')       
        if customQuery:
            result.addItem('-',None) 
            #mettere customQuery dentro result in modo opportuno
            for cq in customQuery:
                result.addItem(cq.label,None,caption=cq.attr['caption'],
                                action='SET list.selectmethod= $1.fullpath; FIRE list.runQuery;')

        result.addItem('-',None)
        jsresolver = "genro.rpc.remoteResolver('getQuickQuery',null,{cacheTime:'5'})"
        result.addItem('custquery',jsresolver,_T='JS',caption='!!Custom query',action='FIRE list.query_id = $1.pkey;')
        return result
    
            
    def rpc_getQuickView(self,**kwargs):
        result = self.rpc_listUserObject(objtype='view', tbl=self.maintable,onlyQuicklist=True,**kwargs)
        return result
        
