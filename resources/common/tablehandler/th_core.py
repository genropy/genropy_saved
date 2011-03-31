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
from gnr.web.gnrwebstruct import struct_method

from gnr.core.gnrbag import Bag

class StackTableHandler(BaseComponent):
    py_requires='tablehandler/th_list:TableHandlerListBase,tablehandler/th_form:TableHandlerFormBase'
    @struct_method
    def th_stackTableHandler(self,pane,table=None,datapath=None,formName=None,viewName=None,**kwargs):
        pkg,tablename = table.split('.')
        tableCode = table.replace('.','_')
        defaultName = 'th_%s' %tablename
        formName = formName or defaultName
        viewName = viewName or defaultName
        self.mixinComponent(pkg,'tables',tablename,'%s:Form' %formName)
        self.mixinComponent(pkg,'tables',tablename,'%s:View' %viewName)
        sc = pane.stackContainer(datapath=datapath or '.%s'%tableCode,selectedPage='^.selectedPage',**kwargs)
        viewpage = sc.listPage(frameCode='%s_list' %tableCode,table=table,
                                linkedForm='%s_form' %tableCode,pageName='view')
        formpage = sc.formPage(frameCode='%s_form' %tableCode,table=table,pageName='form')
        formpage.attributes['formsubscribe_onLoaded'] = 'SET .#parent.selectedPage="form";'
        formpage.attributes['formsubscribe_onDismissed'] = 'SET .#parent.selectedPage="view";'
        formpage.store.attributes['parentStore'] = '%s_list_grid' %tableCode
        viewpage.iv.attributes['selfsubscribe_add'] = 'genro.getForm(this.attr.linkedForm).load({destPkey:"*newrecord*"});'
        viewpage.iv.attributes['selfsubscribe_del'] = 'var pkeyToDel = this.widget.getSelectedPkeys(); console.log(pkeyToDel);' #'genro.getForm(this.attr.linkedForm).deleteItem({});'
        return sc


class TableHandlerCommon(BaseComponent):
    def userCanWrite(self):
        return self.application.checkResourcePermission(self.tableWriteTags(), self.userTags)

    def userCanDelete(self):
        return self.application.checkResourcePermission(self.tableDeleteTags(), self.userTags)

    def tableWriteTags(self):
        return 'superadmin'

    def tableDeleteTags(self):
        return 'superadmin'

    def rpc_onLoadingSelection(self, selection):
        """ovverride if you need"""
        pass

    def rowsPerPage(self):
        return 25

    def hiddencolumnsBase(self):
        return

    def hierarchicalViewConf(self):
        return None

    def hierarchicalEdit(self):
        return None

    def formTitleBase(self, pane):
        pane.data('form.title', self.tblobj.attributes.get('name_long', 'Record'))
        
    def onSavingFormBase(self):
        """JS ONCALLING OF RPCSAVING PROCESS
           params inside js:
           data: what you send
           form: the formBase js object
           if you return false the rpc is not called;
        """
        return None

