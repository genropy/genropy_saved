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
from gnr.core.gnrdict import dictExtract
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs

class IncludedView(BaseComponent):
    """IncludedView allows you to manage data of the table in relation many to many.
    includedViewBox is the main method of this class."""
    js_requires = 'public'
    py_requires = 'gnrcomponents/framegrid:FrameGrid,foundation/macrowidgets:FilterBox'
        
    def includedViewBox(self, parentBC, nodeId=None, table=None, datapath=None,
                        storepath=None, selectionPars=None, formPars=None, label=None, caption=None, footer=None,
                        add_action=None, add_class='buttonIcon icnBaseAdd', add_enable='^form.canWrite',
                        del_action=None, del_class='buttonIcon icnBaseDelete', del_enable='^form.canWrite',
                        upd_action=None, upd_class='buttonIcon icnBaseEdit', upd_enable='^form.canWrite',
                        close_action=None, close_class='buttonIcon icnTabClose',
                        print_action=None, print_class='buttonIcon icnBasePrinter',
                        pdf_action=None, pdf_class='buttonIcon icnBasePdf', pdf_name=None,
                        export_action=None, export_class='buttonIcon icnBaseExport',
                        tools_action=None, tools_class='buttonIcon icnBaseAction',
                        tools_enable='^form.canWrite', tools_lbl=None,
                        lock_action=False, tools_menu=None, _onStart=False,
                        filterOn=None, pickerPars=None, centerPaneCb=None,
                        editorEnabled=None, parentLock='^status.locked', reloader=None, externalChanges=None,
                        addOnCb=None, zoom=True, hasToolbar=False,
                        canSort=True, configurable=None, dropCodes=None,
                        **kwargs):
        """This method returns a grid (includedView) for viewing and selecting rows from a many
        to many table related to the main table, and it returns the widget that allows to edit data.
        You can edit data of a single row (record) using a form (formPars), or picking some rows
        from another table with the picker widget (pickerPars).
        The form can be contained inside a dialog or a contentPane and is useful to edit a single record.
        If the data is stored inside another table you should use the picker to select the rows from that table.
        
        :param parentBC: MANDATORY - parentBC is a :ref:`bordercontainer`
                         
                         .. note:: The includedViewBox and its sons can only accept the borderContainer
                                   layout container
                                   
        :param nodeId: the includedViewbox's Id. For more information, check :ref:`nodeid` page
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        :param storepath: the path of the data of the includedViewBox
        :param selectionPars: TODO
                              
                              **selectionPars parameters**:
                              
                              * applymethod: TODO
                              * where: the sql "WHERE" clause. For more information check the
                                :ref:`sql_where` section.
        :param formPars: (dict) it contains all the params of the widget who hosts the form.
                         .
                         
                            **formPars parameters:**
                            
                            * mode: `dialog` / `pane`
                            * height: the dialog's height
                            * width: the dialog's width
                            * formCb: MANDATORY - callback method used to create the form
                            
                             **formCb parameters:**
                             
                             * formBorderCont: a :ref:`bordercontainer` used as root for the formCb's construction.
                             * datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                               For more information, check the :ref:`datapath` and the :ref:`datastore` pages.
                             * region: 'center' of the pane/borderContainer where you place it into
                             * toolbarHandler: OPTIONAL - a callback for the form toolbar
                             * title: MANDATORY - for dialog mode
                             * pane: OPTIONAL - pane of the form input
            
        :param label: (string) allow to create a label for the includedView
        :param caption: TODO
        :param footer: TODO
        :param add_action: (boolean) allow the insertion of a row in the includedView
        :param add_class: the css class of the add button
        :param add_enable: a path to enable/disable add action
        :param del_action: (boolean) allow the deleting of a row in the includedView
        :param del_class: the css class of the delete button
        :param del_enable: a path to enable/disable del action
        :param upd_action: TODO
        :param upd_class: TODO
        :param upd_enable: TODO
        :param close_action: (boolean) adding closing button in tooltipDialog
        :param close_class: css class of close button
        :param print_action: TODO
        :param print_class: TODO
        :param pdf_action: TODO
        :param pdf_class: TODO
        :param pdf_name: TODO
        :param export_action: TODO
        :param export_class: TODO
        :param tools_action: TODO
        :param tools_class: TODO
        :param tools_enable: TODO
        :param tools_lbl: TODO
        :param lock_action: an optional parameter; TODO
        :param tools_menu: TODO
        :param _onStart: boolean. If ``True``, the controller is executed only after that all
                         the line codes are read
        :param filterOn: (boolean, only for picker) allow the filter into the picker grid
        :param pickerPars: (dict) it contains all the params of the tooltip dialog which host the
                           picker grid
                           
                           **Parameters:**
                           
                           * height: height of the tooltipdialog
                           * width: width of the tooltipdialog
                           * label: label of the tooltipdialog
                           * table: MANDATORY - the table of the picker grid. From this table you can pick a row
                                    for the many to many table you handle
                           * columns: MANDATORY - columns of the picker grid
                           * nodeId: MANDATORY - id for the picker
                           * filterOn: the columns on which to apply filter
                           
        :param centerPaneCb: TODO
        :param editorEnabled: TODO
        :param parentLock: TODO
        :param reloader: TODO
        :param externalChanges: TODO
        :param addOnCb: TODO
        :param zoom: It allows to open the linked record in a :ref:`dialog`.
                     For further details, check the :ref:`zoom` documentation page
        :param hasToolbar: TODO
        :param canSort: TODO
        :param fromPicker_target_fields: allow to bind the picker's table. columns to the includedView
                                         columns of the many to many table.
        :param fromPicker_nodup_field: if this column value is present in the includedView it allows to
                                       replace that row instead of adding a duplicate row
        :param \*\*kwargs: **autowidth**, **storepath**, etc"""
        if storepath:
            assert not storepath.startswith('^') and not storepath.startswith('='),\
            "storepath should be a plain datapath, no ^ or ="
        if not datapath:
            if storepath.startswith('.'):
                inherited_attributes = parentBC.parentNode.getInheritedAttributes()
                #assert inherited_attributes.has_key('sqlContextRoot'),\
                #'please specify an absolute storepath, if sqlContextRoot is not available'
                #storepath = '%s%s' % (inherited_attributes['sqlContextRoot'], storepath)
                storepath = '#FORM.record%s' %storepath
        viewPars = dict(kwargs)
        gridId = nodeId or self.getUuid()
        viewPars['nodeId'] = gridId
        if dropCodes:
            for dropCode in dropCodes.split(','):
                mode = 'grid'
                if ':' in dropCode:
                    dropCode, mode = dropCode.split(':')
                dropmode = 'dropTarget_%s' % mode
                viewPars[dropmode] = '%s,%s' % (viewPars[dropmode], dropCode) if dropmode in viewPars else dropCode
                viewPars['onDrop_%s' % dropCode] = 'FIRE .dropped_%s = data' % dropCode
                viewPars['onCreated'] = """dojo.connect(widget,'_onFocus',function(){genro.publish("show_palette_%s")})""" % dropCode #provo?si
                # 
        controllerPath = datapath or 'grids.%s' % gridId
        storepath = storepath or '.selection'
        viewPars['storepath'] = storepath
        viewPars['controllerPath'] = controllerPath
        controller = parentBC.dataController(datapath=controllerPath)
        assert not 'selectedIndex' in viewPars
        viewPars['selectedIndex'] = '^.selectedIndex'
        assert not 'selectedLabel' in viewPars
        if not viewPars.get('selectedId'):
            viewPars['selectedId'] = '^.selectedId'
        viewPars['selectedLabel'] = '^.selectedLabel'
        label_pars = dict([(k[6:], kwargs.pop(k)) for k in kwargs.keys() if k.startswith('label_')])
        label_pars['_class'] = label_pars.pop('class', None) or (not hasToolbar and 'pbl_viewBoxLabel')
        box_pars = dict([(k[4:], kwargs.pop(k)) for k in kwargs.keys() if k.startswith('box_')])
        box_pars['_class'] = (box_pars.pop('class', None) or 'pbl_viewBox')
        if label is not False:
            gridtop = parentBC.contentPane(region='top', datapath=controllerPath, overflow='hidden',childname='top',
                                           nodeId='%s_top' % gridId, **label_pars)
            if hasToolbar is True:
                gridtop = gridtop.toolbar(_class='pbl_viewBoxToolbar')
            gridtop_left = gridtop.div(float='left')
            if callable(label):
                label(gridtop_left)
            else:
                gridtop_left.div(label, margin_top='2px', float='left')
            gridtop_right = gridtop.div(float='right',childname='right')
            if filterOn:
                gridtop_filter = gridtop_right.div(float='left', margin_right='5px')
                self.gridFilterBox(gridtop_filter, gridId=gridId, filterOn=filterOn, table=table)
            if print_action or export_action or tools_menu or tools_action or pdf_action:
                gridtop_actions = gridtop_right.div(float='left', margin_right='5px')
                self._iv_gridAction(gridtop_actions, print_action=print_action, export_action=export_action,
                                    export_class=export_class, print_class=print_class, tools_class=tools_class,
                                    tools_menu=tools_menu, tools_action=tools_action, pdf_action=pdf_action,
                                    pdf_class=pdf_class, pdf_name=pdf_name, table=table, gridId=gridId,
                                    tools_enable=tools_enable, tools_lbl=tools_lbl)
            if add_action or del_action or upd_action:
                gridtop_add_del = gridtop_right.div(float='left', margin_right='5px',childname='add_del')
                self._iv_gridAddDel(gridtop_add_del, add_action=add_action,
                                    del_action=del_action, upd_action=upd_action,
                                    upd_class=upd_class, upd_enable=upd_enable,
                                    add_class=add_class, add_enable=add_enable,
                                    del_class=del_class, del_enable=del_enable,
                                    pickerPars=pickerPars,
                                    formPars=formPars, gridId=gridId)
            if lock_action:
                gridtop_lock = gridtop_right.div(float='left', margin_right='5px')
                self._iv_gridLock(gridtop_lock, lock_action=lock_action)
                
        if footer:
            assert callable(footer), 'footer param must be a callable'
            footerPars = dict([(k[7:], v) for k, v in kwargs.items() if k.startswith('footer_')])
            if not 'height' in footerPars:
                footerPars['height'] = '18px'
            if not '_class'in footerPars:
                footerPars['_class'] = 'pbl_roundedGroupBottom'
            gridbottom = parentBC.contentPane(region='bottom',
                                              datapath=controllerPath, **footerPars)
            footer(gridbottom)
            
        self._iv_IncludedViewController(controller, gridId, controllerPath, table=table)
        if centerPaneCb:
            gridcenter = getattr(self, centerPaneCb)(parentBC, region='center', datapath=controllerPath, **box_pars)
        else:
            gridcenter = parentBC.contentPane(region='center', datapath=controllerPath, **box_pars)
        viewPars['structpath'] = viewPars.get('structpath') or '.struct'  or 'grids.%s.struct' % nodeId
        if filterOn is True:
            gridcenter.dataController("""var colsMenu = new gnr.GnrBag();
                                         struct.forEach(function(n){
                                             colsMenu.setItem(n.label, null, {col:n.attr.field, caption:n.attr.name})
                                          });
                                          SET .flt.colsMenu = colsMenu;""",
                                      struct='^%s.view_0.row_0' % viewPars['structpath'])
        if parentLock:
            gridcenter.dataFormula(".editorEnabled", "parentLock==null?false:!parentLock", parentLock=parentLock)
        elif parentLock is False:
            editorEnabled = True
        if caption:
            innerbc = gridcenter.borderContainer()
            caption_pars = dictExtract(viewPars, 'caption_', pop=True)
            innerbc.contentPane(region='top').div(caption, **caption_pars)
            gridcenter = innerbc.contentPane(region='center')
        view = gridcenter.includedView(extension='includedViewPicker', table=table,
                                       editorEnabled=editorEnabled or '^.editorEnabled',
                                       reloader=reloader, **viewPars)
        if addOnCb:
            addOnCb(gridcenter)
        if _onStart:
            controller.dataController("FIRE .reload", _onStart=True)
        if externalChanges:
            externalChangesTypes = ''
            if isinstance(externalChanges, basestring):
                if ':' in externalChanges:
                    externalChanges, externalChangesTypes = externalChanges.split(':')
                    if externalChanges == '*':
                        externalChanges = True
            subscribed_tables = [t for t in getattr(self, 'subscribed_tables', '').split(',') if t]
            assert  table in subscribed_tables, "table %s must be subscribed to get externalChanges" % table
            event_path = 'gnr.dbevent.%s' % table.replace('.', '_')
            pars = dict()
            conditions = list()
            if isinstance(externalChanges, basestring):
                for fld in externalChanges.split(','):
                    fldname, fldpath = fld.split('=')
                    conditions.append('genro.isEqual(curr_%s,event_%s)' % (fldname, fldname))
                    pars['event_%s' % fldname] = '=%s.%s' % (event_path, fldname)
                    pars['curr_%s' % fldname] = '=%s' % fldpath
            if externalChangesTypes:
                conditions.append('evtypes.indexOf(evtype)>=0')
                pars['evtypes'] = externalChangesTypes
                pars['evtype'] = '=%s?dbevent' % event_path
            gridcenter.dataController("FIRE .reload;", _if=' && '.join(conditions),
                                      _fired='^%s' % event_path, **pars)
        if selectionPars:
            self._iv_includedViewSelection(gridcenter, gridId, table, storepath, selectionPars, controllerPath)
            
        if formPars:
            formPars.setdefault('pane', gridcenter)
            self._includedViewForm(controller, controllerPath, view, formPars)
            
        if pickerPars:
            pickerPars.setdefault('pane', gridcenter)
            self._iv_Picker(controller, controllerPath, view, pickerPars)
        return view
        
    def _iv_gridLock(self, pane, lock_action=None):
        if lock_action is True:
            spacer = pane.div(float='right', width='30px', height='20px', position='relative')
            spacer.button(label='^.status.lockLabel', fire='.status.changelock', iconClass="^.status.statusClass",
                          showLabel=False)
                          
    def _iv_gridAddDel(self, pane, add_action=None, del_action=None, upd_action=None, upd_class=None, upd_enable=None,
                       add_class=None, add_enable=None, del_class=None, del_enable=None, pickerPars=None, formPars=None,
                       gridId=None):
        if del_action:
            if del_action is True:
                del_action = 'FIRE .delSelection'
            pane.div(float='right', _class=del_class, connect_onclick=del_action,
                     margin_right='2px', visible=del_enable)
        if add_action:
            if add_action is True:
                if pickerPars:
                    add_action = 'FIRE .showPicker'
                elif formPars:
                    add_action = 'FIRE .showRecord; FIRE .addRecord =$1;'
                else:
                    add_action = 'FIRE .addRecord =$1;FIRE .editRow=1000;'
            elif add_action=='menu':
                add_action=None
            pane.div(float='right', _class=add_class, connect_onclick=add_action,childname='addButton',
                     margin_right='2px', visible=add_enable)
        if upd_action:
            if upd_action is True:
                upd_action = 'FIRE .showRecord'
            pane.div(float='right', _class=upd_class, connect_onclick=upd_action,
                     margin_right='2px', visible=upd_enable)
                     
    def _iv_gridAction(self, pane, print_action=None, export_action=None, export_mode=None, tools_menu=None, tools_class=None,
                       tools_action=None, export_class=None, print_class=None, pdf_action=None, pdf_class=None,
                       pdf_name=None, table=None, gridId=None, tools_enable=None, tools_lbl=None, **kwargs):
        if print_action:
            if print_action is True:
                print_action = 'FIRE .print;'
            pane.div(float='left', margin_right='7px', _class=print_class, connect_onclick=print_action)
            
        if export_action:
            if export_action is True:
                export_action = 'export'
                export_mode = 'xls'
            export_action = 'FIRE .iv_action={action:"%s",export_mode:"%s"};' % (export_action, export_mode)
            pane.div(float='left', margin_right='7px', _class=export_class, connect_onclick=export_action)
            
        if tools_menu:
            storepath = '.toolsmenu'
            if isinstance(tools_menu, basestring):
                storepath = tools_menu
            else:
                pane.data('.toolsmenu', tools_menu)
            btn = pane.dropDownButton('!!Edit', showLabel=False, float='left',
                                      iconClass=tools_class, margin_right='7px', baseClass='no_background')
            btn.menu(storepath=storepath, modifiers='*', _class='smallmenu',
                     action='this.fireEvent(item.attr.fire_path);')
        elif tools_action:
            if tools_action is True:
                tools_action = 'FIRE .reload'
            tool_block = pane.div(margin='0px', border_spacing='0px', visible=tools_enable)
            tool_block.div(float='left', _class=tools_class, connect_onclick=tools_action)
            if tools_lbl:
                tool_block.div(tools_lbl, margin_left='5px', width='70px', font_size='0.9em')
                
        if pdf_action:
            pane.dataController("""
                             var record = genro.wdgById(gridId).storebag();
                             var docName = docName || record;
                             var docName=docName.replace('.', '');
                             var downloadAs =docName +'.pdf';
                             var parameters = {'recordId':null,
                                               'downloadAs':downloadAs,
                                               'pdf':true,
                                               'respath':respath,
                                               'rebuild':rebuild,
                                               'table':table};
                             //objectUpdate(parameters,moreargs);
                             genro.rpcDownload("callTableScript",parameters);
                             """,
                                _fired='^.downloadPdf',
                                #runKwargs = '=%s' % runKwargsPath, #aggiunto
                                docName='%s' % pdf_name,
                                table=table, gridId=gridId, respath=pdf_action,
                                rebuild=True)
            pane.div(float='left', _class=pdf_class, connect_onclick='FIRE .downloadPdf')
            
    def _iv_includedViewSelection(self, pane, gridId, table, storepath, selectionPars, controllerPath):
        #assert table
        assert not 'columnsFromView' in selectionPars
        assert not 'nodeId' in selectionPars
        #assert 'where' in selectionPars
        selectionPars['nodeId'] = "%s_store" % gridId
        if table:
            selectionPars['table'] = table
            selectionPars['columns'] = selectionPars.get('columns') or '=.columns'
            
        method = selectionPars.pop('method', 'app.getSelection')
        destpath = None
        if 'destpath' not in selectionPars:
            destpath = storepath
        pane.dataRpc(destpath, method, **selectionPars)
        
    def _iv_IncludedViewController(self, controller, gridId, controllerPath, table=None):
        loadingParameters = None
        if table:
            loadingParameters = '=gnr.tables.%s.loadingParameters' % table.replace('.', '_')
        controller.dataController("""var grid = genro.wdgById(gridId);
                                     grid.addBagRow('#id', '*', grid.newBagRow(),event);
                                     """,
                                  event='^.addRecord',
                                  gridId=gridId)
        #loadingParameters=loadingParameters)
        delScript = """PUT .selectedLabel= null;
                       var grid = genro.wdgById(gridId);
                       var nodesToDel = grid.delBagRow('*', delSelection);
                       FIRE .onDeletedRow;"""
                       
        controller.dataController(delScript, _fired='^.delRecord', delSelection='^.delSelection',
                                  idx='=.selectedIndex', gridId=gridId)
        controller.dataController("""genro.wdgById(gridId).editBagRow(null,fired);""", fired='^.editRow', gridId=gridId)
        controller.dataController("genro.wdgById(gridId).printData();", fired='^.print', gridId=gridId)
        #controller.dataController("genro.wdgById(gridId).exportData(mode, export_method);" ,
        #                           mode='^.export', export_method='=.export_method', gridId=gridId)
        controller.dataController("""
                                var grid = genro.wdgById(gridId);
                                var method = objectPop(action,"method") || "app.includedViewAction";
                                var kwargs = objectUpdate({},action);
                                kwargs['selectedRowIdx'] = grid.getSelectedRowidx();
                                kwargs['table'] =grid.sourceNode.attr.table;
                                kwargs['datamode'] = grid.datamode;
                                kwargs['struct'] = grid.structbag();
                                kwargs['data'] = grid.storebag();
                                var cb = function(result){genro.download(result);};
                                kwargs['meta'] = objectExtract(grid.sourceNode.attr, 'meta_*', true);
                                genro.rpc.remoteCall(method, kwargs, null, 'POST', null,cb);
                            """,
                                  gridId=gridId, action='^.iv_action')
                                  
        controller.dataController("genro.wdgById(gridId).reload(true);", _fired='^.reload', gridId=gridId)
        #controller.dataController("""SET .selectedIndex = null;
        #                             PUT .selectedLabel= null;""",
        #                          _fired="^gnr.forms.formPane.saving")
        
    def _includedViewForm(self, controller, controllerPath, view, formPars):
        viewPars = view.attributes
        gridId = viewPars['nodeId']
        storepath = viewPars['storepath']
        assert not 'connect_onCellDblClick' in viewPars
        viewPars['connect_onCellDblClick'] = """var grid = this.widget;
                                                var cell = grid.getCell($1.cellIndex);
                                                if (!grid.gridEditor || !(cell.field in grid.gridEditor.columns)){
                                                    FIRE .showRecord = true;
                                                }
                                                """
                                                
        formHandler = getattr(self, '_iv_Form_%s' % formPars.get('mode', 'dialog'))
        
        toolbarPars = dict([(k, formPars.pop(k, None)) for k in
                            ('add_action', 'add_class', 'add_enable', 'del_action', 'del_class', 'del_enable',)])
        toolbarPars['controllerHandler'] = formPars.pop('controllerHandler', '_iv_FormStaticController')
        formHandler(formPars, storepath, controller, controllerPath, gridId, toolbarPars)
        
    def _iv_Form_inline(self, formPars, storepath, controller, controllerPath, gridId, toolbarPars):
        getattr(self, toolbarPars['controllerHandler'])(controller, gridId)
        
    def _iv_FormToolbar(self, parentBC, controller, controllerPath, controllerHandler, gridId,
                        add_action=None, add_class=None, add_enable=None,
                        del_action=None, del_class=None, del_enable=None, ):
        pane = parentBC.contentPane(region='top', height='28px', datapath=controllerPath, overflow='hidden')
        getattr(self, controllerHandler)(controller, gridId)
        tb = pane.toolbar()
        if del_action:
            if del_action is True:
                del_action = 'FIRE .delRecord=true'
            del_class = del_class or 'buttonIcon icnBaseDelete'
            del_enable = del_enable or '^form.canWrite'
            tb.button('!!Delete', float='right', action=del_action, iconClass=del_class,
                      showLabel=False, visible=del_enable)
        if add_action:
            if add_action is True:
                add_action = 'FIRE .addRecord=true'
            add_class = add_class or 'buttonIcon icnBaseAdd'
            add_enable = add_enable or '^form.canWrite'
            tb.button('!!Add', float='right', action=add_action, visible=add_enable,
                      iconClass=add_class, showLabel=False)
                      
        tb.button('!!First', fire_first='.navbutton', iconClass="tb_button icnNavFirst", disabled='^.atBegin',
                  showLabel=False)
        tb.button('!!Previous', fire_prev='.navbutton', iconClass="tb_button icnNavPrev", disabled='^.atBegin',
                  showLabel=False)
        tb.button('!!Next', fire_next='.navbutton', iconClass="tb_button icnNavNext", disabled='^.atEnd',
                  showLabel=False)
        tb.button('!!Last', fire_last='.navbutton', iconClass="tb_button icnNavLast", disabled='^.atEnd',
                  showLabel=False)
                  
        controller.dataFormula('.atBegin', '(idx==0)', idx='^.selectedIndex')
        controller.dataFormula('.atEnd', '(idx==genro.wdgById(gridId).rowCount-1)', idx='^.selectedIndex',
                               gridId=gridId)
                               
    def _iv_FormStaticController(self, controller, gridId):
        controller.dataController("""var newidx;
                                 var rowcount = genro.wdgById(gridId).rowCount;
                                 if (btn == 'first'){newidx = 0;}
                                 else if (btn == 'last'){newidx = rowcount-1;}
                                 else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                                 else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                                 SET .selectedIndex = newidx;
                                 """, btn='^.navbutton', idx='=.selectedIndex', gridId=gridId)
                                 
    def _includedViewFormBody(self, recordBC, controller, storepath, gridId, formPars):
        #controller not used
        #recordBC datapath = controllerPath
        bottom_left = formPars.pop('bottom_left', None)
        bottom_right = formPars.pop('bottom_right', '!!Close')
        bottom_left_action = formPars.pop('bottom_left_action', None)
        bottom_right_action = formPars.pop('bottom_right_action', 'FIRE .close')
        disabled = formPars.pop('disabled', '^form.locked')
        if formPars.get('mode', 'dialog') == 'dialog':
            bottom = recordBC.contentPane(region='bottom', _class='dialog_bottom')
            if bottom_left:
                bottom.button(bottom_left, float='left', baseClass='bottom_btn',
                              connect_onclick=bottom_left_action)
            if bottom_right:
                bottom.button(bottom_right, float='right', baseClass='bottom_btn',
                              connect_onclick=bottom_right_action)
        st = recordBC.stackContainer(region='center', selected='^.dlgpage')
        st.dataController("if(idx!=null){SET .dlgpage=0;}else{SET .dlgpage=1;}",
                          idx='^.selectedIndex', _onStart=True)
        _classBC = formPars.pop('_classBC', 'pbl_dialog_center') #aggiunto da fporcari
        recordBC.dataController("""var currLineDatapath;
                                   if (sel_label){
                                       currLineDatapath = view_storepath+'.'+sel_label;
                                   }else{
                                       currLineDatapath='.emptypath';
                                   }
                                   SET _temp.grids.%s.currLineDatapath=currLineDatapath;
                                   """ % gridId,
                                sel_label='^.selectedLabel',
                                view_storepath=storepath)
        formBorderCont = st.borderContainer(datapath='^_temp.grids.%s.currLineDatapath' % gridId)
        # #datapath='^.selectedLabel?=if(#v){"."+#v}else{"emptypath"}', _class=_classBC) #aggiunto il _classBC da fporcari
        #--NEW--#formBorderCont = st.borderContainer(datapath='==sel_label?"."+sel_label:"emptypath"',sel_label='^%s.selectedLabel'% controllerPath, _class=_classBC)
        emptypane = st.contentPane()
        emptypane.div("No record selected", _class='dlg_msgbox')
        formPars['formCb'](formBorderCont, region='center', disabled=disabled)
        
    def _iv_Picker(self, controller, controllerPath, view, pickerPars):
        pickerId = pickerPars.setdefault('nodeId', self.getUuid())
        gridId = view.attributes['nodeId']
        nodup_field = view.attributes.get('fromPicker_nodup_field')
        dialogId = '%s_picker' % gridId
        height = pickerPars.pop('height', '40ex')
        width = pickerPars.pop('width', '40em')
        mainPane = pickerPars.pop('pane')
        title = pickerPars.pop('label', None)
        onOpen = pickerPars.pop('onOpen', None)
        if nodup_field:
            onOpen = onOpen or ''
            onOpen = 'genro.wdgById("' + pickerId + '").applyFilter();%s' % onOpen
        dlgBC = self.hiddenTooltipDialog(mainPane, dlgId=dialogId, title=title,
                                         width=width, height=height, fired='^%s.showPicker' % controllerPath,
                                         datapath=controllerPath, close_action="FIRE .close;",
                                         bottom_left='!!Add', bottom_left_action='FIRE .pickerAdd;',
                                         bottom_right='!!Add and Close',
                                         bottom_right_action='FIRE .close;FIRE_AFTER .pickerAdd;',
                                         onOpen=onOpen, onEnter='FIRE .close;FIRE_AFTER .pickerAdd;')
        gridBC = dlgBC.borderContainer(region='center')
        
        selector_cb = pickerPars.pop('selector_cb', None)
        selector_storepath = pickerPars.pop('selector_storepath', None)
        selector_result = pickerPars.pop('selector_result', None)
        if selector_cb or selector_storepath:
            if selector_storepath:
                top = dlgBC.contentPane(region='top', height='26px').toolbar()
                top.filteringSelect(value=selector_result, storepath=selector_storepath)
            else:
                selector_cb(dlgBC)
                
        if nodup_field:
            pickerPars[
            'excludeListCb'] = 'return genro.wdgById("' + gridId + '").getColumnValues("' + nodup_field + '")'
            target_fields = view.attributes.get('fromPicker_target_fields').split(',')
            for fld in target_fields:
                tfld, pfld = fld.split('=')
                if tfld.strip() == nodup_field:
                    pickerPars['excludeCol'] = pfld.strip()
                    break
                    
        self.includedViewBox(gridBC, **pickerPars)
        controller.dataController("genro.wdgById(dialogId).onCancel();", dialogId=dialogId, _fired='^.close')
        controller.dataController("""var nodelist = genro.wdgById(pickerId).getSelectedNodes();
                                    genro.nodeById(gridId).includedViewPicker.fromPicker(nodelist);
                                    """,
                                  pickerId=pickerId,
                                  gridId=gridId, _fired='^.pickerAdd')
                                  
    def _iv_Form_dialog(self, formPars, storepath, controller, controllerPath, gridId, toolbarPars):
        dialogId = '%s_dialog' % gridId
        height = formPars.pop('height', '40ex')
        width = formPars.pop('width', '40em')
        mainPane = formPars.pop('pane')
        if 'onOpen' in formPars:
            formPars['connect_show'] = '%s' % formPars.pop('onOpen')
        controller.dataController("genro.wdgById('%s').show();" % dialogId, _fired='^.showRecord')
        controller.dataController("genro.wdgById('%s').onCancel()" % dialogId, _fired='^.close')
        
        toolbarHandler = formPars.pop('toolbarHandler', '_iv_FormToolbar')
        #recordBC = mainPane.dialog(nodeId=dialogId,**formPars).borderContainer(nodeId='%s_bc' %gridId,
        #                                                                       datapath=storepath, #[check]
        #                                                                       height=height, width=width)
        recordBC = mainPane.dialog(nodeId=dialogId, **formPars).borderContainer(nodeId='%s_bc' % gridId,
                                                                                datapath=controllerPath,
                                                                                height=height, width=width)
        getattr(self, toolbarHandler)(recordBC, controller, controllerPath=controllerPath, gridId=gridId, **toolbarPars)
        self._includedViewFormBody(recordBC, controller, storepath, gridId, formPars)
        
    def _iv_Form_pane(self, formPars, storepath, controller, controllerPath, gridId, toolbarPars):
        mainPane = formPars.pop('pane')
        toolbarHandler = formPars.pop('toolbarHandler', '_iv_FormToolbar')
        recordBC = mainPane.borderContainer(datapath=storepath, **formPars) #[check]
        getattr(self, toolbarHandler)(recordBC, controller, controllerPath=controllerPath,
                                      gridId=gridId, **toolbarPars)
        self._includedViewFormBody(recordBC, controller, storepath, gridId, formPars)
        
    @extract_kwargs(_dictkwargs={'add':True,'del':True,'upd':True,'print':True,'export':True,'tools':True,'top':True})
    def includedGrid(self,parentBC,nodeId=None,frameCode=None,datapath=None,struct=None,table=None,pbl_classes=True,
                     storepath=None,label=None,caption=None,filterOn=None,editorEnabled=None,canSort=True,dropCodes=None,
                     add_kwargs=None,del_kwargs=None,upd_kwargs=None,print_kwargs=None,export_kwargs=None,tools_kwargs=None,
                     top_kwargs=None,datamode=None,**kwargs):
        """The :ref:`includedgrid` is a :ref:`grid` that allows the inline editing. So, the insertion
        or the modify of records is handled inside the grid
        
        :param parentBC: the root parent :ref:`bordercontainer`
        :param nodeId: the includedGrid's :ref:`nodeid`. You have to define it OR the *frameCode* attribute
        :param frameCode: it is the includedGrid's :ref:`nodeid`. You have to define it OR the *nodeId* attribute
        :param datapath: allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        :param struct: the name of the method that defines the :ref:`struct`
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pbl_classes: boolean. The :ref:`pbl_classes` attribute
        :param storepath: TODO
        :param label: TODO
        :param caption: TODO
        :param filterOn: TODO
        :param editorEnabled: TODO
        :param canSort: boolean. TODO
        :param dropCodes: TODO
        :param add_kwargs: TODO
        :param del_kwargs: TODO
        :param upd_kwargs: TODO
        :param print_kwargs: TODO
        :param export_kwargs: TODO
        :param tools_kwargs: TODO
        :param top_kwargs: TODO
        :param datamode: TODO"""
        assert not 'selectionPars' in kwargs, 'instead of the selectionPars use the tableviewer or attach a selectionStore'
        assert not 'formPars' in kwargs, 'no longer supported'
        assert not 'lock_action' in kwargs, 'no longer supported'
        assert not 'footer' in kwargs, 'no longer supported'
        assert not '_onStart' in kwargs, 'no longer supported'
        assert not 'pickerPars' in kwargs, 'no longer supported'
        assert not 'centerPaneCb' in kwargs, 'no longer supported'
        assert not 'parentLock' in kwargs, 'no longer supported'
        assert not 'reloader' in kwargs, 'no longer supported'
        assert not 'externalChanges' in kwargs, 'no longer supported'
        assert not 'addOnCb' in kwargs, 'no longer supported'
        assert not 'hasToolbar' in kwargs, 'no longer supported'
        assert not 'zoom' in kwargs, 'no longer supported'
        assert not print_kwargs, 'provided by default'
        assert not export_kwargs, 'provided by default'
        assert (frameCode or nodeId), 'nodeId or frameCode must be provided'
        assert storepath,'this adapter is for grid with storepath'
        
        parentBC.attributes['tag'] = 'ContentPane'
        pane = parentBC
        frameCode = frameCode or 'frame_%s' %nodeId
        datapath = datapath or '#FORM.%s' %frameCode
        if pbl_classes:
            kwargs['_class'] = kwargs.get('_class','') + ' pbl_roundedGroup'
        
        if storepath.startswith('.'):
            storepath = '#FORM.record%s' %storepath
        frame = pane.frameGrid(frameCode=frameCode,datapath=datapath,struct=struct,
                               grid_nodeId=nodeId,datamode=datamode,table=table,
                               storepath=storepath,**kwargs)
        frame.dataFormula(".locked","locked",locked="^#FORM.controller.locked")
        
        gridattr = frame.grid.attributes
        gridattr['selfsubscribe_addrow'] = """for(var i=0; i<$1._counter;i++){
                                                this.widget.addBagRow('#id', '*', this.widget.newBagRow(),$1.evt);
                                              }
                                              this.widget.editBagRow(null);"""
        gridattr['selfsubscribe_delrow'] = """this.widget.delBagRow('*', true);FIRE .onDeletedRow;"""
        gridattr['tag'] = 'includedview'
        if dropCodes:
            frame.grid.dragAndDrop(dropCodes)
        slots = []
        slotsKw = {}
        if label:
            slots.append('label,*')
            slotsKw['label'] = label
        else:
            slots.append('*')
        if del_kwargs:
            delaction = del_kwargs.get('action')
            if delaction:
                slots.append('delrow')
                slotsKw['delrow_parentForm'] = True
                assert not isinstance(delaction,basestring), 'custom action are not supported'
        if add_kwargs:
            addaction = add_kwargs.get('action')
            if addaction:
                slots.append('addrow')
                slotsKw['addrow_parentForm'] = True
                assert not isinstance(addaction,basestring), 'custom action are not supported'
        if pbl_classes:
            frame.top.slotBar(','.join(slots),_class='slotbar_toolbar pbl_roundedGroupLabel',**slotsKw)
        else:
            frame.top.slotToolbar(','.join(slots),**slotsKw)
        return frame.grid
                