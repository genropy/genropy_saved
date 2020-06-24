# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent

from gnr.core.gnrdecorator import public_method

from gnr.web.gnrwebstruct import struct_method

class UserObjectEditor(BaseComponent):
    def _wherePaneConfig(self,bc,table=None,frame=None):
        querypane = bc.contentPane(query_table=table,
                        onCreated="this.querymanager = new gnr.FakeTableHandler(this);",
                        nodeId='{frameCode}_query'.format(frameCode=frame.attributes['frameCode']),
                        margin='2px',region='center')   
        bc.dataController("""if(_reason=='node'){
                                querypane.querymanager.createQueryPane();
                            }""",
                        querypane=querypane,where='^.query')
        fb = bc.contentPane(region='bottom',datapath='.query').formbuilder()
        right = bc.roundedGroupFrame(region='right',width='50%',datapath='.query',title='!!Order by and limit')
        right.bottom.formbuilder().numberTextBox('^.limit',lbl='Limit',width='5em')
        grid = right.quickGrid(value='^.customOrderBy',
                                dropTarget_grid='gridcolumn',
                                 onDrop_gridcolumn="""
                                 function(p1,p2,kw){
                                     this.widget.addBagRow('#id', '*', this.widget.newBagRow({'fieldpath':kw.data.field,'field':kw.data.original_field,
                                                                    group_aggr:kw.data.group_aggr,sorting:true}));
                                 }
                                 """)
        grid.column('field',name='!!Column',width='30em')
        grid.column('group_aggr',name='!!Aggr',width='5em')
        grid.column('sorting',name='!!Aggr',dtype='B',format_trueclass='iconbox arrow_up',format_falseclass="iconbox arrow_down",
                    format_onclick="""var r = this.widget.storebag().getItem("#"+$1.rowIndex);
                                      r.setItem("sorting",!r.getItem("sorting"));""",width='3em')
        grid.column('delrow',width='3em',
                    format_isbutton=True,
                    format_onclick='this.widget.storebag().popNode("#"+$1.rowIndex);',
                    format_buttonclass='iconbox qb_del')


class GroupByEditor(UserObjectEditor):
    py_requires='public:Public,th/th'

    @struct_method
    def uo_groupByEditor(self,pane,table=None,userobject_id=None,from_table=None,
                         datapath=None,frameCode=None,**kwargs):        
        frameCode= frameCode or '{}_th_groupby_maker'.format(table.replace('.','_'))
        datapath = datapath or '.{frameCode}'.format(frameCode=frameCode)
        mainframe = pane.framePane(frameCode=frameCode,datapath=datapath,**kwargs)
        objtype = 'group_by_stat'
        mainframe.top.userObjectBar(table=table,objtype=objtype,
                                source_where='=.gth.query.where',
                                source_groupLimit='=.gth.query.limit',
                                source_groupOrderBy='=.gth.query.customOrderBy',
                                source_joinConditions='=.gth.query.joinConditions',
                                source_groupByStruct='=.gth.grid.struct',
                                source_groupMode='=.gth.groupMode',
                                source_treeRootName='=.gth.treeRootName',
                                source_output='=.gth.output',
                                source_queryPars='=.gth.queryPars',
                                mainIdentifier=frameCode)
        bc = mainframe.center.borderContainer()
        thframecode = '{}_gth'.format(frameCode)
        frame = bc.contentPane(region='center').groupByTableHandler(table=table,frameCode=thframecode,
                                    configurable=True,
                                    where='=.query.where',
                                    store_joinConditions='=.query.joinConditions',
                                    store_groupLimit ='=.query.limit',
                                    store_groupOrderBy ='=.query.customOrderBy',
                                    store__fired='^.runQueryDo',
                                    datapath='.gth')
        bar = frame.top.bar.replaceSlots('#','5,ctitle,stackButtons,10,groupByModeSelector,counterCol,*,runGroupBy,configuratorPalette,10,searchOn,count,10,export,5')
        bar.runGroupBy.slotButton(iconClass='iconbox run',
                                    action="TH('{frameCode}_query').querymanager.onQueryCalling(querybag);".format(frameCode=thframecode),
                                    _shortcut='@run:enter',
                                    querybag='=.query.where') 
        frame.data('.always',True)
        top = bc.tabContainer(region='top',height='200px',closable=True,margin='2px',splitter=True)
        self._wherePaneConfig(top.borderContainer(title='!!Where',datapath='.gth'),table=table,frame=frame)
        onCreated="""var that = this;
                var queryCode = '%s_query';
                this.watch('waitingFakeTH',function(){
                    return TH(queryCode); 
                },function(){
                    that.freeze();
                    TH(queryCode).querymanager.joinConditions(that);
                    that.unfreeze(true);
                })
                """ %thframecode
        top.contentPane(title='!!Join conditions',datapath='.query',_lazyBuild=True,
                        onCreated=onCreated)

        if not userobject_id and from_table:
            fieldpath = None
            if table != from_table:
                relpars = self.th_searchRelationPath(table=from_table,destTable=table)
                if len(relpars['relpathlist'])==1:
                    fieldpath = relpars['relpathlist'][0]
            else:
                fieldpath = self.db.table(table).pkey
            if fieldpath:
                queryBag = self.th_prepareQueryBag(dict(column=fieldpath.replace('$',''),op='equal',val='?%s' %from_table.split('.')[1]),table=table)
            else:
                queryBag = self.th_prepareQueryBag(dict(column=self.db.table(table).pkey,op='equal',val=''),table=table)
            frame.data('.gth.query.where',queryBag)

