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

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag


class TableHandlerList(BaseComponent):
    js_requires = 'tablehandler/th_script'
    css_requires = 'tablehandler/th_style'

    py_requires = """foundation/includedview:IncludedViewBase,
                     tablehandler/th_extra:QueryHelper,
                     tablehandler/th_core:LstQueryHandler,
                     tablehandler/th_core:TableHandlerCommon"""
                     
    @struct_method
    def th_slotbar_queryfb(self, pane,table=None,**kwargs):
        table = table or self.maintable
        queryfb = pane.formbuilder(cols=5, datapath='.query.where', _class='query_form',
                                   border_spacing='0', onEnter='genro.nodeById(this.getInheritedAttributes().target).publish("runbtn",{"modifiers":null});',
                                   float='left')
        queryfb.div('^.c_0?column_caption', min_width='12em', _class='smallFakeTextBox floatingPopup',
                    nodeId='fastQueryColumn',
                     dropTarget=True,
                    lbl='!!Search',**{'onDrop_gnrdbfld_%s' %table.replace('.','_'):"genro.querybuilder.onChangedQueryColumn(this,data);"})
        optd = queryfb.div(_class='smallFakeTextBox', lbl='!!Op.', lbl_width='4em')

        optd.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                 display='inline-block', width='1.5em', _class='floatingPopup', nodeId='fastQueryNot',
                 border_right='1px solid silver')
        optd.div('^.c_0?op_caption', min_width='7em', nodeId='fastQueryOp', readonly=True,
                 selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                 connectedMenu='==genro.querybuilder.getOpMenuId(_dtype);',
                 action="genro.querybuilder.onChangedQueryOp($2,$1);",
                 _dtype='^.c_0?column_dtype',
                 _class='floatingPopup', display='inline-block', padding_left='2px')
        value_textbox = queryfb.textbox(lbl='!!Value', value='^.c_0', width='12em', lbl_width='5em',
                                        _autoselect=True,
                                        row_class='^.c_0?css_class', position='relative',
                                        disabled='==(_op in genro.querybuilder.helper_op_dict)', _op='^.c_0?op',
                                        validate_onAccept='genro.queryanalyzer.checkQueryLineValue(this,value);',
                                        _class='st_conditionValue')

        value_textbox.div('^.c_0', hidden='==!(_op in genro.querybuilder.helper_op_dict)',
                          connect_onclick="if(GET .c_0?op in genro.querybuilder.helper_op_dict){FIRE list.helper.queryrow='c_0';}",
                          _op='^.c_0?op', _class='helperField')

    def onQueryCalling(self):
        return None
        
    def _th_listController(self,pane,table=None):
        table = table or self.maintable
        pane.data('.baseQuery', self.getQueryBag(table=table))
        pane.dataController("""
                               genro.querybuilder.cleanQueryPane(); 
                               SET .queryRunning = true;
                               var parslist = genro.queryanalyzer.translateQueryPars();
                               if (parslist.length>0){
                                  genro.queryanalyzer.buildParsDialog(parslist);
                               }else{
                                  FIRE .runQueryDo = true;
                               }
                            """,_fired="^.runQuery")
        pane.dataFormula('.currentQueryCountAsString', 'msg.replace("_rec_",cnt)',
                            cnt='^.currentQueryCount', _if='cnt', _else='',
                            msg='!!Current query will return _rec_ items')
        pane.dataController("""SET .currentQueryCountAsString = waitmsg;
                               FIRE .updateCurrentQueryCount;
                                genro.dlg.alert(alertmsg,dlgtitle);
                                  """, _fired="^.showQueryCountDlg", waitmsg='!!Working.....',
                               dlgtitle='!!Current query record count',alertmsg='^.currentQueryCountAsString')
        pane.data('.table',table)
        pane.data('.excludeLogicalDeleted', True)
        pane.data('aux.showDeleted', False)
        pane.dataController(
                """genro.querybuilder = new gnr.GnrQueryBuilder(this,table,"query_root");""" 
                , _init=True,table='=.table')
        pane.dataController(
                """genro.queryanalyzer = new gnr.GnrQueryAnalyzer(this,".runQueryDo","translator_root")"""
                ,_onStart=True)
        pane.dataController("""genro.querybuilder.createMenues();
                                  dijit.byId('qb_fields_menu').bindDomNode(genro.domById('fastQueryColumn'));
                                  dijit.byId('qb_not_menu').bindDomNode(genro.domById('fastQueryNot'));
                                  genro.querybuilder.buildQueryPane();""", _onStart=True)

    def rpc_fieldExplorer(self, table=None, omit=None):
        result = self.rpc_relationExplorer(table=table, omit=omit)
        if hasattr(self,'customQuery_'):
            customQuery = self._th_listCustomCbBag('customQuery_')
            if customQuery:
                result.addItem('-', None)
                #mettere customQuery dentro result in modo opportuno
                for cq in customQuery:
                    result.addItem(cq.label, None, caption=cq.attr['caption'],
                                   action='SET list.selectmethod= $1.fullpath; FIRE list.runQuery;')

        result.addItem('-', None)
        jsresolver = "genro.rpc.remoteResolver('getQuickQuery',null,{cacheTime:'5'})"
        result.addItem('custquery', jsresolver, _T='JS', caption='!!Custom query',
                       action='FIRE list.query_id = $1.pkey;')
        return result


    def getQueryBag(self,table=None):
        table = table or self.maintable
        tblobj = self.db.table(table)
        result = Bag()
        querybase = self.queryBase()
        op_not = querybase.get('op_not', 'yes')
        column = querybase.get('column')
        column_dtype = None
        if column:
            column_dtype = tblobj.column(column).getAttr('dtype')
        not_caption = '&nbsp;' if op_not == 'yes' else '!!not'
        result.setItem('c_0', querybase.get('val'),
                       {'op': querybase.get('op'), 'column': column,
                        'op_caption': '!!%s' % self.db.whereTranslator.opCaption(querybase.get('op')),
                        'not': op_not, 'not_caption': not_caption,
                        'column_dtype': column_dtype,
                        'column_caption': self.app._relPathToCaption(table, column)})
        return result

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fields(self.columnsBase())
        return struct
        
    def columnsBase(self):
        return ''

    def orderBase(self):
        return ''
        
    def conditionBase(self):
        return (None, None)
        
        
    def queryBase(self):
        return dict()
        
    def enableFilter(self):
        #to deprecate
        return True

    def tableRecordCount(self):
        """redefine to avoid the count query"""
        return True

