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

    def pt_valuesStruct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname',name='Field',width='100%')
        values = ','.join(GnrPandas.AGGFUNCDICT.keys())
        r.cell('aggregators',name='Aggregators',width='15em',edit=dict(tag='checkBoxText',
                                                                        values=values))



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
    def cmd_editDataset(self,sc,**kwargs):
        bc = sc.borderContainer(size_h=400,size_w=550,**kwargs)
        bc.dataController("SET #FORM.record.pars.edited_dataframe = genro.statspane.parentDataFrame(this);",
                            formsubscribe_onLoaded=True,_if='command == "editDataset" && this.form.isNewRecord()',
                            command='=#FORM.record.command')

        def editable_struct(struct):
            r = struct.view().rows()
            r.cell('fieldname',width='10em',name='Column',edit=True,editDisabled="=#ROW.newserie?=!#v")
            r.cell('name',width='12em',edit=True,name='Name')
            r.cell('datatype',width='12em',name='DataType')
            #r.cell('element_count',width='12em',name='Count')
            r.cell('formula',width='12em',name='Formula',edit=True,editDisabled="=#ROW.newserie?=!#v")

        #bc.contentPane(region='center').quickGrid('^#FORM.record.dataframe_info')


        bc.contentPane(region='center').bagGrid(storepath='#FORM.record.pars.edited_dataframe',
                                                datapath='#FORM.dfeditor',
                                                addrow=True,delrow=True,title='Edit Dataframe',
                                                struct=editable_struct,pbl_classes=True,
                                                grid_addRowMode='>',
                                                default_newserie =True,
                                                margin='2px')


    @metadata(order=1,name='!!New Pivot table')
    def cmd_pivotTable(self,sc,**kwargs):
        mainbc = sc.borderContainer(size_h=600,size_w=700,**kwargs)
        mainbc.dataController("SET #FORM.parentDataframe.store = genro.statspane.parentDataFrame(this);",
                                formsubscribe_onLoaded=True,_if="command=='pivotTable'",command='=#FORM.record.command')
        fb = mainbc.contentPane(region='top').formbuilder(datapath='.record')
        fb.textbox(value='^.pars.name',lbl='Name',validate_notnull='^#FORM.record.command?=#v=="pivotTable"')
        bc = mainbc.borderContainer(design='sidebar',region='center')


        def picker_struct(struct):
            r = struct.view().rows()
            r.cell('fieldname',width='100%')
            r.cell('datatype',width='6em',name='DataType')

        bc.contentPane(region='left',width='200px').bagGrid(storepath='#FORM.parentDataframe.store',
                                                            datapath='#FORM.parentDataframe',
                                                                    grid_draggable_row=True,
                                                                    grid_dragClass='draggedItem',
                                                                    grid_onDrag='dragValues["statcol"]=dragValues.gridrow.rowset;',
                                                                    grid_selected_fieldname='.selectedField',
                                                                    grid_multiSelect=False,
                                                                    addrow=False,delrow=False,title='Dataframe cols',
                                                                    struct=picker_struct,pbl_classes=True,
                                                                    margin='2px')

        tc = bc.tabContainer(region='center',margin='2px',selectedPage='^#FORM.selectedPage')
        parsbc = tc.borderContainer(title='Pivot parameters',pageName='pivotPars')
 
        commonKw = dict(grid_selfDragRows=True,
                        struct=self.pt_fieldsStruct,addrow=False,
                        grid_dropTarget_grid="statcol",pbl_classes=True,margin='2px',
                        grid_onDrop_statcol="""
                            var storebag = this.widget.storebag();
                            data.forEach(function(n){
                                storebag.setItem(n.fieldname,new gnr.GnrBag({fieldname:n.fieldname}));
                            });
 
                        """)
        parsbc.contentPane(region='top',height='33%').bagGrid(title='Index',frameCode='pt_index',storepath='#FORM.record.pars.pivot.index',
                                                          datapath='#FORM.indexgrid',**commonKw)
        parsbc.contentPane(region='bottom',height='33%').bagGrid(title='Columns',frameCode='pt_columns',storepath='#FORM.record.pars.pivot.columns',
                                                          datapath='#FORM.columnsgrid',**commonKw)
        commonKw['struct'] = self.pt_valuesStruct
        parsbc.contentPane(region='center').bagGrid(title='Values',frameCode='pt_values',storepath='#FORM.record.pars.pivot.values',
                                                          datapath='#FORM.valuesgrid',**commonKw)

        filterspane = tc.contentPane(title='Dataset filters',pageName='dfFilters')
        filterspane.dataRpc(None,self.page.statspane_availableFieldValues,httpMethod='WSK',
                     fieldname='^#FORM.parentDataframe.grid.selectedField',dfname='=#FORM.record.dfname',
                     code='=#ANCHOR.statcode',
                     _if="fieldname && _pageName=='dfFilters'",
                     _pageName='^#FORM.selectedPage',
                     _onCalling="""
                     if(_stores && _stores.getNode(fieldname)){
                        return false;
                     }
                     """,
                     _onResult="""
                        this.setRelativeData('#FORM.availableFilterValuesGrid.stores.'+kwargs.fieldname,result);
                     """,_stores='=#FORM.availableFilterValuesGrid.stores')

        def filters_struct(struct):
            r = struct.view().rows()
            r.cell('_selected',userSets=True,name=' ')
            r.cell('fieldvalue',width='100%')

        frame=filterspane.bagGrid(storepath='^#FORM.availableFilterValuesGrid.currentFilterPath',
                    datapath='#FORM.availableFilterValuesGrid',
                    grid_userSets='.currentCheckeds',
                    grid_identifier='fieldvalue',
                        addrow=False,delrow=False,title='Filter on',
                        struct=filters_struct,margin='2px',pbl_classes=True,datamode='attr')
        frame.grid.dataController("""
            if(_triggerpars.kw.reason=='fieldfilterSet'){
                return;
            }
            this.setRelativeData('#FORM.record.pars.filters.'+fieldname,currentCheckeds);
            """,currentCheckeds='^.currentCheckeds._selected',fieldname='=#FORM.parentDataframe.grid.selectedField',
            _if='fieldname')
        frame.grid.dataController("""
            var fieldFilters = this.getRelativeData('#FORM.record.pars.filters.'+fieldname);
            this.setRelativeData('.currentCheckeds._selected',fieldFilters,null,null,'fieldfilterSet');
            """,currentCheckeds='=.currentCheckeds._selected',fieldname='^#FORM.parentDataframe.grid.selectedField',
            _if='fieldname')
        frame.dataController("""
            SET #FORM.availableFilterValuesGrid.currentFilterPath = '#FORM.availableFilterValuesGrid.stores.'+fieldname;
            """,fieldname='^#FORM.parentDataframe.grid.selectedField',_if='fieldname')
        frame.top.bar.replaceSlots('#','#,searchOn,5')