class PrintGridEditor(UserObjectEditor):
    @struct_method
    def uo_printGridEditor(self,parent,frameCode=None,table=None,parentTH=None,
                            defaultStruct=None,defaultWherebag=None,**kwargs):
        frame = parent.framePane(frameCode=frameCode,**kwargs)
        frame.top.userObjectBar(table=table,objtype='gridprint',
                source_viewerStruct='=.viewer.grid.struct',
                source_struct='=.viewer.exportStruct',
                source_query='=.viewer.query',
                source_printParams='=.printParams',
                source_queryPars='=.viewer.queryPars',
                default_viewerStruct='=.viewer.defaultStruct',
                mainIdentifier=frameCode)   
        defaultStruct = defaultStruct or self._getDefaultStruct(table=table) 
        frame.data('.viewer.grid.struct',defaultStruct)
        frame.data('.viewer.defaultStruct',defaultStruct)
        frame.data('.viewer.query.where',defaultWherebag)
        if parentTH:
            frame.dataController("""
            SET .viewer.query = TH(parentTH).querymanager.prepareQueryData();
            let grid = genro.wdgById(`${parentTH}_grid`);
            SET .viewer.grid.struct = grid.structBag.deepCopy();
            SET .viewer.defaultStruct = grid.structBag.deepCopy();
            """,_onBuilt=100,parentTH=parentTH)

        center = frame.center.borderContainer(design='sidebar')
        framegrid = self._buildPrintEditor_view(center,table=table)
        gridId = framegrid.grid.attributes['nodeId']
        bar = framegrid.top.bar.replaceSlots('configuratorPalette','qpalette,configuratorPalette')
        palette = bar.qpalette.palettePane(paletteCode='{}_pl'.format(gridId),
                                            title='Query',datapath='#{}.#parent'.format(gridId),
                                        palette_height='300px',palette_width='750px',
                                        dockButton=dict(iconClass='iconbox menubox magnifier'))
        self._wherePaneConfig(palette.borderContainer(),table=table,frame=framegrid)
        #self._printOptionsForm(parametersTab.contentPane(region='center'))
        bar = frame.bottom.slotBar('*,doPrint,2',margin_bottom='2px',_class='slotbar_dialog_footer')  
        bar.doPrint.slotButton('!!Print',action="""
                             var parameters = {'table':table,
                                                'respath':'html_res/print_gridres',
                                                'pdf':true,
                                                'currentGridStruct':currentGridStruct,
                                                'currentQuery':currentQuery,
                                                'printParams':printParams,
                                                'pkey':'*',
                                                'record':'*'
                                                }
                             genro.rpcDownload("callTableScript",parameters,'print');
                    """,currentGridStruct='=.viewer.exportStruct',
                            currentQuery='=.viewer.query',
                            printParams='=.printParams',
                        table=table)
                
    def _getDefaultStruct(self,table=None):
        struct = self.newGridStruct(table)
        tblobj = self.db.table(table)
        r = struct.view().rows()
        if tblobj.attributes.get('caption_field'):
            r.fieldcell(tblobj.attributes.get('caption_field'))
        else:
            r.fieldcell(tblobj.pkey)

    def _printOptionsForm(self,pane):
        pass

    def _buildPrintEditor_view(self,bc,table=None):
        top = bc.contentPane(region='top',height='50%',splitter=True,closable=True)
        frame = top.frameGrid(structpath='.struct',
                            grid_configurable=True,
                            grid_selfsubscribe_runbtn="FIRE .doQuery;",
                            datapath='.viewer',margin='4px',
                            grid_externalSave=True,
                            _newGrid=True,
                            rounded=6,border='1px solid silver')
        gridattr = frame.grid.attributes
        configuratorId = '{}_configurator'.format(gridattr['nodeId'])
        gridattr['configuratorId'] = configuratorId
        frame.dataController("""FIRE .runQueryDo;
                                SET .exportStruct = grid.getExportStruct();
                                """,
                            grid=frame.grid.js_widget,
                            struct='^.grid.struct',_delay=100)

        right = bc.framePane(region='right',width='200px',border_left='1px solid silver')

        right.center.contentPane(nodeId=configuratorId).fieldsTree(table=table,checkPermissions=True,searchOn=True,
                            box_top='0',box_bottom='0',box_left='0',box_right='0',box_position='absolute',
                            top='0',bottom='0',left='0',right='0',position='absolute',
                            box_datapath='._confFieldsTree',
                            searchMode='static',
                            searchOn_searchCode='{}_fieldsTree'.format(frame.attributes['frameCode']),
                            trash=True)
        right.bottom.slotToolbar('*,fbpar,3').fbpar.formbuilder(border_spacing='2px').numberTextBox(value='^.viewer.previewLimit',
                                                    width='4em',lbl='!!Preview limit',default=300)
        bar = frame.top.slotToolbar('2,printParams,*,configuratorPalette,10,runPrint,2')
        printparams = bar.printParams.div(datapath='.#parent.printParams',
                                        _class='popupLabel',font_weight='bold',
                                        color='#666',cursor='pointer')
        printparams.div('^.print_title?=#v?#v:"Missing title"')
        self._printParamsFb(printparams.tooltipPane())
        bar.runPrint.slotButton(iconClass='iconbox run',
                            action="TH('{frameCode}_query').querymanager.onQueryCalling(querybag);".format(frameCode=frame.attributes['frameCode']),
                            _shortcut='@run:enter',
                            querybag='=.query.where') 
        bar.dataController("SET .queryPars = TH(`${frameCode}_query`).querymanager.queryParsBag()",
                            frameCode=frame.attributes['frameCode'],
                            _fired='^.query.where',_delay=500)


        frame.grid.selectionStore(table=table,
                            where='=.query.where',
                               queryMode='=.query.queryMode', 
                               sortedBy='=.grid.sorted',
                               customOrderBy='=.query.customOrderBy',
                               multiStores='=.query.multiStores',
                               pkeys='=.query.pkeys', 
                               _cleared='^.clearStore',
                               _onError="""return error;""", 
                               recordResolver=False, 
                               row_start='0',
                               filteringPkeys='=.query.queryAttributes.filteringPkeys',
                               currentFilter = '=.query.currentFilter',
                               prevSelectedDict = '=.query.prevSelectedDict',
                               queryExtraPars='=.query.extraPars',
                               joinConditions='=.query.joinConditions',
                               limit='^.previewLimit',
                            _doRun='^.runQueryDo')
        tc = bc.tabContainer(margin='2px',region='center')
        tc.contentPane(title='HTML',background='white'
                        ).documentFrame(resource='{table}:html_res/print_gridres'.format(table=table),
                                pkey='*',html=True,
                                currentGridStruct='=.viewer.exportStruct',
                                currentQuery='=.viewer.query',
                                page_debug='#efefef',
                                previewLimit='^.viewer.previewLimit',
                                printParams='^.printParams',
                                httpMethod='POST',
                                _fired='^.viewer.runQueryDo',
                                _if='currentGridStruct',
                        _delay=1000)
        tc.contentPane(title='PDF',background='white'
                        ).documentFrame(resource='{table}:html_res/print_gridres'.format(table=table),
                                pkey='*',html=False,
                                httpMethod='POST',
                                currentGridStruct='=.viewer.exportStruct',
                                currentQuery='=.viewer.query',
                                previewLimit='^.viewer.previewLimit',
                                printParams='^.printParams',
                                _fired='^.viewer.runQueryDo',
                                _if='currentGridStruct',
                        _delay=1000)
        return frame


    def _printParamsFb(self,pane):
        box = pane.div(font_size='.9em',color='#666')
        box.div('!!Edit print parameters',_class='commonTitleBar')
        pane = box.div(padding='10px')
        fb = pane.formbuilder()
        fb.textbox(value='^.print_title',lbl='!!Title')
        fb.filteringSelect(value='^.orientation',lbl='!!Orientation',values='H:Horizontal,V:Vertical')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.letterhead_id',
                    lbl='!!Letterhead',hasDownArrow=True)
        fb.filteringSelect(value='^.totalize_mode', lbl='!!Totalize',values='doc:Document,page:Page')
        fb.textbox(value='^.totalize_carry',lbl='!!Carry caption',hidden='^.totalize_mode?=#v!="page"')
        fb.textbox(value='^.totalize_footer',lbl='!!Totals caption',hidden='^.totalize_mode?=!#v')
        fb.checkbox(value='^.allow_only_saved_query',label='!!Allow only saved query')
