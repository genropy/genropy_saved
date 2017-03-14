# -*- coding: UTF-8 -*-

# chartmanager.py
# Created by Francesco Porcari on 2017-01-01.
# Copyright (c) 2017 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,websocket_method,metadata
from gnr.xtnd.gnrpandas import GnrPandas
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebstruct import struct_method


class StatsCommandForms(object):

    def __init__(self,page=None):
        self.page = page

    def commandlist(self):
        return [(m.__name__[4:],m) for m in [getattr(self,c) for c in dir(self) if c.startswith('cmd_')]]

    @classmethod
    def commandmenubags(cls):
        basecommands = Bag()
        dfcommands = Bag()
        for m in [getattr(cls,c) for c in dir(cls) if c.startswith('cmd_')]:
            b = basecommands if getattr(m,'basecmd',None) else dfcommands
            b.setItem('r_%s' %m.order,None,default_kw=dict(command=m.__name__[4:]),caption=m.name)
        basecommands.sort('#k')
        dfcommands.sort('#k')
        return basecommands,dfcommands

    def pt_fieldsStruct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname',name='Field',width='100%')



    @metadata(order=0,name='!!Dataframe from db',basecmd=True)
    def cmd_dataframeFromDb(self,sc,**kwargs):
        bc = sc.borderContainer(size_h=300,size_w=400,**kwargs)
        fb = bc.contentPane(region='top',datapath='.record').div(margin_right='30px').formbuilder(colswidth='auto',width='100%',fld_width='100%')
        fb.textbox(value='^.dfname',lbl='Dataframe',validate_notnull='^#FORM.record.command?=#v=="dataframeFromDb"',unmodifiable=True)
        fb.textbox(value='^.pars.table',lbl='Table',validate_notnull='^#FORM.record.command?=#v=="dataframeFromDb"')
        fb.textbox(value='^.pars.columns',lbl='Columns')
        fb.simpleTextArea(value='^.pars.where',lbl='Where',height='100px')
        #bc.roundedGroupFrame(title='Extra kwargs',region='center').multiValueEditor(value='^#FORM.record.query_kwargs')

    @metadata(order=0,name='!!Edit dataset')
    def cmd_changeColumns(self,sc,**kwargs):
        sc.contentPane(**kwargs).div('change')


    @metadata(order=1,name='!!New Pivot table')
    def cmd_pivotTable(self,sc,**kwargs):
        mainbc = sc.borderContainer(size_h=600,size_w=700,**kwargs)
        mainbc.dataController("SET #FORM.parentDataframe.store = genro.statspane.parentDataFrame(this);",formsubscribe_onLoaded=True)
        fb = mainbc.contentPane(region='top').formbuilder(datapath='.record')
        fb.textbox(value='^.pars.name',lbl='Name',validate_notnull='^#FORM.record.command?=#v=="pivotTable"')
        bc = mainbc.borderContainer(region='center',design='sidebar')

        def picker_struct(struct):
            r = struct.view().rows()
            r.cell('fieldname',width='100%')

        bc.contentPane(region='left',width='140px').bagGrid(storepath='#FORM.parentDataframe.store',
                                                            datapath='#FORM.parentDataframe',
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
        bc.contentPane(region='top',height='33%').bagGrid(title='Index',frameCode='pt_index',storepath='#FORM.record.pars.pivot.index',
                                                          datapath='#FORM.indexgrid',**commonKw)
        bc.contentPane(region='bottom',height='33%').bagGrid(title='Columns',frameCode='pt_columns',storepath='#FORM.record.pars.pivot.columns',
                                                          datapath='#FORM.columnsgrid',**commonKw)
        bc.contentPane(region='center').bagGrid(title='Values',frameCode='pt_values',storepath='#FORM.record.pars.pivot.values',
                                                          datapath='#FORM.valuesgrid',**commonKw)

class PdCommandsGrid(BaseComponent):
    py_requires="""gnrcomponents/framegrid:FrameGrid,
                    gnrcomponents/formhandler:FormHandler"""

    def pdcommand_struct(self,struct):
        r = struct.view().rows()
        r.cell('counter',name='C.',width='3em',counter=True,dtype='L')
        r.cell('_tpl',name='Pars',width='100%',rowTemplate='$dfname <span style="color:blue">$command</span> <br/>pars:$pars')
        r.cell('done',dtype='B',semaphore=True)
        r.cell('result_id',hidden=True)

    @struct_method
    def pdstats_pdCommandsGrid(self,pane,code=None,storepath=None,datapath=None,table=None,**kwargs):
        code = code or self.getUuid()
        datapath = datapath or 'gnr.workspace.pdcommands.%s' %code
        storepath = '.commands.rows'
        frame = pane.bagGrid(frameCode='V_commands_%s' %code,title='Stats commands',datapath=datapath,
                            storepath=storepath,
                            grid_canSort=False,
                            _class='noheader',
                            addrow=False,delrow=True,struct=self.pdcommand_struct,
                            grid_selectedLabel='.selectedCommand',
                            grid_multiSelect=False,
                            **kwargs)
        frame.grid.dataController("""
            var viewerNode = this.getRelativeData('#ANCHOR.viewer.rows.'+selectedCommand);
            SET #ANCHOR.selectedStep = viewerNode?selectedCommand:'emptyStep';
            """,selectedCommand='^.selectedCommand',_if='selectedCommand')
        frame.sharedObject('.commands',shared_id=code,autoSave=True,autoLoad=True)
        bar = frame.top.bar.replaceSlots('delrow','delrow,addrow,5',
                                    addrow_defaults='.menucommands')
        footer = frame.bottom.slotToolbar('5,runOnSave,*,clear_res,5,run,5')
        footer.runOnSave.checkbox(value='^.runOnSave',label='Run on save',default_value=True)
        footer.clear_res.slotButton('Clear',action="""if(commands){commands.values().forEach(function(v){v.setItem('done',false)})}""",
            commands='=.commands.rows')
        footer.run.slotButton('Run stat',iconClass='iconbox run',action='FIRE .runCommands;')

        footer.dataRpc(None,self.statspane_runCommands,commands='=%s' %storepath,code=code,_fired='^.runCommands',httpMethod='WSK')
        basecommands,dfcommands = StatsCommandForms.commandmenubags()
        frame.data('.basecommands',basecommands)
        frame.data('.dfcommands',dfcommands)

        frame.dataController("""var cb = function(){
                                    var currentCommands = g.storebag();
                                    return genro.statspane.commandMenu(currentCommands,basecommands,dfcommands,{table:table});
                                };
                                SET .menucommands = new gnr.GnrBagCbResolver({method:cb});
                                """,
                        _onBuilt=True,basecommands='=.basecommands',dfcommands='=.dfcommands',g=frame.grid.js_widget,
                        table=table)

        #[(caption,dict(command=command)) for order,command,caption in StatsCommandForms.commandlist()]

        form = frame.grid.linkedForm(frameCode='F_commands_%s' %code,
                                 datapath='%s.form' %datapath,loadEvent='onRowDblClick',
                                 dialog_height='300px',dialog_width='400px',
                                 dialog_title='Command',handlerType='dialog',
                                 dialog_nodeId='command_dialog_%s' %code,
                                 childname='form',attachTo=pane,store='memory',default_data_type='T',
                                 store_pkeyField='code',dialog_noModal=False,store_newPkeyCb="return 'c_'+new Date().getTime()")
        form.dataController("""grid.updateCounterColumn();
            FIRE #ANCHOR.runCommands;
            """,formsubscribe_onDismissed=True,
            grid=frame.grid.js_widget,
            runOnSave='=#ANCHOR.runOnSave')
        form.dataController("""
            genro.bp(true);
            """,formsubscribe_onSaved=True)

        sc = form.center.stackContainer(selectedPage='^.record.command',
                                    selfsubscribe_selected="""
                                        if($1.selected){
                                            var sizer = objectExtract(this.widget.gnrPageDict[p_0.page].sourceNode.attr,'size_*',true);
                                            var dialogNode= genro.nodeById('command_dialog_%s') //.resize();
                                            setTimeout(function(){
                                                dialogNode.widget.resize(sizer);
                                                dialogNode.widget.adjustDialogSize();
                                            },1);
                                        }
                                    """ %code)
        bar = form.bottom.slotBar('*,cancel,savebtn',margin_bottom='2px',_class='slotbar_dialog_footer')
        fh = StatsCommandForms(self)
        for commandname,commandhandler in fh.commandlist():
            commandhandler(sc,pageName=commandname)
        bar.cancel.button('!!Cancel',action='this.form.abort();')
        bar.savebtn.button('!!Save',iconClass='fh_semaphore',action='this.form.publish("save",{destPkey:"*dismiss*"})')

    @websocket_method
    def statspane_runCommands(self,commands=None,code=None):
        topic = '%s_pandas_step'%code
        with self.sharedData('pandasdata') as pandasdata: 
            gp = pandasdata.get(code)
            if not gp:
                gp = GnrPandas()
                pandasdata[code] = gp
            for n in commands:
                v = n.value
                result = getattr(self,'statspane_run_%(command)s' %v)(gnrpandas=gp,dfname=v['dfname'],**v['pars'].asDict(ascii=True))
                print 'aaa'
                self.clientPublish(topic,result=result,step=n.label,counter=v['counter'])



    def statspane_run_dataframeFromDb(self,gnrpandas=None,dfname=None,table=None,where=None,condition=None,columns=None,
                           selectionKwargs=None,**kwargs):
        if selectionKwargs:
            kwargs.update(selectionKwargs)
        if isinstance(where,Bag):
            where,kwargs = self.db.table(table).sqlWhereFromBag(where, kwargs)
        if condition:
            where = ' ( %s ) AND ( %s ) ' % (where, condition) if where else condition
        gnrpandas.dataframeFromDb(dfname=dfname,db=self.db,tablename=table,where=where,condition=condition,
                                columns=columns,**kwargs)
        struct = Bag()
        r = Bag()
        struct['view_0.rows_0'] = r
        r.setItem('cell_0',None,field='fieldname',
                            name='Field',
                            width='10em')
        r.setItem('cell_1',None,field='name',
                            name='Label',
                            width='10em')
        r.setItem('cell_1',None,field='element_count',
                            name='C.',
                            width='4em')
        return Bag(store=gnrpandas[dfname].getInfo(),struct=struct,infostatus=dfname)


    def statspane_run_pivotTable(self,gnrpandas=None,dfname=None,name=None,pivot=None,**kwargs):
        return gnrpandas[dfname].pivotTableGrid(index=pivot['index'].keys() if pivot['index'] else None,
                                    values=pivot['values'].keys() if pivot['values'] else None,
                                    columns=pivot['columns'].keys() if pivot['columns'] else None)



class StatsPane(BaseComponent):
    py_requires='js_plugins/chartjs/chartjs:ChartPane,js_plugins/statspane/statspane:PdCommandsGrid'
    js_requires='js_plugins/statspane/statspane'
    css_requires='js_plugins/statspane/statspane'


    @public_method
    def pdstats_commandsGrid(self,pane,table=None,code=None,connectedWidgetId=None,**kwargs):
        pane.pdCommandsGrid(code,table=table,
                            connectedWidgetId=connectedWidgetId,datapath='.dfcommands')


    #@public_method
    #def pdstats_configuratorTabs(self,pane,table=None,dfname=None,query_pars=None,connectedWidgetId=None,**kwargs):
    #    query_pars = query_pars or {}
    #    if query_pars:
    #        query_pars['where'] = query_pars.pop('_')
    #    bc = pane.borderContainer()
    #    top = bc.contentPane(region='top',border_bottom='1px solid silver')
    #    fb = top.formbuilder(cols=2,border_spacing='3px',_anchor=True)
    #    fb.button('Load',fire='#WORKSPACE.df.load_dataframe')
    #    fb.dataRpc('#WORKSPACE.df.info.store',self.dataframeFromDb,
    #                _connectedWidgetId=connectedWidgetId,
    #                _fired='^#WORKSPACE.df.load_dataframe',
    #                tablename=table,dfname=dfname,
    #                _onCalling="""
    #                    genro.statspane.queryParsFromGrid(kwargs);
    #                """,
    #                _onResult='FIRE #WORKSPACE.df.loadedDataframe',
    #                _lockScreen=True,timeout=300000,
    #                **query_pars)
    #    tc = bc.tabContainer(region='center',margin='2px')
    #    self.dataFrameCoords(tc.borderContainer(title='Dataframe'),table=table,dfname=dfname)
    #    self.pivotTables(tc.borderContainer(title='Pivot',_class='noheader'),table=table,dfname=dfname)        
#
#
    #def dataFrameCoords(self,bc,table=None,dfname=None):
    #    frame = bc.contentPane(region='top',height='50%').bagGrid(frameCode='dataFrameInfo',storepath='.store',title='DF coords',
    #                                                            datapath='#WORKSPACE.df.info',
    #                                                            struct=self.dfcoords_struct,
    #                                                            grid_selfDragRows=True,
    #                                                            addrow=True,delrow=True)
    #    bar = frame.bottom.slotBar('*,updateDataframe,5',margin_bottom='2px',_class='slotbar_dialog_footer')
    #    bar.updateDataframe.slotButton('Update',fire='#WORKSPACE.df.update')
    #    bc.dataRpc('#WORKSPACE.df.info.store',self.updateDataframe,table='=#WORKSPACE.df.table',limit='=#WORKSPACE.df.limit',
    #                dfname='=#WORKSPACE.df.dfname',info='=#WORKSPACE.df.info.store',_fired='^#WORKSPACE.df.update')
#
    #def pivotTablesStruct(self,struct):
    #    r = struct.view().rows()
    #    r.cell('_tpl',_customGetter="""
    #        function(row){
    #            var b = new gnr.GnrBag(row);
    #            return b.getFormattedValue();
    #        }
    #        """,width='100%')
#
#
    #def pivotTables(self,bc,table=None,dfname=None):
    #    view = bc.contentPane(region='bottom',height='40%').bagGrid(title='Stored pivots',frameCode='V_%s_pivotTable' %dfname,storepath='.store',
    #                                                                datapath='#WORKSPACE.df.storedPivots',
    #                                                                struct=self.pivotTablesStruct,
    #                                                                addrow=False,delrow=True)
    #    self.pivotTableForm(view.grid.linkedForm(frameCode='F_%s_pivotTable' %dfname,
    #                             datapath='#WORKSPACE.df.storedPivots.form',loadEvent='onRowDblClick',
    #                             handlerType='border',
    #                             childname='form',attachTo=bc,
    #                             formRoot=bc.contentPane(region='center'),
    #                             store='memory',
    #                             store_pkeyField='code'),table=table,dfname=dfname)
#
#
#
    #def pivotTableForm(self,form,table=None,dfname=None):
    #    topbar = form.top.slotToolbar('10,ftitle,*')
    #    bottom = form.bottom.slotBar('5,clearCurrent,savePivot,*,runCurrent,5',margin_bottom='2px',_class='slotbar_dialog_footer')
#
    #    topbar.ftitle.div("^#FORM.record.code?=#v?'Pivot:'+#v:'Pivot'",font_size='.9em',color='#666',font_weight='bold')
    #    form.dataController("this.form.reset();this.form.newrecord();",_fired='^#WORKSPACE.df.loadedDataframe')
    #    bottom.clearCurrent.slotButton('Clear',action="""
    #        this.form.reset();
    #        this.form.newrecord();
    #        """)
    #    bottom.runCurrent.slotButton('Run',fire='.run')
    #    form.dataRpc('#WORKSPACE.pivot.result',self.getPivotTable,data='=#FORM.record',
    #                dfname=dfname,table=table,_fired='^.run')
    #    bottom.savePivot.slotButton('Save',#iconClass="iconbox save",
    #                            parentForm=True,
    #                            ask=dict(askIf="!code",title='Save new pivot',askOn='Shift',
    #                                    fields=[dict(name='code',lbl='Code')]),
    #                            action="""
    #                            SET #FORM.record.code = code;
    #                            this.form.save();
    #                            """,code='=#FORM.record.code')
#
    #    bc = form.center.borderContainer(design='sidebar')
#
    #    def picker_struct(struct):
    #        r = struct.view().rows()
    #        r.cell('fieldname',width='100%')
    #    bc.contentPane(region='left',width='140px').bagGrid(storepath='#WORKSPACE.df.info.store',
    #                                                        datapath='#FORM.available_df_cols',
    #                                                                grid_draggable_row=True,
    #                                                                grid_dragClass='draggedItem',
    #                                                                grid_onDrag='dragValues["statcol"]=dragValues.gridrow.rowset;',
    #                                                                addrow=False,delrow=False,title='Dataframe cols',
    #                                                                struct=picker_struct)
#
    #    commonKw = dict(grid_selfDragRows=True,
    #                    struct=self.pt_fieldsStruct,addrow=False,
    #                    grid_dropTarget_grid="statcol",
    #                    grid_onDrop_statcol="""
    #                        var storebag = this.widget.storebag();
    #                        data.forEach(function(n){
    #                            storebag.setItem(n.fieldname,new gnr.GnrBag({fieldname:n.fieldname}));
    #                        });
#
    #                    """)
    #    bc.contentPane(region='top',height='33%').bagGrid(title='Index',frameCode='pt_index',storepath='#FORM.record.index',
    #                                                      datapath='#FORM.indexgrid',**commonKw)
    #    bc.contentPane(region='bottom',height='33%').bagGrid(title='Values',frameCode='pt_values',storepath='#FORM.record.values',
    #                                                      datapath='#FORM.valuesgrid',**commonKw)
    #    bc.contentPane(region='center').bagGrid(title='Columns',frameCode='pt_columns',storepath='#FORM.record.columns',
    #                                                      datapath='#FORM.columnsgrid',**commonKw)
#
    #def pt_fieldsStruct(self,struct):
    #    r = struct.view().rows()
    #    r.cell('fieldname',name='Field',width='100%')
#
    #def dfcoords_struct(self,struct):
    #    r = struct.view().rows()
    #    r.cell('fieldname',name='Field',width='10em')
    #    #r.cell('dataType',name='Dtype',width='5em')
    #    r.cell('name',name='Label',width='12em',edit=True)
    #    r.cell('element_count',name='C.',width='4em',dtype='L')
#
    #@public_method
    #def dataframeFromDb(self,dfname=None,tablename=None,where=None,condition=None,columns=None,statname=None,selectionKwargs=None,**kwargs):
    #    statname = statname or dfname
    #    path = self.site.getStaticPath('page:stats',statname)
    #    if selectionKwargs:
    #        kwargs.update(selectionKwargs)
    #    if isinstance(where,Bag):
    #        where,kwargs = self.db.table(tablename).sqlWhereFromBag(where, kwargs)
    #    if condition:
    #        where = ' ( %s ) AND ( %s ) ' % (where, condition) if where else condition
    #    gp = GnrPandas()
    #    #with GnrPandas(path) as gp:
    #    gp.dataframeFromDb(dfname=dfname,db=self.db,tablename=tablename,where=where,condition=condition,
    #                            columns=columns,**kwargs)
    #    gp.save(path)
    #    return gp[dfname].getInfo()
#
    #@public_method
    #def updateDataframe(self,dfname=None,statname=None,info=None,**kwargs):
    #    statname = statname or dfname
    #    path = self.site.getStaticPath('page:stats',statname)
    #    gp = GnrPandas()
    #    gp.load(path)
#
    #    #return gnrdf.getInfo()
#
    #@public_method
    #def getPivotTable(self,dfname=None,data=None,statname=None,**kwargs):
    #    statname = statname or dfname
    #    path = self.site.getStaticPath('page:stats',statname)
    #    gp = GnrPandas()
    #    gp.load(path)
    #    #with GnrPandas(path) as gp:
    #    return gp[dfname].pivotTableGrid(index=data['index'].keys() if data['index'] else None,
    #                                values=data['values'].keys() if data['values'] else None,
    #                                columns=data['columns'].keys() if data['columns'] else None)
#
