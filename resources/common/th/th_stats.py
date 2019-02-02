# -*- coding: utf-8 -*-
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

from past.builtins import basestring
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrbag import Bag

try:
    import pandas as pd
    import numpy as np
    from gnr.xtnd.gnrpandas import GnrDbDataframe
except Exception:
    pd = False
    np = False
    GnrDbDataframe = False

class TableHandlerStats(BaseComponent):
    js_requires='th/th_stats'

    def ths_pandas_available(self):
        return GnrDbDataframe is not False

    @extract_kwargs(condition=dict(slice_prefix=False))
    @struct_method
    def th_tableHandlerStats(self,pane,table=None,
                            relation_field=None,
                            relation_value=None,
                            default_rows=None,
                            default_values=None,
                            default_columns=None,
                            condition=None,
                            condition_kwargs=None,
                            nodeId=None,
                            datapath=None,
                            statIdentifier=None,**kwargs):
        if not pd:
            pane.div('Missing Pandas')
        inattr = pane.getInheritedAttributes()
        relatedTable = inattr.get('table')
        relatedTableHandlerFrameCode = inattr.get('frameCode') if not (relation_value or condition) else None
        table = table or relatedTable
        nodeId = nodeId or '%s_pivotHandler' %relatedTableHandlerFrameCode if relatedTableHandlerFrameCode else 'th_stats_%s' %table.replace('.','_')
        bc = pane.borderContainer(datapath=datapath or '.%s' %nodeId,_anchor=True,**kwargs)
        bc.data('.currentTitle','Pandas Pivot Table')

        bc.child('_tableHandlerStatsLayout',region='center',
                            table=table,nodeId=nodeId,
                            relation_field=relation_field,
                            relation_value=relation_value.replace('^','') if relation_value else None,
                            default_rows=default_rows,
                            default_values=default_values,
                            default_columns=default_columns,
                            condition=condition,
                            relatedTable=relatedTable,
                            relatedTableHandlerFrameCode=relatedTableHandlerFrameCode,
                            condition_kwargs=condition_kwargs,
                            userObjectId=statIdentifier,**kwargs)
        
        indipendentQuery = relation_value or condition
        bc.dataController("""
           if(autorun){
               var that = this;
               genro.callAfter(function(){
                   that.fireEvent('.stats.run_pivot_do',true);
               },2000,this,'stast_run');
           }
        """,relation_value=relation_value,
            filters='^.stats.filters',
            stat_rows='^.stats.conf.rows',
            stat_values='^.stats.conf.values',
            stat_columns='^.stats.conf.columns',
            tat_columns='^.stats.conf.margins',
            autorun='=.stats.autorun',
            #_delay=2000,
            bcNode=bc)
        if not indipendentQuery:
            linkedNode = self.pageSource().findNodeByAttr('frameCode', relatedTableHandlerFrameCode)
            linkedNode.value.dataController("bc.fireEvent('.stats.run_pivot_do',true);",_runQuery='^.runQueryDo',bc=bc)
        bc.dataRpc(None,self.ths_getPivotTable,
                    table=table,
                    relatedTable=relatedTable,
                    relation_field=relation_field,
                    relation_value=relation_value.replace('^','=') if relation_value else None,
                    mainfilter = '=.stats.filters.%s' %relation_field if relatedTable and not relation_value else None,
                    condition=condition,
                    filters='=.stats.filters',
                    stat_rows='=.stats.conf.rows',
                    stat_values='=.stats.conf.values',
                    stat_columns='=.stats.conf.columns',
                    stat_fields='=.stats.conf.fields',
                    stat_margins='=.stats.conf.margins',
                    relatedTableHandlerFrameCode=relatedTableHandlerFrameCode,
                    _lockScreen=dict(thermo=True),
                    _onCalling="""
                        if(!genro.dom.isVisible(_bcNode)){
                            return false;
                        }
                        if(relatedTableHandlerFrameCode){
                            var selectionAttributes = genro.wdgById(relatedTableHandlerFrameCode+'_grid').collectionStore().storeNode.currentAttributes()
                            var storeKw = objectExtract(selectionAttributes,'table,columns,checkPermissions,_sections');
                            objectUpdate(kwargs,selectionAttributes);
                            if(storeKw._sections){
                                th_sections_manager.onCalling(storeKw._sections,kwargs);
                            }
                        }
                        SET .stats.pivot_html = "";
                        if (!(stat_values && stat_values.len() && stat_rows && stat_rows.len())){
                            return false;
                        }
                    """,
                    outmode='^.stats.run_pivot_do',
                    _onResult="""
                        result = result || new gnr.GnrBag();
                        SET .stats.pivot_grid = result.popNode('pivot_grid')
                        SET .stats.pivot_html = result.getItem('pivot_html')
                        if(result.getItem('xls_url')){
                            genro.download(result.getItem('xls_url'));
                        }
                    """,_bcNode=bc,**condition_kwargs)
        
    @public_method
    def _ths_configurator(self,pane,table=None,relation_field=None,
                                relation_value=None,
                                relatedTableHandlerFrameCode=None,
                                relatedTable=None,source_filters=None,**kwargs):
        tc = pane.tabContainer()
        self._ths_configPivotGrids(tc.framePane(title='!!Pivot'),table=table)

        #self._ths_configFields(tc.borderContainer(title='!!Fields'),table=table)
        if relatedTable:
            tblobj = self.db.table(relatedTable)
            caption_field = tblobj.attributes.get('caption_field')
            if caption_field and relatedTable and not relation_value:
                self._ths_mainFilter(tc.contentPane(title='!!Main'),
                                relatedTableHandlerFrameCode=relatedTableHandlerFrameCode,
                                table=relatedTable,relation_field=relation_field) 
        if source_filters:
            self._ths_filters(tc.contentPane(title='!!Filters'),table=table,source_filters=source_filters)
        
        self._ths_reportParameters(tc.framePane(title='!!Report parameters'),table=table,relatedTableHandlerFrameCode=relatedTableHandlerFrameCode)

        #pane.dataController("""tc.switchPage(fields && fields.len()?0:1);""",
        #                    tc=tc.js_widget,fields='=#ANCHOR.stats.conf.fields',_onBuilt=True)

    @public_method
    def _ths_viewer(self,pane,table=None,relation_field=None,default_columns=None,
                    default_rows=None,default_values=None,relation_value=None,**kwargs):
        
        frame = pane.framePane()
        #frame.data('.stats.conf',self.ths_configPivotTreeData(table,relation_field=relation_field,
        #                                            default_columns=default_columns,
        #                                            default_rows=default_rows,
        #                                            default_values=default_values))
        self._ths_fill_filtersData(pane,table)

        sc = frame.center.stackContainer()
        iframe = self._ths_framehtml(sc.contentPane(title='Html'))
        #tc = center.tabContainer()
        gridframe = sc.framePane(frameCode='pivot_grid_#',title='!!Grid')
        gridId = '%s_grid' %gridframe.attributes['frameCode']
        gridframe.top.slotToolbar('*,searchOn,2',searchOn_searchCode=gridId)
        grid = gridframe.quickGrid('^.stats.pivot_grid',nodeId=gridId)
        #grid.tools('export')
        bar = frame.top.slotToolbar('2,stackButtons,*,margins,20,autorun,10,printStats,exportStats,5')
        bar.autorun.checkbox(value='^.stats.autorun',label='!!Autorun',
                            validate_onAccept="""
                                if(value){
                                    FIRE .stats.run_pivot;
                                }
                            """,default_value=True if relation_value else False)

        bar.margins.checkbox(value='^.stats.conf.margins',label='!!Margins')

        bar.printStats.slotButton('!!Print',action="genro.dom.iFramePrint(_iframe)",iconClass='iconbox print',
                                _iframe=iframe.js_domNode)
        bar.exportStats.slotButton('!!Export',iconClass='iconbox export',fire_xls='.stats.run_pivot_do')


    def _ths_mainFilter(self,pane,table=None,relatedTableHandlerFrameCode=None,relation_field=None):
        tblobj = self.db.table(table)
        caption_field = tblobj.attributes.get('caption_field')
        def struct(struct):
            r = struct.view().rows()
            if relation_field:
                r.cell(relation_field.replace('.','_').replace('@','_'), userSets=True, name=' ')
            r.fieldcell(caption_field,
                        width='100%',
                        name=tblobj.attributes['name_long'])
        pane.dataFormula("#ANCHOR.stats.filters.%s" %relation_field, 'mainfilterPkeys',
                        mainfilterPkeys='^#ANCHOR.stats._checked_mainfilter.%s' %relation_field)
        pane.frameGrid(datapath='.stats.mainfilter',table=table,
                        grid_store='%s_grid' %relatedTableHandlerFrameCode,
                        _newGrid=True,
                        grid_userSets='#ANCHOR.stats._checked_mainfilter',
                        struct=struct)

    def _ths_filters(self,pane,table=None,source_filters=None):
        tblobj = self.db.table(table)
        if not source_filters:
            return
        for n in source_filters:
            v = n.value
            label = n.label
            title = n.attr.get('title') or tblobj.column(label).attributes.get('name_long') or label
            titlepane = pane.titlePane(title=title,margin='2px')
            if isinstance(v,basestring):
                titlepane.checkBoxText(value='^.%s' %label,
                                        values='^#ANCHOR.stats.source_filters.%s' %label,
                                        datapath='.stats.filters',
                                        cols=1)
            if isinstance(v,Bag):
                titlepane.tree(storepath='.stats.source_filters.%s' %label,
                        checked_id='.stats.filters.%s' %label,
                        labelAttribute='caption',hideValues=True,
                        margin='2px')

    def _ths_fill_filtersData(self,pane,table):
        tblobj = self.db.table(table)
        if not hasattr(tblobj,'stats_filters'):
            return
        filtersbag = tblobj.stats_filters()
        pane.data('.stats.source_filters',filtersbag)
        for n in filtersbag:
            v = n.value
            label = n.label
            defaults = n.attr.get('defaults')
            pane.data('.stats.filters.%s' %label,defaults)

    def _ths_framehtml(self,pane,**kwargs):
        iframe = pane.div(_class='scroll-wrapper').htmliframe(height='100%',width='100%',border=0)
        pane.dataController("""var cw = _iframe.contentWindow;
                        var cw_body = cw.document.body;
                        if(genro.isMobile){
                            cw_body.classList.add('touchDevice');
                        }
                        var e = cw.document.createElement("link");
                        e.href = styleurl;
                        e.type = "text/css";
                        e.rel = "stylesheet";
                        //e.media = "screen";
                        cw.document.getElementsByTagName("head")[0].appendChild(e);
                        cw_body.classList.add('bodySize_'+genro.deviceScreenSize);
                        cw_body.classList.add('report_content');
                        cw_body.innerHTML = htmlcontent;
                    """ ,
                    _if='htmlcontent',
                    _else="""_iframe.contentWindow.document.body.innerHTML ="<div class='document'>Vuoto</div>" """,
                    _iframe=iframe.js_domNode,styleurl=self.getResourceUri('js_plugins/statspane/report.css', add_mtime=True),
                    htmlcontent='^.stats.pivot_html')
        return iframe       

    def ths_getDataframe(self,table,filters=None,mainfilter=None,relatedTable=None,
                                relation_field=None,relation_value=None,
                                maintable=None,columns=None,condition=None,condition_kwargs=None,
                                where=None,
                                limit=None,
                                extraPars=None,
                                customOrderBy=None,
                                **kwargs):
        df = GnrDbDataframe('current_df_%s' %table.replace('.','_'),self.db,thermocb=self.utils.quickThermo)
        related_pkeys = None
        if mainfilter:
            where = None
        elif isinstance(where,Bag):
            if relatedTable and relation_field:
                relatedTableObj = self.db.table(relatedTable)
                where, kwargs = self.app._decodeWhereBag(relatedTableObj, where, kwargs)
                kwargs['filters_%s' %relation_field] =  [r['pkey'] for r in relatedTableObj.query(where=where, **kwargs).fetch()]
                where = ' $%s IN :filters_%s' %(relation_field,relation_field)
            else:
                if extraPars:
                    kwargs.update(extraPars.asDict(ascii=True))
                where, kwargs = self.app._decodeWhereBag(self.db.table(table), where, kwargs)
                if limit:
                    kwargs['limit'] = limit
                if customOrderBy:
                    order_by = []
                    for fieldpath,sorting in customOrderBy.digest('#v.fieldpath,#v.sorting'):
                        fieldpath = '$%s' %fieldpath if not fieldpath.startswith('@') else fieldpath
                        sorting = 'asc' if sorting else 'desc'
                        order_by.append('%s %s' %(fieldpath,sorting))
                    kwargs['order_by'] = ', '.join(order_by)

        elif relation_value:
            where = ' $%s IN :filters_%s' %(relation_field,relation_field)
            kwargs['filters_%s' %relation_field] = [relation_value]
        where = [where] if where else []
        where_kwargs = kwargs
        if condition:
            where.append(condition)
            where_kwargs.update(condition_kwargs)
        if filters:
            for fkey,filter_pkeys in list(filters.items()):
                if filter_pkeys:
                    where.append(' $%s IN :filters_%s' %(fkey,fkey))
                    where_kwargs['filters_%s' %fkey] = filter_pkeys.split(',')
        df.query(table,where=' AND '.join(where),columns=columns,**where_kwargs)
        return df
        
        
    def ths_configPivotTreeData(self,table,relation_field=None,
                                default_columns=None,
                                default_rows=None,
                                default_values=None):
        df = GnrDbDataframe('current_df_%s' %table.replace('.','_'),self.db)
        
        return df.configPivotTree(self.db.table(table),
                                default_values=default_values,
                                default_rows=default_rows,
                                default_columns=default_columns)

    @public_method
    def ths_getPivotTable(self,df=None,table=None,relation_field=None,relation_value=None,
                        filters=None,mainfilter=None,
                        stat_rows=None,stat_columns=None,
                        stat_values=None,stat_fields=None,stat_margins=None,outmode=None,
                        filename=None,condition=None,where=None,
                        **kwargs):
        condition_kwargs= dictExtract(kwargs,'condition_')
        stats_tableobj = self.db.table(table)
        main_tableobj = stats_tableobj.column(relation_field).relatedColumn().table if relation_field else stats_tableobj
        if not df:
            stat_values = stat_values or Bag()
            stat_columns = stat_columns or Bag()
            stat_rows = stat_rows or Bag()
            columns = []
            for f,asname in stat_fields.digest('#v.field,#v.name'):
                if not f:
                    continue
                f = '$%s' %f if not f.startswith('@') else f
                if asname:
                    f = '%s AS %s' %(f,asname)
                columns.append(f)
            df = self.ths_getDataframe(table,filters=filters,mainfilter=mainfilter,
                                        relation_field=relation_field,
                                        relation_value=relation_value,
                                        maintable=main_tableobj.fullname,
                                        columns=','.join(set(columns)),
                                        condition=condition,
                                        where=where,
                                        condition_kwargs=condition_kwargs,
                                        **kwargs)
            pddf = df.dataframe
            if not len(pddf):
                return
            for fv in list(stat_fields.values()):
                if not fv['calculated']:
                    continue
                if fv['value']:
                    pddf.eval('%(name)s = %(value)s' %fv,inplace=True) 
            if not df:
                return    
        pivotdf,bagresult = df.pivotTableGrid(index=stat_rows if stat_rows else None,
                                            values=stat_values if stat_values else None,
                                            columns=stat_columns if stat_columns else None,
                                            margins=stat_margins)
        result = Bag()
        result['pivot_html'] = pivotdf.to_html()
        result['pivot_grid'] = bagresult
        if outmode=='xls':
            filename = filename or 'stats_%s' %main_tableobj.name
            path = self.db.application.site.getStaticPath('page:xls_stats','%s.xls' %filename,autocreate=-1)
            writer = pd.ExcelWriter(path)
            pivotdf.to_excel(writer,'Sheet1')
            writer.save()
            result['xls_url'] = self.db.application.site.getStaticUrl('page:xls_stats','%s.xls' %filename)
        return result   

    
    def _ths_branchgrid(self,parent,branch,addrow=False,delrow=True,**kwargs):
        frameCode = 'V_th_conf_%s' %branch

        def struct(struct):
            r = struct.view().rows()
            r.cell('caption',width='100%',name='!!Field')
            if branch=='values':
                r.cell('aggregators',edit=dict(tag='checkboxtext',values='sum,mean,min,max,count',cols=1),
                                        width='15em',name='Aggregate')


        frame = parent.bagGrid(frameCode=frameCode,title=branch.title(),
                                datapath='#ANCHOR.stats.%s' %frameCode,
                                struct=struct,storepath='#ANCHOR.stats.conf.%s' %branch,
                                pbl_classes=True if branch=='values' else '*',
                                grid_selfDragRows=True,
                                addrow=addrow,delrow=delrow,
                                margin='2px',**kwargs)
        if branch!='fields':
            menupath = '#ANCHOR.stats.controller.%s_menu' %(branch if branch=='values' else 'index')
            frame.top.bar.replaceSlots('delrow','delrow,addrow',
                                addrow_defaults=menupath)
            frame.grid.attributes.update(
                selfsubscribe_addrow="""
                var storebag = this.widget.storebag();
                var newrow = new gnr.GnrBag(p_0.opt);
                newrow.setItem('caption',newrow.pop('label'));
                newrow.pop('fullpath');
                storebag.setItem(newrow.getItem('name'),newrow);
                """
            )

        return frame

    def _ths_reportParameters(self,frame,table=None,relatedTableHandlerFrameCode=None):
        fb = frame.formbuilder()
        fb.dbSelect(value='^#ANCHOR.stats.conf.report_query',
                    lbl='Query',dbtable='adm.userobject',
                    condition='$objtype=:obj AND $tbl=:tbl',
                    rowcaption='$description',
                    alternatePkey='code',
                    condition_obj='query',condition_tbl=table,hasDownArrow=True,
                    width='10em')

        fb.dataController("""
        if(relatedTableHandlerFrameCode){
            genro.getFrameNode(relatedTableHandlerFrameCode).setRelativeData('.query.currentQuery',report_query);
        }else{

        }
        
        """,relatedTableHandlerFrameCode=relatedTableHandlerFrameCode,
            report_query='^#ANCHOR.stats.conf.report_query',_if="report_query")

    def _ths_configPivotGrids(self,frame,table=None):
        bar = frame.top.slotToolbar('*,editFields,5')
        bc = frame.center.borderContainer()
        bc.dataController("""
        var index_menu = new gnr.GnrBag();
        var values_menu = new gnr.GnrBag();
        fields.getNodes().forEach(function(n){
            var dtype = n.getValue().getItem('dtype');
            var nattr = n.getValue().asDict();
            if(rows.getNode(n.label) || columns.getNode(n.label) || values.getNode(n.label)){
                return;
            }
            if(dtype=='N' || dtype=='L' || dtype=='I'){
                values_menu.setItem(n.label,null,nattr);
            }
            index_menu.setItem(n.label,null,nattr);
        });
        SET .stats.controller.index_menu = index_menu;
        SET .stats.controller.values_menu = values_menu;
        """,fields='^.stats.conf.fields',
            rows='^.stats.conf.rows',
            columns='^.stats.conf.columns',
            values='^.stats.conf.values',
            _if='fields',_onBuilt=True,_delay=10)
        bar.editFields.slotButton('Fields',action='dlg.show();',
                                    dlg=self._ths_confFieldsDialog(bc,table=table).js_widget)
        
        self._ths_branchgrid(bc,'rows',region='top',height='33%')
        self._ths_branchgrid(bc,'values',region='bottom',height='33%')
        self._ths_branchgrid(bc,'columns',region='center')

    def _ths_confFieldsDialog(self,parent,table=None):
        dlg = parent.dialog(title='!!Edit fields',windowRatio=.8,closable=True,noModal=True)
        bc = dlg.borderContainer()
        frame = bc.bagGrid(frameCode='V_th_conf_fields_#',datapath='#ANCHOR.st_grid',title='!!Fields',
                                storepath='=#ANCHOR.stats.conf.fields',
                                struct=self._ths_varsgrid_struct,
                                parentForm=False,grid_masterColumn='name',
                                addrow=True,delrow=True,
                                default_calculated=True,
                                grid_gridplugins=False,
                                region='center')
        frame.left.slotBar('5,fieldsTree,*',
                        fieldsTree_table=table,
                        fieldsTree_dragCode='fieldvars',
                        border_right='1px solid silver',
                        closable=True,width='150px',fieldsTree_height='100%',splitter=True)
        grid = frame.grid

        grid.dataController("""
        var r = grid.rowByIndex(rowIndex);
        SET .currformula.shortcuts = th_stats_js.getFormulaShortcuts(this,r.name);
        SET .currformula.title = 'Edit '+r.name;
        SET .currformula.value = r.value;
        SET .currformula.rowIndex = rowIndex;
        dlgformula.widget.show();
        """,grid=grid.js_widget,
                        rowIndex='^.editFormulaCell',
                        dlgformula=self.ths_formulaEditor(grid))
        grid.data('.table',table)
        grid.dragAndDrop(dropCodes='fieldvars')
        grid.dataController("""var caption = data.fullcaption;
                                var field = data.fieldpath;
                                var pkey = field.replace(/\W/g,'_');
                                var dtype = data.dtype;
                                grid.gridEditor.addNewRows([{'field':field,
                                                            value:field,
                                                            dtype:dtype,
                                                            caption:caption,
                                                            pkey:pkey,
                                                            name:pkey,
                                                            calculated:false,
                                                            virtual_column:data.virtual_column,
                                                            required_columns:data.required_columns}]);
                                                            """,
                                data="^.dropped_fieldvars",grid=grid.js_widget) 
        return dlg

    def ths_formulaEditor(self,grid):
        dlg = grid.dialog(title='^.currformula.title')
        frame = dlg.framePane(height='300px',width='400px')
        ta = frame.center.simpleTextArea(value='^.currformula.value')
        ta.menu(storepath='.currformula.shortcuts',_class='smallMenu',
                action="genro.dom.setTextInSelection($2,$1.formula);")
        bar = frame.bottom.slotBar('*,cancel,10,confirm,2',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton('Cancel',action="dlg.hide()",dlg=dlg.js_widget)
        bar.confirm.slotButton('Confirm',action="""
                                                grid.gridEditor.setCellValue(rowIndex,'value',formula);
                                                var guessDtype = 'T';
                                                if(formula.match(/[\+\-\*\\/]/im)){
                                                    guessDtype = 'N';
                                                }
                                                grid.gridEditor.setCellValue(rowIndex,'dtype',guessDtype);
                                                dlg.hide();
                                                    """,
                                        dlg=dlg.js_widget,
                                        grid=grid.js_widget,
                                        rowIndex='=.currformula.rowIndex',
                                        formula='=.currformula.value')
        return dlg



    def _ths_varsgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('name', name='Name', width='15em',edit=dict(validate_notnull=True))
        r.cell('calculated',dtype='B',width='2em',name=' ',format_trueclass='iconbox arrow_left',format_falseclass=' ')
        
        r.cell('value', name='Value', width='100%',
                            edit=True,
                            editOnOpening="""
                            this.grid.sourceNode.fireEvent('.editFormulaCell',rowIndex);
                            """,
                            editDisabled='=#ROW.calculated?=!#v')
        r.cell('caption', name='Caption', width='15em',edit=True)
        r.cell('dtype', name='Dtype', width='4em',edit=dict(tag='filteringSelect',values='T,N,L,D,DH,H'))

        #r.cell('format', name='Format', width='10em')
        #r.cell('mask', name='Mask', width='20em',edit=True)
   

class PivotTableViewer(BaseComponent):
    py_requires = 'th/th_stats:TableHandlerStats'
    @struct_method
    def ptv_pivotTableViewer(self,parent,table=None,statIdentifier=None,
                        condition=None,outmode=None,datapath=None,region=None,title=None,nodeId=None,**kwargs):
        bc = parent.borderContainer(datapath=datapath,region=region,title=title,nodeId=nodeId)
        userobject_tbl = self.db.table('adm.userobject')
        data,metadata = userobject_tbl.loadUserObject(code=statIdentifier, 
                                            objtype='pnd_simple',
                                            tbl=table)
        if not condition and data['report_query']:
            where,where_metadata = userobject_tbl.loadUserObject(code=data['report_query'], 
                                            objtype='query',
                                            tbl=table)
            customOrderBy = None
            limit = None
            queryPars = None
            if where['where']:
                limit = where['queryLimit']
                customOrderBy = where['customOrderBy']
                queryPars = where.pop('queryPars')
                bc._queryPars = queryPars
                extraPars = where.pop('extraPars')
                where = where.pop('where')
                bc.data('.query.where',where)
                bc.data('.query.queryPars',queryPars)
                bc.data('.query.customOrderBy',customOrderBy)
                bc.data('.query.extraPars',extraPars)
                bc.data('.query.limit',limit)
            bc.queryPars = queryPars

        bc.data('.stats.conf',data)
      
        bc.dataRpc(None,self.ths_getPivotTable,
                    table=table,
                    condition=condition,
                    where='=.query.where',
                    queryPars='=.query.queryPars',
                    limit='=.query.limit',
                    extraPars='=.query.extraPars',
                    customOrderBy='=.query.customOrderBy',

                    stat_rows='=.stats.conf.rows',

                    stat_values='=.stats.conf.values',
                    stat_columns='=.stats.conf.columns',
                    stat_fields='=.stats.conf.fields',
                    stat_margins='=.stats.conf.margins',
                    _lockScreen=dict(thermo=True),
                    _onCalling="""
                        SET .stats.pivot_html = "";
                        if (!(stat_values && stat_values.len() && stat_rows && stat_rows.len())){
                            return false;
                        }
                    """,
                    _if='',
                    outmode=outmode,
                    _onResult="""
                        result = result || new gnr.GnrBag();
                        SET .stats.pivot_grid = result.popNode('pivot_grid')
                        SET .stats.pivot_html = result.getItem('pivot_html')
                        if(result.getItem('xls_url')){
                            genro.download(result.getItem('xls_url'));
                        }
                    """,**kwargs)
        iframe = self._ths_framehtml(bc.contentPane(region='center'))
        return bc