class TableHandlerToolbox(BaseComponent):
    py_requires = 'gnrcomponents/batch_handler/batch_handler:TableScriptRunner'

    def _th_toolboxController(self,pane):
        pane.data('list.showToolbox', False)
        pane.data('list.showExtendedQuery', False)
        pane.dataController("""genro.wdgById("gridbc").showHideRegion("top",showquery);genro.resizeAll();""",
                            showquery='^list.showExtendedQuery',
                            _fired='^gnr.onStart')
        pane.dataController("""if(page=='view'){SET list.selectedTop=1;}
                                   else if(page=='query'){SET list.selectedTop=0;}
                                """, page='^list.toolboxSelected')

        pane.dataController("""genro.wdgById("gridbc").showHideRegion("left",show);
                                genro.resizeAll();
                               genro.publish('main_left_set_status',!show);
                               """,
                            show='^list.showToolbox', _fired='^gnr.onStart')
        pane.dataFormula('list.showExtendedQuery', "true", _if='where.len()>1', where='^list.query.where')
        
    def lstToolbox(self, bc):
        self._th_toolboxController(bc)
        if self.tblobj.logicalDeletionField:
            delprefpane = bc.contentPane(region='bottom', height='20px', background_color='lightgray',
                                         _class='pbl_roundedGroup', margin='3px')
            delprefpane.checkbox(value='^aux.showDeleted', label='!!Show hidden records')
            delprefpane.checkbox(value='^list.tableRecordCount', label='!!Show total count', margin_left='5px')
            delprefpane.dataController("""SET list.excludeLogicalDeleted = showDeleted? 'mark':true;""",
                                       showDeleted='^aux.showDeleted')
        self.toolboxFields(bc.contentPane(region='top', height='50%', splitter=True))
        tc = bc.tabContainer(region='center', selectedPage='^list.toolboxSelected', margin='5px', margin_top='10px')
        self.toolboxQueries(
                tc.borderContainer(title_tip='!!Queries', pageName='query', iconClass='icnBaseLens', showLabel=False))
        self.toolboxViews(tc.borderContainer(title_tip='!!Views', pageName='view', iconClass='icnBaseView'))

        self.toolboxFromResources(tc.contentPane(title_tip='!!Actions', pageName='action', iconClass='icnBaseAction'),
                                  res_type='action')
        self.toolboxFromResources(tc.contentPane(title_tip='Mails', pageName='mail', iconClass='icnBaseEmail'),
                                  res_type='mail')
        self.toolboxFromResources(tc.contentPane(title_tip='Prints', pageName='print', iconClass='icnBasePrinter'),
                                  res_type='print')
        tc.dataController("""
                            var selectedRowidx = genro.wdgById('maingrid').getSelectedRowidx();
                            var script_pars = {'res_type':tablehandler_run_script[0],
                                                'resource':tablehandler_run_script[1],
                                                'onCalling': tablehandler_run_script[2],
                                                'table':table,
                                                'selectedRowidx':selectedRowidx,
                                                'selectionName':selectionName,
                                                'structpath':'list.view.structure'};
                            PUBLISH table_script_run = script_pars;
                            """, subscribe_tablehandler_run_script=True, table=self.maintable,
                          selectionName='=list.selectionName')

    def toolboxFromResources(self, parent, res_type=None):
        datapath = 'list.toolbox.%s' % res_type
        pane = parent.contentPane(datapath=datapath)
        self.table_script_resource_tree(pane, table=self.maintable, res_type=res_type,
                                        selectionName='=list.selectionName',
                                        gridId='maingrid', _class='toolboxResourceTree')

    def toolboxFields(self, pane):
        treediv = pane.div(_class='treeContainer')
        treediv.tree(storepath='gnr.qb.fieldstree', persist=False,
                     inspect='shift', labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True, nodeId='treeField',
                     onDrag="""
                                if(!(treeItem.attr.dtype && treeItem.attr.dtype!='RM' && treeItem.attr.dtype!='RO')){
                                    return false;
                                }
                               var fldinfo=objectUpdate({},treeItem.attr);
                               var maintable = genro._('gnr.maintable');
                               fldinfo['maintable']=maintable;
                               dragValues['text/plain']=treeItem.attr.fieldpath;
                               dragValues['gnrdbfld_'+maintable.replace('.','_')]=fldinfo;                            
                             """,
                     draggable=True,
                     getIconClass='if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}')

class ViewExporter(BaseComponent):
    def rpc_rpcSavedSelection(self, table, view=None, query=None, userid=None, out_mode='tabtext', **kwargs):
        tblobj = self.db.table(table)

        columns = tblobj.pkg.loadUserObject(code=view, objtype='view', tbl=table, userid=userid)[0]
        where = tblobj.pkg.loadUserObject(code=query, objtype='query', tbl=table, userid=userid)[0]

        selection = self.app._default_getSelection(tblobj=tblobj, columns=columns, where=where, **kwargs)
        return selection.output(out_mode)

    def savedQueryResult(self, table, view=None, query=None,
                         order_by=None, group_by=None,
                         having=None, distinct=False,
                         excludeLogicalDeleted=True,
                         **kwargs):
        tblobj = self.db.table(table)

        columnsBag = tblobj.pkg.loadUserObject(code=view, objtype='view', tbl=table)[0]
        columns = self.app._columnsFromStruct(columnsBag)
        whereBag = tblobj.pkg.loadUserObject(code=query, objtype='query', tbl=table)[0]
        whereBag._locale = self.locale
        whereBag._workdate = self.workdate
        where, kwargs = tblobj.sqlWhereFromBag(whereBag, kwargs)

        query = tblobj.query(columns=columns, distinct=distinct, where=where,
                             order_by=order_by, group_by=group_by, having=having,
                             excludeLogicalDeleted=excludeLogicalDeleted, **kwargs)
        return query

