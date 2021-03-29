# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari
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


from gnrpkg.biz.dashboard import BaseDashboardItem
from gnr.core.gnrdecorator import public_method

caption = 'Stats Grouped'
description = 'Stats Grouped'
objtype = 'dash_groupby'
 
class Main(BaseDashboardItem):
    """Choose table and saved stat"""
    item_name = 'Stats Grouped'
    title_template = '$title $whereParsFormatted'
    linked_item = dict(_class='line_chart_white_svg',

                    tip='!!Drag on an empty tile to make a chart',
                    onDrag="""
                    var linkedGrid = genro.getData(dragInfo.sourceNode.attr.workpath+'.currentLinkableGrid');
                    var linkedItem = dragInfo.sourceNode.getRelativeData('.itemIdentifier');
                    dragValues.dashboardUserObjectItems = {fixedParameters:{'linkedGrid':linkedGrid,title:'Chart #',linkedItem:linkedItem},
                                                    objtype:'_groupby_chart',
                                                    caption:_T('Linked chart')};
                    """)

    def content(self,pane,table=None,userobject_id=None,**kwargs):
        self.page.mixinComponent('th/th:TableHandler')
        bc = pane.borderContainer()
        center = bc.contentPane(region='center',_class='hideInnerToolbars')
        frameCode = self.itemIdentifier
        data,metadata = self.page.db.table('adm.userobject').loadUserObject(id=userobject_id)
        frame = center.groupByTableHandler(table=table,frameCode=frameCode,
                                    configurable=False,
                                    struct=data['groupByStruct'],
                                    where='=.query.where',
                                    store_joinConditions='=.query.joinConditions',
                                    store_groupLimit ='=.query.limit',
                                    store_groupOrderBy ='=.query.customOrderBy',
                                    store__fired='^.runStore',
                                    datapath=self.workpath)

        frame.grid.attributes['configurable'] = True #no full configurator but allow selfdragging cols
        frame.stackedView.grid.attributes['configurable'] = True #no full configurator but allow selfdragging cols
        self.content_handleQueryPars(frame)
        bc.dataFormula('.currentLinkableGrid','itemIdentifier+(groupMode=="stackedview"?"_stacked_grid":"_grid");',datapath=self.workpath,
                            groupMode='^.groupMode',itemIdentifier=self.itemIdentifier)
        self.queryPars = data['queryPars']
        frame.data('.always',True)
        frame.data('.query.where',data['where'])
        frame.data('.query.limit',data['groupLimit'])
        frame.data('.query.customOrderBy',data['groupOrderBy'])
        frame.data('.query.queryPars',data['queryPars'])
        frame.data('.query.joinConditions',data['joinConditions'])

        center.dataController("""
            viewMode = viewMode || defaultGroupMode+'_'+defaultOutput;
            genro.nodeById(frameCode).publish('viewMode',viewMode);
        """,viewMode='^.conf.viewMode',
        defaultOutput= data['output'],frameCode=frameCode,
        defaultGroupMode = data['groupMode'],
        _fired='^%s.runItem' %self.workpath)
        center.data('.conf.treeRootName',data['treeRootName'])
        center.dataFormula('%s.treeRootName' %self.workpath,'confRootName',confRootName='^.conf.treeRootName',_onBuilt=True)

    def configuration(self,pane,table=None,userobject_id=None,**kwargs):
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').div(padding='10px').formbuilder()
        fb.filteringSelect(value='^.viewMode',lbl='Mode',
                            values='flatview_grid:Flat grid,stackedview_grid:Stacked view,flatview_tree:Tree,stackedview_tree:Stacked tree')
        fb.textBox(value='^.treeRootName',
                    hidden='^%s.viewMode?=#v?#v.endsWith("_grid"):false' %self.workpath,lbl='!!Tree root label')
        center = bc.contentPane(region='center')
        if not self.queryPars:
            return
        self.configuration_handleQueryPars(center,table)


    def getDashboardItemInfo(self,table=None,userObjectData=None,**kwargs):
        result = []
        where = userObjectData['where']
        struct = userObjectData['groupByStruct']
        if struct:
            z = [self.localize(n.attr.get('name')) for n in struct['view_0.rows_0'].nodes if not n.attr.get('hidden')]
            result.append('<div class="di_pr_subcaption" >Fields</div><div class="di_content">%s</div>' %','.join(z))
        if where:
            result.append('<div class="di_pr_subcaption">Where</div><div class="di_content">%s</div>' %self.db.table(table).whereTranslator.toHtml(self.db.table(table),where))
        
        queryPars = userObjectData['queryPars']
        configurations = []
        configurations.append('Mode')
        if queryPars:
            for code,pars in queryPars.digest('#k,#a'):
                autoTopic = False
                if not code.endswith('*'):
                    configurations.append(code)
        result.append('<div class="di_pr_subcaption">Config</div><div class="di_content">%s</div>' %'<br/>'.join(configurations))

        return ''.join(result)

    
    def itemActionsSlot(self,pane):
        pane.lightbutton(_class='excel_white_svg',
                        action="""
                        var opt = objectExtract(_kwargs,'opt_*');
                        var kw = {command:'export',opt:opt};
                        var gridId = itemIdentifier+(groupMode=='stackedview'?'_stacked_grid':'_grid');
                        genro.nodeById(gridId).publish('serverAction',kw)""",
                        groupMode='=.groupMode' ,datapath=self.workpath,
                        itemIdentifier=self.itemIdentifier,height='16px',width='16px',
                        opt_export_mode='xls',
                        opt_downloadAs='=.current_title?=#v?flattenString(#v,[".",":","/",";"," "]).toLowerCase():""',
                        opt_rawData=True, 
                        opt_localized_data=True,
                        ask=dict(title='Export selection',skipOn='Shift',
                                fields=[dict(name='opt_downloadAs',lbl='Download as'),
                                        dict(name='opt_export_mode',wdg='filteringSelect',values='xls:Excel,csv:CSV',lbl='Mode'),
                                        dict(name='opt_allRows',label='All rows',wdg='checkbox'),
                                        dict(name='opt_localized_data',wdg='checkbox',label='Localized data')]),
                        cursor='pointer')


    @public_method
    def di_userObjectEditor(self,pane,table=None,userobject_id=None,from_table=None,from_pkey=None,**kwargs):        
        bc = pane.borderContainer()
        frame = bc.contentPane(region='center').groupByTableHandler(table=table,frameCode='th_groupby_maker',
                                    configurable=True,
                                    where='=.query.where',
                                    store_joinConditions='=.query.joinConditions',
                                    store_groupLimit ='=.query.limit',
                                    store_groupOrderBy ='=.query.customOrderBy',
                                    store__fired='^.runQueryDo',
                                    datapath='main')
        bar = frame.top.bar.replaceSlots('#','5,ctitle,stackButtons,10,groupByModeSelector,counterCol,*,runGroupBy,configuratorPalette,10,searchOn,count,10,export,5')
        bar.runGroupBy.slotButton(iconClass='iconbox run',
                                    action="TH('th_groupby_maker_query').querymanager.onQueryCalling(querybag);",
                                    _shortcut='@run:enter',
                                    querybag='=main.query.where') 
        frame.data('.always',True)
        top = bc.tabContainer(region='top',height='200px',closable=True,margin='2px',splitter=True)
        self._wherePaneConfig(top.borderContainer(title='!!Where'),table=table,frame=frame)
        top.contentPane(title='!!Join conditions',datapath='.query',_lazyBuild=True,
                        onCreated="""
                        var that = this;
                        this.watch('waitingFakeTH',function(){
                            return TH('th_groupby_maker_query');
                        },function(){
                            that.freeze();
                            TH('th_groupby_maker_query').querymanager.joinConditions(that);
                            that.unfreeze(true);
                        })
                        """)
        frame.dataController("genro.nodeById('th_groupby_maker').publish('loadDashboard',{pkey:userobject_id})",_onStart=True,
                                    userobject_id=userobject_id,
                                    _if='userobject_id')
        frame.dataController("""
        var gth = genro.nodeById('th_groupby_maker');
        if(!pkey){
            gth.setRelativeData('.dashboardMeta.code','__'+genro.time36Id());
            gth.setRelativeData('.dashboardMeta.objtype',objtype);
            gth.setRelativeData('.dashboardMeta.tbl',table);
            
        }
        gth.publish('saveDashboard',{onSaved:function(result){
            genro.publish({topic:'editUserObjectDashboardConfirmed',parent:true},result.attr.id);
        }});
        """,subscribe_userObjectEditorConfirm=True,table=table,objtype=objtype,
        datapath='.dashboardMeta',pkey='=.id')
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
            frame.data('main.query.where',queryBag)
    
    def _wherePaneConfig(self,bc,table=None,frame=None):
        bc.contentPane(datapath='main',query_table=table,
                        onCreated="this.querymanager = new gnr.FakeTableHandler(this);",
                        nodeId='%s_query' %frame.attributes['frameCode'],margin='2px',region='center')   
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