class StatsPane(BaseComponent):
    py_requires="""js_plugins/chartjs/chartjs:ChartPane,
                    gnrcomponents/framegrid:FrameGrid,
                    gnrcomponents/formhandler:FormHandler"""
    js_requires='js_plugins/statspane/statspane'
    css_requires='js_plugins/statspane/statspane'


    @public_method
    def pdstats_remoteCommandGrid(self,pane,table=None,code=None,connectedWidgetId=None,**kwargs):
        pane.pdCommandsGrid(code,table=table,
                            connectedWidgetId=connectedWidgetId,datapath='.dfcommands')


    def pdcommand_struct(self,struct):
        r = struct.view().rows()
        r.cell('counter',name='C.',width='3em',counter=True,dtype='L')
        r.cell('_tpl',name='Pars',width='100%',rowTemplate='$dfname <span style="color:blue">$command</span>')
        r.cell('status',width='2em',name=' ',
                _customGetter="""function(row){
                    return '<div class="stat_step_status_'+row.status+'">&nbsp;</div>';
                }""")
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
                            grid_selectedId='^.selectedCommand',
                            grid_identifier='code',
                            grid_multiSelect=False,
                            **kwargs)
        frame.grid.dataController("""
            var viewerNode = this.getRelativeData('#ANCHOR.viewer.rows.'+selectedCommand);
            SET #ANCHOR.selectedStep = viewerNode?selectedCommand:'emptyStep';
            """,selectedCommand='^.selectedCommand',_if='selectedCommand')
        frame.grid.dataController("""
            SET .selectedCommand = selectedStep;
            """,selectedStep='^#ANCHOR.selectedStep',_if='selectedStep && selectedStep!="emptyStep"')
        frame.dataController("""if(_reason=='child' && _triggerpars.kw.evt=='del'){
                var parent_lv = _node.parentshipLevel(this.getRelativeData('.commands').getNode('rows'));
                if(parent_lv==1){
                    genro.publish(code+'_stepRemoved',{step:_node.getValue().getItem('code')});
                }
            }""", commands='^.commands.rows',code=code)
        frame.dataController("""
            this.setRelativeData('.commands.rows.'+step+'.status','OK');
            genro.publish(code+'_stepDone',{step:step,result:result,counter:counter});
            """,code=code,
            **{'subscribe_%s_pandas_step' %code:True})


        frame.sharedObject('.commands',shared_id=code,autoSave=True,autoLoad=True)
        bar = frame.top.bar.replaceSlots('delrow','delrow,addrow,5',
                                    addrow_defaults='.menucommands')
        footer = frame.bottom.slotToolbar('5,*,clear_res,5,run,5')
        footer.clear_res.slotButton('Clear',action="""if(commands){commands.values().forEach(function(v){v.setItem('status','NO')})}""",
            commands='=.commands.rows')
        footer.run.slotButton('Run stat',iconClass='iconbox run',action='FIRE .runCommands;')

        footer.dataRpc(None,self.statspane_runCommands,_allcommands='=%s' %storepath,code=code,
                        _fired='^.runCommands',httpMethod='WSK',
                        _onCalling="""
                            if(!_allcommands || _allcommands.len()===0){
                                return false;
                            }
                            var filteredCommands = new gnr.GnrBag();
                            var first = _allcommands.getNodeByValue('status','TC');
                            if(!first){
                                first = _allcommands.getNodeByValue('status','NO');
                            }
                            if(!first){
                                return false;
                            }
                            _allcommands.getNodes().slice(_allcommands.index(first.label)).forEach(function(n){
                                filteredCommands.setItem(n.label,n._value);
                            });
                            kwargs.commands = filteredCommands;
                        """)
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
            if(doRunCommand){
                FIRE #ANCHOR.dfcommands.runCommands;
            }
            """,formsubscribe_onDismissed=True,
            grid=frame.grid.js_widget,doRunCommand='=#FORM.controller.temp.doRunCommand')

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
        bar = form.bottom.slotBar('*,cancel,savebtn,saveAndRun',margin_bottom='2px',_class='slotbar_dialog_footer')
        fh = StatsCommandForms(self)
        for commandname,commandhandler in fh.commandlist():
            commandhandler(sc,pageName=commandname)
        bar.cancel.button('!!Cancel',action='this.form.abort();')
        bar.savebtn.button('!!Save',iconClass='fh_semaphore',action="""
                                SET #FORM.record.status = 'TC';
                                this.form.publish("save",{destPkey:"*dismiss*"})""")
        bar.saveAndRun.button('!!Save and run',
                        iconClass='fh_semaphore',action="""SET #FORM.record.status = 'TC';
                                        this.form.publish("save",{destPkey:"*dismiss*"});
                                        SET #FORM.controller.temp.doRunCommand = true;
                                        """)
    @websocket_method
    def statspane_runCommands(self,commands=None,code=None):
        topic = '%s_pandas_step'%code
        with self.sharedData('pandasdata') as pandasdata: 
            gp = pandasdata.get(code)
            if not gp:
                gp = GnrPandas(language=self.language)
                pandasdata[code] = gp
            for n in commands:
                v = n.value
                result = getattr(self,'statspane_run_%(command)s' %v)(gnrpandas=gp,dfname=v['dfname'],**v['pars'].asDict(ascii=True))
                self.clientPublish(topic,result=result,step=n.label,counter=v['counter'])

    @websocket_method
    def statspane_availableFieldValues(self,code=None,dfname=None,fieldname=None):
        result = Bag()
        with self.sharedData('pandasdata') as pandasdata: 
            gp = pandasdata[code]
        gnrdf = gp.dataframes[dfname]
        df = gnrdf.dataframe
        for i,v in enumerate(df[fieldname].unique()):
            if v is not None:
                result.setItem('r_%s' %i,None,fieldvalue=v)
        return result

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
        return Bag(store=gnrpandas[dfname].getInfo(),infostatus=dfname)


    def statspane_run_pivotTable(self,gnrpandas=None,dfname=None,name=None,pivot=None,filters=None,**kwargs):
        return gnrpandas[dfname].pivotTableGrid(index=pivot['index'],values=pivot['values'],
                                                columns=pivot['columns'])


    def statspane_run_editDataset(self,gnrpandas=None,dfname=None,edited_dataframe=None,**kwargs):
        return Bag(store=gnrpandas[dfname].applyChanges(edited_dataframe),infostatus=dfname)