class ListViewHandler(BaseComponent):
    def savedViewController(self, pane):
        pane.dataRemote('list.view.saved_menu', 'list_view', tbl=self.maintable, cacheTime=10)
        pane.dataRpc('list.view.structure', 'load_view', id='^list.view.selectedId', _if='id')
        pane.dataController("""
                              SET list.view.structure = genro._("list.view.pyviews."+viewName).deepCopy(); 
                              SET list.view.selectedId=null;
                              """,
                            viewName='=list.view.pyviews?baseview', _fired='^list.view.new',
                            _onStart=True)

    def toolboxViews(self, container):
        self.savedViewController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.view.saved_menu', persist=False, inspect='shift',
                      labelAttribute='caption', connect_ondblclick='FIRE list.runQuery = true;',
                      selected_pkey='list.view.selectedId', selected_code='list.view.selectedCode',
                      _class='queryTree', hideValues=True,
                      _reload='^list.view.reload')

    def rpc_new_view(self, filldefaults=False, **kwargs):
        if filldefaults:
            result = self.lstBase(self.newGridStruct())
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
    def lstEditors_main(self, sc):
        sc.dataController("""
                          var currentId = this.getRelativeData('list.'+restype+'.selectedId'); 
                         SET #userobject_dlg.pars.objtype = restype;
                         SET #userobject_dlg.pars.title = 'Edit '+restype;
                         var data_path = restype=='query'?query_path:view_path;
                         SET #userobject_dlg.pars.data = this.getRelativeData(data_path);
                         FIRE #userobject_dlg.pkey = currentId?currentId:"*newrecord*";
                       """, restype="^list.save_userobject",
                          query_path='list.query.where',
                          view_path='list.view.structure')

        extendedQueryPane = sc.contentPane(onEnter='FIRE list.runQuery=true;')
        self.editorPane('query', extendedQueryPane, datapath='list.query.where')
        ve_editpane = sc.contentPane()
        fb = ve_editpane.dropdownbutton('', hidden=True, nodeId='ve_colEditor',
                                        datapath='^vars.editedColumn').tooltipdialog().formbuilder(border_spacing='3px',
                                                                                                   font_size='0.9em',
                                                                                                   cols=1)
        fb.textbox(lbl='Name', value='^.?name')
        fb.textbox(lbl='Width', value='^.?width')
        fb.textbox(lbl='Color', value='^.?color')
        fb.textbox(lbl='Background', value='^.?background_color')
        self.editorPane('view', ve_editpane, datapath='list.view.structure')

    def editorPane(self, restype, pane, datapath):
        parentdatapath, resname = datapath.rsplit('.', 1)
        top = pane.div(_class='st_editor_bar', datapath=parentdatapath)
        save_action = 'FIRE list.save_userobject="%s";' % restype
        if restype == 'query':
            save_action = 'genro.querybuilder.cleanQueryPane(); %s' % save_action
        top.div(_class='icnBase10_Doc buttonIcon', float='right',
                connect_onclick=" SET list.%s.selectedId = null ;FIRE .new=true;" % restype,
                margin_right='5px', margin_top='2px', tooltip='!!New %s' % restype);
        top.div(_class='icnBase10_Save buttonIcon', float='right', margin_right='5px', margin_top='2px',
                connect_onclick=save_action, tooltip='!!Save %s' % restype);
        top.dataController("FIRE list.%s.reload; SET list.%s.selectedId = savedId;" % (restype, restype),
                           savedId="=#userobject_dlg.savedPkey",
                           objtype='=#userobject_dlg.pars.objtype',
                           restype=restype, _if='objtype==restype',
                           _fired='^#userobject_dlg.saved')
        top.div(_class='icnBase10_Trash buttonIcon', float='right',
                connect_onclick=""" SET #deleteUserObject.pars.pkey= GET .%s?id; 
                                    SET #deleteUserObject.pars.title= "Delete %s"
                                    FIRE #deleteUserObject.open;""" % (resname, restype),
                margin_left='5px', margin_right='15px',
                margin_top='2px', tooltip='!!Delete %s' % restype,
                visible='^.%s?id' % resname)
        top.dataController("FIRE list.%s.reload; FIRE list.%s.new;" % (restype, restype),
                           _fired="^#deleteUserObject.deleted", restype=restype,
                           objtype='=#userobject_dlg.pars.objtype',
                           _if='objtype==restype')
        top.div('^.%s?code' % resname, _class='st_editor_title')
        pane.div(_class='st_editor_body st_editor_%s' % restype, nodeId='%s_root' % restype, datapath=datapath)


