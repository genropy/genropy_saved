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
        tablecode = table.replace('.','_')
        mangler = pane.getInheritedAttributes()['th_root']
        queryfb = pane.formbuilder(cols=5, datapath='.query.where', _class='query_form',
                                   border_spacing='0', onEnter='genro.nodeById(this.getInheritedAttributes().target).publish("runbtn",{"modifiers":null});',
                                   float='left')
        queryfb.div('^.c_0?column_caption', min_width='12em', _class='smallFakeTextBox floatingPopup',
                    nodeId='%s_fastQueryColumn' %mangler,
                     dropTarget=True,
                    lbl='!!Search',**{str('onDrop_gnrdbfld_%s' %table.replace('.','_')):"genro.querybuilder('%s').onChangedQueryColumn(this,data);" %mangler})
        optd = queryfb.div(_class='smallFakeTextBox', lbl='!!Op.', lbl_width='4em')

        optd.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                 display='inline-block', width='1.5em', _class='floatingPopup', nodeId='%s_fastQueryNot' %mangler,
                 border_right='1px solid silver')
        optd.div('^.c_0?op_caption', min_width='7em', nodeId='%s_fastQueryOp' %mangler, readonly=True,
                 selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                 connectedMenu='==genro.querybuilder("%s").getOpMenuId(_dtype);' %mangler,
                 action="genro.querybuilder('%s').onChangedQueryOp($2,$1);" %mangler,
                 _dtype='^.c_0?column_dtype',
                 _class='floatingPopup', display='inline-block', padding_left='2px')
        value_textbox = queryfb.textbox(lbl='!!Value', value='^.c_0', width='12em', lbl_width='5em',
                                        _autoselect=True,
                                        row_class='^.c_0?css_class', position='relative',
                                        disabled='==(_op in genro.querybuilder("%s").helper_op_dict)'  %mangler, _op='^.c_0?op',
                                        validate_onAccept='genro.queryanalyzer("%s").checkQueryLineValue(this,value);' %mangler,
                                        _class='st_conditionValue')

        value_textbox.div('^.c_0', hidden='==!(_op in  genro.querybuilder("%s").helper_op_dict)' %mangler,
                          connect_onclick="if(GET .c_0?op in genro.querybuilder('%s').helper_op_dict){FIRE .#parent.#parent.helper.queryrow='c_0';}" %mangler,
                          _op='^.c_0?op', _class='helperField')

    def onQueryCalling(self):
        return None
        
    def _th_listController(self,pane,table=None):
        table = table or self.maintable
        mangler = pane.attributes['th_root']
        pane.data('.table',table)
        pane.data('.excludeLogicalDeleted', True)
        pane.data('.showDeleted', False)
        pane.dataController(
                """this._querybuilder = new gnr.GnrQueryBuilder(this,table,"query_root");
                   var qb = this._querybuilder;
                   this._queryanalyzer = new gnr.GnrQueryAnalyzer(this,table);
                """ 
                , _init=True,table=table,nodeId='%s_queryscripts' %mangler)

    def _th_queryToolController(self,pane,table=None):
        mangler = pane.attributes['th_root']
        pane.dataController("""
                               genro.querybuilder(mangler).cleanQueryPane(); 
                               SET .queryRunning = true;
                               var parslist = genro.queryanalyzer(mangler).translateQueryPars();
                               if (parslist.length>0){
                                  genro.queryanalyzer(mangler).buildParsDialog(parslist);
                               }else{
                                  FIRE .runQueryDo = true;
                               }
                            """,mangler=mangler,_fired="^.runQuery")
        pane.dataFormula('.currentQueryCountAsString', 'msg.replace("_rec_",cnt)',
                            cnt='^.currentQueryCount', _if='cnt', _else='',
                            msg='!!Current query will return _rec_ items')
        pane.dataController("""SET .currentQueryCountAsString = waitmsg;
                               FIRE .updateCurrentQueryCount;
                                genro.dlg.alert(alertmsg,dlgtitle);
                                  """, _fired="^.showQueryCountDlg", waitmsg='!!Working.....',
                               dlgtitle='!!Current query record count',alertmsg='^.currentQueryCountAsString')
        pane.dataController("""
                    var qb = genro.querybuilder(mangler);
                    qb.createMenues();
                    dijit.byId(qb.relativeId('qb_fields_menu')).bindDomNode(genro.domById(qb.relativeId('fastQueryColumn')));
                    dijit.byId(qb.relativeId('qb_not_menu')).bindDomNode(genro.domById(qb.relativeId('fastQueryNot')));
                    qb.buildQueryPane();
        """,_onStart=True,mangler=mangler)

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


    def _prepareQueryBag(self,querybase,table=None):
        result = Bag()
        if not querybase:
            return result
        table = table or self.maintable
        tblobj = self.db.table(table)
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
    def th_listPage(self,pane,table=None,th_pkey=None,frameCode=None,reloader=None,virtualStore=None,
                        tbar_add=False,tbar_del=False,tbar_locker=False,**kwargs):
        #self.query_helper_main(pane)
        frame = pane.framePane(frameCode=frameCode,childname='list',datapath='.list',center_overflow='hidden',**kwargs)
        mangler =frameCode
        frame.data('.table',table=table)
        queryTool = kwargs['queryTool'] if 'queryTool' in kwargs else virtualStore
        self._th_listController(frame,table=table)
        slots = []
        slotbarKw = dict()
        if queryTool:
            slots = ['queryfb','iv_runbtn','5','|','queryTool','*','count','5']
            slotbarKw['queryfb_table'] = table
            self._th_queryToolController(frame,table=table)
        else:
            slots['*','searchOn','count','10']
        if tbar_add:
            slots.append('iv_add')
            slotbarKw['iv_add_parentForm'] = True
        if tbar_del:
            slots.append('iv_del')
            slotbarKw['iv_del_parentForm'] = True
        if tbar_locker:
            slots.append('list_locker')
        frame.top.slotToolbar(','.join(slots),**slotbarKw)            
        frame.gridPane(table=table,reloader=reloader,th_pkey=th_pkey,virtualStore=virtualStore)
        return frame
        
    @struct_method
    def th_slotbar_queryTool(self,pane,**kwargs):
       # pane = pane.div(width='20px',height='16px',_class='icnBaseLens hiddenDock')
        mangler = pane.getInheritedAttributes()['th_root']
        pane.palettePane('%s_queryTool' %mangler,title='Query tool',nodeId='%s_query_root' %mangler,
                        dockButton_iconClass='icnBaseLens',
                        datapath='.query.where',height='150px',width='400px')
    
    @struct_method
    def th_slotbar_list_locker(self, pane,**kwargs):
        pane.button('!!Locker',width='20px',iconClass='icnBaseUnlocked',showLabel=False,
                    action='genro.formById("formPane").publish("setLocked","toggle");',
                    subscribe_form_formPane_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'icnBaseLocked':'icnBaseUnlocked');""")
    @struct_method
    def th_gridPane(self, pane,table=None,reloader=None,th_pkey=None,virtualStore=None):
        table = table or self.maintable
        mangler = pane.getInheritedAttributes()['th_root']
        order_by=self._th_hook('order',mangler=mangler)()
        pane.data('.sorted',order_by)
        condition = self._th_hook('condition',mangler=mangler)()
        
        if th_pkey:
            querybase = dict(column=self.db.table(table).pkey,op='equal',val=th_pkey,runOnStart=True)
        else:
            querybase = self._th_hook('query',mangler=mangler)() or dict()
        queryBag = self._prepareQueryBag(querybase,table=table)
        pane.data('.baseQuery', queryBag)

        condPars = {}
        if isinstance(condition,dict):
            condPars = condition
            condition = condPars.pop('condition')
        elif condition:
            condPars = condition[1] or {}
            condition = condition[0]
            
        pane.dataController("""
        var columns = gnr.columnsFromStruct(struct);
        if(hiddencolumns){
            var hiddencolumns = hiddencolumns.split(',');
            columns = columns+','+hiddencolumns;
        }
        
        SET .columns = columns;
        """, hiddencolumns=self._th_hook('hiddencolumns',mangler=mangler)(),
                            struct='^.view.structure', _init=True)

        pane.data('.tableRecordCount', self.tableRecordCount())

        iv = pane.includedView(autoWidth=False,datapath=False,selectedId='.selectedId',
                                rowsPerPage=self.rowsPerPage(), sortedBy='^.sorted',
                                 _newGrid=True,
                                 dropTypes=None,
                                 dropTarget=True,
                                 draggable=True, draggable_row=True,
                                 struct=self._th_hook('struct',mangler=mangler),
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
        chunkSize=self.rowsPerPage()*4   if virtualStore else None          
        store = iv.selectionStore(table=table, columns='=.columns',
                               chunkSize=chunkSize,childname='store',
                               where='=.query.where', sortedBy='=.sorted',
                               pkeys='=.query.pkeys', _fired='^.runQueryDo',
                               selectionName='*%s' %mangler, recordResolver=False, condition=condition,
                               sqlContextName='standard_list', totalRowCount='=.tableRecordCount',
                               row_start='0', externalChanges=True,
                               excludeLogicalDeleted='^.excludeLogicalDeleted',
                               applymethod='onLoadingSelection',
                               timeout=180000, selectmethod='=.selectmethod',
                               selectmethod_prefix='customQuery',
                               _onCalling=self.onQueryCalling(),
                               _reloader=reloader,**condPars)
        store.addCallback('FIRE .queryEnd=true; SET .selectmethod=null; return result;')        
        pane.dataRpc('.currentQueryCount', 'app.getRecordCount', condition=condition,
                     fired='^.updateCurrentQueryCount',
                     table=table, where='=.query.where',
                     excludeLogicalDeleted='=.excludeLogicalDeleted',
                     **condPars)
        
        pane.dataController("""
                               SET .view.selectedId = null;
                               FIRE .query.new;
                               if(runOnStart){
                                    FIRE .runQuery;
                               }
                            """,
                            _onStart=True,
                            runOnStart=querybase.get('runOnStart', False))
        pane.dataController("""
            this.setRelativeData(".query.where",baseQuery.deepCopy(),{objtype:"query", tbl:maintable});
            genro.querybuilder(mangler).buildQueryPane(); 
        """,_fired='^.query.new',baseQuery='=.baseQuery', maintable=table,mangler=mangler)