class TableHandlerListBase(TableHandlerList):
    @struct_method
    def th_listPage(self,pane,table=None,frameCode=None,linkedForm=None,**kwargs):
        #self.query_helper_main(pane)
        frame = pane.framePane(frameCode=frameCode,childname='list',datapath='.list',table=table,linkedForm=linkedForm,**kwargs)
        frame.data('.table',table=table)
        self._th_listController(frame,table=table)
        frame.top.listToolbar(table)
        footer = frame.bottom.slotToolbar('*,th_dock')
        footer.th_dock.div(width='100px',height='20px').dock(id='th_dock')
        pane.palettePane('_queryTool',title='Query tool',nodeId='query_root',
                        dockTo='th_dock',datapath='.list.query.where',height='150px',width='400px')
        frame.gridPane(table=table,linkedForm=linkedForm)
        return frame
    
    @struct_method
    def th_listToolbar(self,pane,table=None):
        toolbar = pane.slotToolbar('queryfb,iv_runbtn,*,iv_add,iv_del,list_locker',queryfb_table=table)
    
    
    @struct_method
    def th_slotbar_list_locker(self, pane,**kwargs):
        pane.button('!!Locker',width='20px',iconClass='icnBaseUnlocked',showLabel=False,
                    action='genro.formById("formPane").publish("setLocked","toggle");',
                    subscribe_form_formPane_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'icnBaseLocked':'icnBaseUnlocked');""")
    @struct_method
    def th_gridPane(self, pane,table=None,linkedForm=None):
        table = table or self.maintable
        pane.data('.sorted', self.orderBase())
        condition = self.conditionBase()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        pane.dataController("""
        var columns = gnr.columnsFromStruct(struct);
        if(hiddencolumns){
            var hiddencolumns = hiddencolumns.split(',');
            columns = columns+','+hiddencolumns;
        }
        
        SET .columns = columns;
        """, hiddencolumns=self.hiddencolumnsBase(),
                            struct='^list.view.structure', _init=True)

        pane.data('.tableRecordCount', self.tableRecordCount())

        iv = pane.includedView(autoWidth=False,datapath=False,selectedId='.selectedId',
                                rowsPerPage=self.rowsPerPage(), sortedBy='^.sorted',
                                 _newGrid=True,
                                 linkedForm=linkedForm, loadFormEvent='onRowDblClick', dropTypes=None,
                                 dropTarget=True,
                                 draggable=True, draggable_row=True,
                                 struct=self.lstBase,
                                 dragClass='draggedItem',
                                 onDrop=""" for (var k in data){
                                                 this.setRelativeData('list.external_drag.'+k,new gnr.GnrBag(data[k]));
                                              }""",
                                selfsubscribe_runbtn="""
                                                        if($1.modifiers=='Shift'){
                                                            FIRE .showQueryCountDlg;
                                                         }else{
                                                            FIRE .runQuery;
                                                         }""")
                             
        store = iv.selectionStore(table=table, columns='=.columns',
                           chunkSize=self.rowsPerPage()*4,
                           where='=.query.where', sortedBy='=.sorted',
                           pkeys='=.query.pkeys', _fired='^.runQueryDo',
                           selectionName='*', recordResolver=False, condition=condition,
                           sqlContextName='standard_list', totalRowCount='=.tableRecordCount',
                           row_start='0', externalChanges=True,
                           excludeLogicalDeleted='^.excludeLogicalDeleted',
                           applymethod='onLoadingSelection',
                           timeout=180000, selectmethod='=.selectmethod',
                           selectmethod_prefix='customQuery',
                           _onCalling=self.onQueryCalling(),
                           **condPars)
                           
        store.addCallback('FIRE .queryEnd=true; SET .selectmethod=null; return result;')
        pane.dataRpc('.currentQueryCount', 'app.getRecordCount', condition=condition,
                     fired='^.updateCurrentQueryCount',
                     table='.table', where='=.query.where',
                     excludeLogicalDeleted='=.excludeLogicalDeleted',
                     **condPars)
        pane.dataController("""this.setRelativeData(".query.where",baseQuery.deepCopy(),{objtype:"query", tbl:maintable});
                               genro.querybuilder.buildQueryPane(); 
                               SET .view.selectedId = null;
                               if(!fired&&runOnStart){
                                    FIRE .runQuery
                               }
                            """,
                            _onStart=True, baseQuery='=.baseQuery', maintable='=.table',
                            fired='^.query.new',
                            runOnStart=self.queryBase().get('runOnStart', False))
