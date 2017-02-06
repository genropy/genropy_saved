# -*- coding: UTF-8 -*-

# chartmanager.py
# Created by Francesco Porcari on 2017-01-01.
# Copyright (c) 2017 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.xtnd.gnrpandas import GnrPandas

class StatsPane(BaseComponent):
    py_requires='js_plugins/chartjs/chartjs:ChartPane'
    js_requires='js_plugins/statspane/statspane'
    css_requires='js_plugins/statspane/statspane'

    @public_method
    def pdstats_configuratorTabs(self,pane,table=None,dfname=None,query_pars=None,connectedWidgetId=None,**kwargs):
        query_pars = query_pars or {}
        if query_pars:
            query_pars['where'] = query_pars.pop('_')
        bc = pane.borderContainer()
        top = bc.contentPane(region='top',border_bottom='1px solid silver')
        fb = top.formbuilder(cols=2,border_spacing='3px',_anchor=True)
        fb.button('Load',fire='#WORKSPACE.df.load_dataframe')
        fb.dataRpc('#WORKSPACE.df.info.store',self.dataframeFromDb,
                    _connectedWidgetId=connectedWidgetId,
                    _fired='^#WORKSPACE.df.load_dataframe',
                    tablename=table,dfname=dfname,
                    #_onCalling="genro.bp(true);",
                    _onResult='FIRE #WORKSPACE.df.loadedDataframe',
                    **query_pars)
        tc = bc.tabContainer(region='center',margin='2px')
        self.pivotTables(tc.borderContainer(title='Pivot',_class='noheader'),table=table,dfname=dfname)
        self.dataFrameCoords(tc.borderContainer(title='Dataframe'),table=table,dfname=dfname)


    def dataFrameCoords(self,bc,table=None,dfname=None):
        frame = bc.contentPane(region='top',height='50%').bagGrid(frameCode='dataFrameInfo',storepath='.store',title='DF coords',
                                                                datapath='#WORKSPACE.df.info',
                                                                struct=self.dfcoords_struct,
                                                                grid_selfDragRows=True,
                                                                addrow=True,delrow=True)
        bar = frame.bottom.slotBar('*,updateDataframe,5',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.updateDataframe.slotButton('Update',fire='#WORKSPACE.df.update')
        bc.dataRpc('#WORKSPACE.df.info.store',self.updateDataframe,table='=#WORKSPACE.df.table',limit='=#WORKSPACE.df.limit',
                    dfname='=#WORKSPACE.df.dfname',info='=#WORKSPACE.df.info.store',_fired='^#WORKSPACE.df.update')

    def pivotTablesStruct(self,struct):
        r = struct.view().rows()
        r.cell('_tpl',_customGetter="""
            function(row){
                var b = new gnr.GnrBag(row);
                return b.getFormattedValue();
            }
            """,width='100%')


    def pivotTables(self,bc,table=None,dfname=None):
        view = bc.contentPane(region='bottom',height='40%').bagGrid(title='Stored pivots',frameCode='V_%s_pivotTable' %dfname,storepath='.store',
                                                                    datapath='#WORKSPACE.df.storedPivots',
                                                                    struct=self.pivotTablesStruct,
                                                                    addrow=False,delrow=True)
        self.pivotTableForm(view.grid.linkedForm(frameCode='F_%s_pivotTable' %dfname,
                                 datapath='#WORKSPACE.df.storedPivots.form',loadEvent='onRowDblClick',
                                 handlerType='border',
                                 childname='form',attachTo=bc,
                                 formRoot=bc.contentPane(region='center'),
                                 store='memory',
                                 store_pkeyField='code'),table=table,dfname=dfname)



    def pivotTableForm(self,form,table=None,dfname=None):
        topbar = form.top.slotToolbar('10,ftitle,*')
        bottom = form.bottom.slotBar('5,clearCurrent,savePivot,*,runCurrent,5',margin_bottom='2px',_class='slotbar_dialog_footer')

        topbar.ftitle.div("^#FORM.record.code?=#v?'Pivot:'+#v:'Pivot'",font_size='.9em',color='#666',font_weight='bold')
        form.dataController("this.form.reset();this.form.newrecord();",_fired='^#WORKSPACE.df.loadedDataframe')
        bottom.clearCurrent.slotButton('Clear',action="""
            this.form.reset();
            this.form.newrecord();
            """)
        bottom.runCurrent.slotButton('Run',fire='.run')
        form.dataRpc('#WORKSPACE.pivot.result',self.getPivotTable,data='=#FORM.record',
                    dfname=dfname,table=table,_fired='^.run')
        bottom.savePivot.slotButton('Save',#iconClass="iconbox save",
                                parentForm=True,
                                ask=dict(askIf="!code",title='Save new pivot',askOn='Shift',
                                        fields=[dict(name='code',lbl='Code')]),
                                action="""
                                SET #FORM.record.code = code;
                                this.form.save();
                                """,code='=#FORM.record.code')

        bc = form.center.borderContainer(design='sidebar')

        def picker_struct(struct):
            r = struct.view().rows()
            r.cell('fieldname',width='100%')
        bc.contentPane(region='left',width='140px').bagGrid(storepath='#WORKSPACE.df.info.store',
                                                            datapath='#FORM.available_df_cols',
                                                                    grid_draggable_row=True,
                                                                    grid_dragClass='draggedItem',
                                                                    grid_onDrag='dragValues["statcol"]=dragValues.gridrow.rowset;',
                                                                    addrow=False,delrow=False,title='Dataframe cols',
                                                                    struct=picker_struct)

        commonKw = dict(grid_selfDragRows=True,
                        struct=self.pt_fieldsStruct,addrow=False,
                        grid_dropTarget_grid="statcol",
                        grid_onDrop_statcol="""
                            var storebag = this.widget.storebag();
                            data.forEach(function(n){
                                storebag.setItem(n.fieldname,new gnr.GnrBag({fieldname:n.fieldname}));
                            });

                        """)
        bc.contentPane(region='top',height='33%').bagGrid(title='Index',frameCode='pt_index',storepath='#FORM.record.index',
                                                          datapath='#FORM.indexgrid',**commonKw)
        bc.contentPane(region='bottom',height='33%').bagGrid(title='Values',frameCode='pt_values',storepath='#FORM.record.values',
                                                          datapath='#FORM.valuesgrid',**commonKw)
        bc.contentPane(region='center').bagGrid(title='Columns',frameCode='pt_columns',storepath='#FORM.record.columns',
                                                          datapath='#FORM.columnsgrid',**commonKw)

    def pt_fieldsStruct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname',name='Field',width='100%')

    def dfcoords_struct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname',name='Field',width='10em')
        r.cell('dataType',name='Dtype',width='5em')
        r.cell('label',name='Label',width='12em',edit=True)
        r.cell('element_count',name='C.',width='4em',dtype='L')

    @public_method
    def dataframeFromDb(self,dfname=None,tablename=None,where=None,columns=None,statname=None,**kwargs):
        statname = statname or 'stats_%s' %dfname
        path = self.site.getStaticPath('page:stats',statname)
        with GnrPandas(path) as gp:
            gp.dataframeFromDb(dfname=dfname,db=self.db,tablename=tablename,where=where,**kwargs)
        return gp[dfname].getInfo()

    @public_method
    def updateDataframe(self,table=None,dfname=None,info=None,**kwargs):
        service = self.site.getService('stats')
        gnrdf = service.gnrDataFrame(filepath='page:stats/%s/%s' %(table.replace('.','/'),dfname))
        gnrdf.updateInfo(info)
        gnrdf.to_pickle('page:stats/%s/%s' %(table.replace('.','/'),dfname))
        return gnrdf.getInfo()

    @public_method
    def getPivotTable(self,table=None,dfname=None,data=None,statname=None,**kwargs):
        statname = statname or 'stats_%s' %dfname
        path = self.site.getStaticPath('page:stats',statname)
        with GnrPandas(path) as gp:
            return gp[dfname].pivotTableGrid(index=data['index'].keys() if data['index'] else None,
                                    values=data['values'].keys() if data['values'] else None,
                                    columns=data['columns'].keys() if data['columns'] else None)