class LstQueryHandler(BaseComponent):
    def rpc_getSqlOperators(self):
        result = Bag()
        listop = ('equal', 'startswith', 'wordstart', 'contains', 'startswithchars', 'greater', 'greatereq',
                  'less', 'lesseq', 'between', 'isnull', 'istrue', 'isfalse', 'nullorempty', 'in', 'regex')
        optype_dict = dict(alpha=['contains', 'startswith', 'equal', 'wordstart',
                                  'startswithchars', 'isnull', 'nullorempty', 'in', 'regex',
                                  'greater', 'greatereq', 'less', 'lesseq', 'between'],
                           date=['equal', 'in', 'isnull', 'greater', 'greatereq', 'less', 'lesseq', 'between'],
                           number=['equal', 'greater', 'greatereq', 'less', 'lesseq', 'isnull', 'in'],
                           boolean=['istrue', 'isfalse', 'isnull'],
                           others=['equal', 'greater', 'greatereq', 'less', 'lesseq', 'in'])

        wt = self.db.whereTranslator
        for op in listop:
            result.setItem('op.%s' % op, None, caption='!!%s' % wt.opCaption(op))
        for optype, values in optype_dict.items():
            for operation in values:
                result.setItem('op_spec.%s.%s' % (optype, operation), operation,
                               caption='!!%s' % wt.opCaption(operation))
        customOperatorsHandlers = [(x[12:], getattr(self, x)) for x in dir(self) if x.startswith('customSqlOp_')]
        for optype, handler in customOperatorsHandlers:
            operation, caption = handler(optype_dict=optype_dict)
            result.setItem('op_spec.%s.%s' % (optype, operation), operation, caption=caption)
            result.setItem('op.%s' % operation, None, caption=caption)

        result.setItem('op_spec.unselected_column.x', None, caption='!!Please select the column')

        result.setItem('jc.and', None, caption='!!AND')
        result.setItem('jc.or', None, caption='!!OR')

        result.setItem('not.yes', None, caption='&nbsp;')
        result.setItem('not.not', None, caption='!!NOT')

        return result

    def toolboxQueries(self, container):
        self.savedQueryController(container)
        trpane = container.contentPane(region='center')
        treepane = trpane.div(_class='treeContainer')
        treepane.tree(storepath='list.query.saved_menu', persist=False, inspect='shift',
                      labelAttribute='caption', connect_ondblclick='FIRE list.runQuery = true;',
                      selected_pkey='list.query.selectedId', selected_code='list.query.selectedCode',
                      selectedLabelClass='selectedTreeNode',
                      _class='queryTree',
                      hideValues=True, _reload='^list.query.reload')

    def savedQueryController(self, pane):
        pane.dataRemote('list.query.saved_menu', 'list_query', tbl=self.maintable, cacheTime=3)
        pane.dataRpc('list.query.where', 'load_query', id='^list.query.selectedId', _if='id',
                     _onResult='genro.querybuilder.buildQueryPane();')


