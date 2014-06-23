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
# 
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

from gnr.core.gnrbag import Bag
from gnr.core.gnranalyzingbag import AnalyzingBag

from gnr.core.gnrstring import toText, splitAndStrip

import os

class QueryHelper(BaseComponent):
    def query_helper_main(self, pane):
        pane.dataController(""" var row = genro.getDataNode('list.query.where.'+queryrow);
                                var attrs = row.getAttr();
                                var op = attrs['op'];
                                var col_caption = attrs['column_caption'];
                                var op_caption = attrs['op_caption'];
                                if(op=='in'){
                                    FIRE #helper_in_dlg.open = {row:queryrow,title:col_caption+' '+op_caption};
                                }else if(op=='tagged'){
                                    FIRE #helper_tag_dlg.open = {row:queryrow,call_mode:'helper'};
                                }""",
                            queryrow="^list.helper.queryrow")
        self.helper_in_dlg(pane)
        self.helper_tag_dlg(pane)

    def helper_in_dlg(self, pane):
        def cb_center(parentBC, **kwargs):
            bc = parentBC.borderContainer(**kwargs)
            top = bc.contentPane(region='top', margin_bottom='0', padding='2px',
                                 datapath='.#parent', height='25px', overflow='hidden')
            top = top.toolbar(height='24px')
            top.div('!!Enter a list of values:', float='left', margin='3px')
            menubag = Bag()
            menubag.setItem('save', None, label='!!Save', action='FIRE .saveAsUserObject;')
            menubag.setItem('save_as', None, label='!!Save as', action='FIRE .saveAsUserObject = "new";')
            menubag.setItem('delete', None, label='!!Delete ', action='FIRE .deleteCurrSaved;')
            menubag.setItem('-', None)
            top.data('.menu', menubag)
            top.dataRemote('.menu.load', 'getObjListIn', cacheTime=10,
                           sync=True, label='!!Load',
                           action='FIRE .loadUserObject = $1.pkey;')
            ddb = top.dropDownButton('!!Command', float='right')
            ddb.menu(storepath='.menu', _class='smallmenu')
            center = bc.contentPane(region='center', margin='5px', margin_top=0)
            center.simpleTextArea(value='^.items', height='90%', width='95%', margin='5px')

        dialogBc = self.formDialog(pane, title='^.opener.title', loadsync=True,
                                   datapath='list.helper.op_in', centerOn='_pageRoot',
                                   height='300px', width='300px',
                                   formId='helper_in', cb_center=cb_center)
        dialogBc.dataController("""var val =genro._('list.query.where.'+queryrow);
                                   if(val){
                                       SET .data.items = val.replace(/,+/g,'\\n');                                       
                                   }else{
                                        SET .data = null;
                                   }
                                   """,
                                nodeId="helper_in_loader", queryrow='=.opener.row')

        dialogBc.dataController("""
                                var splitPattern=/\s*[\\n\\,]+\s*/g;
                                var cleanPattern=/(^\\s*[\\n\\,]*\\s*|\\s*[\\n\\,]*\\s*$)/g;
                                items=items.replace(cleanPattern,'').split(splitPattern).join(',');
                                genro.setData('list.query.where.'+queryrow,items);
                                FIRE .saved;""",
                                items='=.data.items', queryrow='=.opener.row',
                                nodeId="helper_in_saver")
        dialogBc.dataController("""
                                  data = data.replace(/\s+/g,',').replace(/,+$/g,'');
                                  var pars = new gnr.GnrBag({data:new gnr.GnrBag({values:data}),title:title,objtype:objtype});
                                  SET #userobject_dlg.pars = pars;
                                  if(command=='new'){
                                       current = "*newrecord*"
                                  }
                                  FIRE #userobject_dlg.pkey = current || '*newrecord*';""",
                                command="^.saveAsUserObject", current='=.currentUserObject',
                                data='=.data.items', title='!!Save list',
                                objtype='list_in')
        dialogBc.dataRpc('dummy', 'loadUserObject',
                         tbl=self.maintable, id='^.loadUserObject', _if='id',
                         _onResult='SET .currentUserObject = $2.id; SET .data.items = $1.getValue().getItem("values");')
        dialogBc.dataController("SET .currentUserObject=pkey", _fired="^#userobject_dlg.saved",
                                pkey='=#userobject_dlg.savedPkey',
                                objtype='=#userobject_dlg.pars.objtype',
                                _if='objtype=="list_in"')
        dialogBc.dataController("""SET #deleteUserObject.pars = new gnr.GnrBag({title:title,pkey:current,objtype:"list_in"}); 
                                   FIRE #deleteUserObject.open;""", _fired="^.deleteCurrSaved",
                                title='!!Delete list of values', current='=.currentUserObject', _if='current')
        dialogBc.dataController("SET .data.items = null; SET .currentUserObject=null;",
                                _fired="^#deleteUserObject.deleted", objtype='=#deleteUserObject.pars.objtype',
                                _if='objtype=="list_in"')

    def rpc_getObjListIn(self, **kwargs):
        result = self.rpc_listUserObject(objtype='list_in', tbl=self.maintable, **kwargs)
        return result

    def helper_tag_dlg(self, pane):
        def cb_center(parentBC, **kwargs):
            parentBC.contentPane(**kwargs).remote('getFormTags_query', queryColumn='=.#parent.queryColumn',
                                                  queryValues='^.#parent.queryValues', call_mode='helper')

        dialogBc = self.formDialog(pane, title='!!Helper TAG', loadsync=False,
                                   datapath='list.helper.op_tag', centerOn='_pageRoot',
                                   height='300px', width='510px', allowNoChanges=False,
                                   formId='helper_tag', cb_center=cb_center)
        dialogBc.dataController("""
                                   SET .data = null;
                                   var rowNode = genro.getDataNode('list.query.where.'+queryrow);
                                   SET .queryColumn  = rowNode.attr.column;
                                   FIRE .queryValues = rowNode.getValue();
                                   FIRE .loaded;
                                """,
                                nodeId="helper_tag_loader", queryrow='=.opener.row')

        dialogBc.dataController("""
                                var tagged = [];
                                var tagged_not = [];
                                var cb = function(node){
                                    var selectedTag = node.attr['selectedTag'];
                                    if (selectedTag){
                                        if (selectedTag[0]=='!'){
                                            tagged_not.push(selectedTag.slice(1));
                                        }else{
                                            tagged.push(selectedTag);
                                        }
                                    }
                                }
                                tagbag.forEach(cb);
                                var result = tagged.join(',')+'!'+tagged_not.join(',');
                                genro.setData('list.query.where.'+queryrow,result);
                                FIRE .saved;""",
                                tagbag='=.data.tagbag', queryrow='=.opener.row',
                                nodeId="helper_tag_saver")

class FiltersHandler(BaseComponent):
    def filterBase(self):
        return

    def listToolbar_filters(self, pane):
        #trial
        pane.button('bbb')

    def th_filtermenu(self, pane):
        filterButton = pane.dropdownbutton(tip='!!Set Filter', iconClass='st_filterButton', _class='dropDownNoArrow')
        menu = filterButton.menu(_class='smallmenu', action='FIRE list.filterCommand = $1.command', modifiers='*')
        menu.menuline('!!Set filter', command='new_filter')
        #menu.menuline('!!Add to current filter',command='add_to_filter')
        menu.menuline('!!Remove filter', command='remove_filter')
        menu.menuline('-')

        #menu.menuline('!!Custom filter').menu(storepath='list.',action="""genro.rpc.remoteCall("load_query",{id:$1.pkey},null,null,null,
        #                                                                         function(result){
        #                                                                            genro.setData('_clientCtx.filter.%s',result);
        #                                                                            genro.saveContextCookie();
        #                                                                         })""" %self.pagename).remote('getQuickQuery',cacheTime=5)

        pane.dataController(""" var filter;
                                if (command=='new_filter'){
                                    filter = query.deepCopy();
                                }else if(command=='add_to_filter'){
                                    alert('add filter');
                                }else if(command=='remove_filter'){
                                    filter = null;
                                }
                                 genro.setData('_clientCtx.filter.'+pagename,filter);
                                 genro.saveContextCookie();
                            """, current_filter='=_clientCtx.filter.%s' % self.pagename,
                            query='=list.query.where',
                            pagename=self.pagename,
                            command="^list.filterCommand")
        pane.dataController(
                "if(current_filter){dojo.addClass(dojo.body(),'st_filterOn')}else{dojo.removeClass(dojo.body(),'st_filterOn')}"
                ,
                current_filter='^_clientCtx.filter.%s' % self.pagename, _onStart=True)

class TagsHandler(BaseComponent):
    @struct_method
    def th_slotbar_tagsbtn(self,pane,**kwargs):
        pane.slotButton('!!Tags', publish='tagbtn',iconClass="icnTag", showLabel=False,**kwargs)
    
    
    def customSqlOp_tagged(self, column=None, value=None, dtype=None, sqlArgs=None, optype_dict=None,
                           whereTranslator=None):
        if optype_dict:
            operation = 'tagged'
            optype_dict['tagged'] = operation
            return ('tagged', '!!Tag in')
        elif whereTranslator and value:
            column = column.replace('_recordtag_desc', '_recordtag_tag')
            conditions = []
            tagged, tagged_not = value.split('!')
            if tagged:
                cond_tag = []
                for tag in tagged.split(','):
                    cond_tag.append('%s =:%s' % (column, whereTranslator.storeArgs(tag, 'A', sqlArgs)))
                conditions.append(' AND '.join(cond_tag))
            if tagged_not:
                cond_tag = []
                for tag in tagged_not.split(','):
                    cond_tag.append('%s LIKE :%s' % (column, whereTranslator.storeArgs('%s%%' % tag, 'A', sqlArgs)))
                conditions.append(' NOT (%s)' % ' OR '.join(cond_tag))
            return ' AND '.join(conditions)

    def tags_main(self, pane):
        if self.application.checkResourcePermission(self.canLinkTag(), self.userTags):
            self.linktag_dlg(pane)
            self.managetags_dlg(pane)

    def canManageTag(self):
        return 'admin'

    def canLinkTag(self):
        return

    def managetags_dlg(self, pane):
        def cb_bottom(parentBC, **kwargs):
            bottom = parentBC.contentPane(**kwargs)
            bottom.button('!!Close', baseClass='bottom_btn', float='right', margin='1px', fire='.close')

        def cb_center(parentBC, **kwargs):
            bc = parentBC.borderContainer(**kwargs)
            self.selectionHandler(bc, label='!!Edit tags',
                                  datapath=".tags", nodeId='recordtag_view',
                                  table='%s.recordtag' % self.package.name,
                                  struct=self.recordtag_struct, hasToolbar=True, add_enable=True,
                                  del_enable=True, checkMainRecord=False,
                                  selectionPars=dict(where='$tablename =:tbl AND $maintag IS NULL', tbl=self.maintable,
                                                     order_by='tag'),
                                  dialogPars=dict(formCb=self.recordtag_form, height='180px',
                                                  width='300px', dlgId='_th_recortag_dlg', title='!!Record Tag',
                                                  default_tablename=self.maintable, lock_action=False))

        dialogBc = self.formDialog(pane, title='!!Edit tag', loadsync=True,
                                   datapath='gnr.recordtag.edit', centerOn='_pageRoot',
                                   height='250px', width='400px',
                                   formId='recordtag', cb_center=cb_center,
                                   cb_bottom=cb_bottom)
        dialogBc.dataController("FIRE #recordtag_view.reload;", nodeId="recordtag_loader")

    def recordtag_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('tag', width='5em')
        r.fieldcell('description', width='10em')
        return struct

    def recordtag_form(self, parentContainer, disabled, table, **kwargs):
        bc = parentContainer.borderContainer(**kwargs)
        form = bc.contentPane(region='top', height='150px')
        fb = form.formbuilder(cols=1, border_spacing='4px', width='90%', dbtable=table)
        fb.field('tag', autospan=1)
        fb.field('description', autospan=1)
        fb.field('values', autospan=1, tag='simpleTextArea')

    def rpc_load_recordtag(self):
        #'%s.userobject' %self.package.name
        return self.db.table('%s.recordtag' % self.package.name).query(where='$tablename =:tbl',
                                                                       tbl=self.maintable).selection().output('grid')

    def rpc_save_recordtag(self, tags):
        tblrecordtag = self.db.table('%s.recordtag' % self.package.name)

        for r in tags.values():
            if not r['id']:
                r['tablename'] = self.maintable
                tblrecordtag.insertOrUpdate(r)
        self.db.commit()

    def linktag_dlg(self, pane):
        pkey = '=form.record.%s' % self.tblobj.pkey
        selectionName = '=list.selectionName'
        selectedRowIdx = "==genro.wdgById('maingrid').getSelectedRowidx();"

        def cb_center(parentBC, **kwargs):
            parentBC.contentPane(**kwargs).remote('getFormTags', selectedRowIdx='=.#parent.selectedRowIdx',
                                                  pkey=pkey, call_mode='=.#parent.opener.call_mode',
                                                  selectionName=selectionName, _fired='^.#parent.loadContent')

        dialogBc = self.formDialog(pane, title='!!Link tag', loadsync=False,
                                   datapath='gnr.recordtag.assign', allowNoChanges=False,
                                   height='300px', width='510px', centerOn='_pageRoot',
                                   formId='linktag', cb_center=cb_center, cb_bottom=self.linktag_dlg_bottom)
        dialogBc.dataController("""SET .data = null; 
                                   SET .selectedRowIdx = selectedRowIdx;
                                   FIRE .loadContent;
                                   FIRE .loaded;""",
                                nodeId="linktag_loader", selectedRowIdx=selectedRowIdx)
        dialogBc.dataRpc(".result", 'saveRecordTagLinks', nodeId="linktag_saver", call_mode='=.opener.call_mode',
                         selectedRowIdx=selectedRowIdx, data='=.data', selectionName=selectionName, pkey=pkey,
                         _onResult='FIRE .saved;', _if='selectionName', _else='FIRE .close;')

    def linktag_dlg_bottom(self, bc, confirm_btn=None, **kwargs):
        bottom = self.formDialog_bottom(bc, confirm_btn=None, **kwargs)
        if self.application.checkResourcePermission(self.canManageTag(), self.userTags):
            bottom.button('!!Edit tags', margin='1px', float='left', fire='#recordtag_dlg.open')
        bottom.dataController("FIRE .load;", _fired="^#recordtag_dlg.close")

    def rpc_saveRecordTagLinks(self, data=None, call_mode=None, selectedRowIdx=None, pkey=None, selectionName=None):
        tagbag = data['tagbag']
        taglink_table = self.db.table('%s.recordtag_link' % self.package.name)
        pkeys = [pkey]
        if call_mode == 'list':
            pkeys = self.getUserSelection(table=self.tblobj, selectionName=selectionName,
                                          selectedRowidx=selectedRowIdx).output('pkeylist')
        for pkey in pkeys:
            self._assignTagOnRecord(pkey, tagbag, taglink_table)
        self.db.commit()

    def _assignTagOnRecord(self, pkey, tagbag, taglink_table):
        for node in tagbag:
            tag = node.label
            value = [k for k, v in node.value.items() if v]
            if value:
                taglink_table.assignTagLink(self.maintable, pkey, tag, value[0])

    def remote_getFormTags_query(self, pane, queryValues=None, queryColumn=None, **kwargs):
        table = self.maintable
        if queryColumn != '_recordtag_desc':
            table = self.tblobj.column(queryColumn.replace('._recordtag_desc', '')[1:]).relatedTable().fullname
        if queryValues:
            tagged, tagged_not = queryValues.split('!')
            queryValues = Bag()
            queryValues['tagged'] = dict()
            queryValues['tagged_not'] = dict()

            for tag in tagged.split(','):
                queryValues['tagged'][tag] = True
            for tag in tagged_not.split(','):
                queryValues['tagged_not'][tag] = True
        self.remote_getFormTags(pane, queryValues=queryValues, table=table, **kwargs)

    def remote_getFormTags(self, pane, pkey=None, selectedRowIdx=None, call_mode=None,
                           selectionName=None, queryValues=None, table=None, **kwargs):
        taglinktbl = self.db.table('%s.recordtag_link' % self.package.name)
        table = table or self.maintable

        def lblGetter (fulltag, label):
            return label

        if call_mode == 'form':
            tagbag = taglinktbl.getTagLinksBag(self.maintable, pkey)
            pane.data('.tagbag', tagbag)
        elif call_mode == 'list' and selectionName:
            pkeys = self.getUserSelection(table=table, selectionName=selectionName,
                                          selectedRowidx=selectedRowIdx).output('pkeylist')
            countDict = taglinktbl.getCountLinkDict(table, pkeys)

            def lblGetter (fulltag, label):
                if countDict.get(fulltag):
                    return  "%s(%i)" % (label, countDict.get(fulltag)['howmany'])
                return label
        recordtagtbl = self.db.table('%s.recordtag' % self.package.name)
        rows = recordtagtbl.query(where='$tablename =:tbl AND $maintag IS NULL',
                                  tbl=table, order_by='$values desc,$tag').fetch()
        externalFrame = pane.div(_class='tag_frame bgcolor_medium', datapath='.tagbag', padding='10px')
        tag_table = externalFrame.div(style='display:table;width:100%')
        for j, r in enumerate(rows):
            values = r['values']
            tag = r['tag']
            description = r['description']
            label_width = '%fem' % ((len(description) * 0.3) + 2)
            buttons = []
            max_width = 3
            if values:
                for val in values.split(','):
                    subtag, label = splitAndStrip('%s:%s' % (val, val), ':', n=2, fixed=2)
                    fulltag = '%s_%s' % (tag, subtag)
                    label = lblGetter(fulltag, label)
                    buttons.append(
                            dict(value='^.%s' % subtag, _class='dijitButtonNode tag_button tag_value', label=label,
                                 fulltag=fulltag))
                for b in buttons:
                    if len(b['label']) > max_width:
                        max_width = len(b['label'])
                max_width = '%fem' % ((max_width * .5) + 2)
            else:
                label = lblGetter(tag, '!!Yes')
                buttons.append(
                        dict(value='^.true', _class='dijitButtonNode tag_button tag_true', label=label, fulltag=tag))
            oddOrEven = 'even'
            colorRow = 'bgcolor_bright'
            if j % 2:
                oddOrEven = 'odd'
                colorRow = 'bgcolor_brightest'
            tag_row = tag_table.div(style='display:table-row',
                                    height='5px') #no dimensioni riga solo padding dimensioni ai contenuti delle celle
            tag_row = tag_table.div(style='display:table-row', _class='tag_line tag_%s' % (oddOrEven),
                                    datapath='.%s' % tag) #no dimensioni riga solo padding dimensioni ai contenuti delle celle

            if call_mode == 'form':
                label_col = tag_row.div(description, style='display:table-cell', width=label_width,
                                        _class='tag_left_col tag_label_col bgcolor_darkest color_brightest')
            else:
                cb_col = tag_row.div(style='display:table-cell', _class='tag_left_col bgcolor_darkest color_brightest',
                                     padding_left='10px', width='30px')
                cb_col.checkbox(value='^.?enabled', validate_onAccept="""if(!value){
                                                                            var line = GET #; 
                                                                            line.walk(function(node){if(node.getValue()){node.setValue(null);}});
                                                                            SET .?selectedTag = null;
                                                                        }else if(userChange){
                                                                            SET .?enabled = false;
                                                                        }""")
                label_col = tag_row.div(description, style='display:table-cell', width=label_width,
                                        _class='bgcolor_darkest color_brightest tag_label_col',
                                        padding_left='10px')
            no_td = tag_row.div(style='display:table-cell', _class=colorRow, width='4em').div(
                    _class='dijitButtonNode tag_button tag_false')
            if call_mode == 'helper' and queryValues:
                if tag in queryValues['tagged_not']:
                    no_td.data('.false', True)
                    no_td.data('.?enabled', True)
                    no_td.data('.?selectedTag', '!%s' % tag)
            no_td.radiobutton(value='^.false', label='!!No', group=tag,
                              connect_onclick='SET .?enabled= true; SET .?selectedTag="!%s";' % tag)
            value_col = tag_row.div(style='display:table-cell', _class='tag_value_col %s' % colorRow)
            for btn in buttons:
                value_td = value_col.div(_class=btn['_class'], width=max_width)
                if call_mode == 'helper' and queryValues:
                    if btn['fulltag'] in queryValues['tagged']:
                        value_td.data(btn['value'][1:], True)
                        value_td.data('.?enabled', True)
                        value_td.data('.?selectedTag', btn['fulltag'])
                value_td.radiobutton(value=btn['value'], label=btn['label'],
                                     group=tag,
                                     connect_onclick='SET .?enabled= true; SET .?selectedTag="%s";' % btn['fulltag'])

class StatsHandler(BaseComponent):
    def stats_main(self, parent, **kwargs):
        """docstring for stats_mainpane"""
        bc = parent.borderContainer(**kwargs)
        top = bc.contentPane(region='top', height='6ex', splitter=True)
        left = bc.contentPane(region='left', width='300px', datapath='.tree', splitter=True)
        center = bc.borderContainer(region='center')
        self.stats_top(top)
        self.stats_left(left)
        self.stats_center(center)

    def stats_top(self, pane):
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.filteringSelect(values=','.join(["%s:%s" % (k, v) for k, v in self.stats_modes_dict().items()]),
                           value='^.tree.tot_mode', lbl='!!Mode')
        #fb.button('Run',fire='.tree.totalize')

    def stats_left(self, pane):
        pane.tree(storepath='.root', inspect='shift', selectedPath='.currentTreePath', labelAttribute='caption',
                  selectedItem='#_grid_total.data', isTree=True, margin='10px', _fired='^.reload_tree', hideValues=True)
        pane.dataRpc('.root', 'stats_totalize', selectionName='=list.selectionName',
                     tot_mode='^.tot_mode', _if='tot_mode&&(selectedTab==1) && selectionName', timeout=300000,
                     totalrecords='=list.rowcount', selectedTab='=list.selectedTab',
                     _onCalling="""
                            batch_monitor.create_local_root(true);
                            PUBLISH batch_monitor_on;
                     """,
                     _onResult="""
                        genro.wdgById('localBatches_root').hide();
                        PUBLISH batch_monitor_off;
                        FIRE .reload_tree;
                     """,
                    #_onCalling="""genro.wdgById("_stats_load_dlg").show();
                    #                SET #_grid_total.data = null;SET #_grid_detail.data = null;""",
                    #_onResult='FIRE .reload_tree;genro.wdgById("_stats_load_dlg").hide();',
                     _fired='^.do_totalize')
        pane.dataController("""SET .root.data = null; FIRE .reload_tree; FIRE .do_totalize;""", _fired="^list.queryEnd")
        dlg = pane.dialog(nodeId='_stats_load_dlg', title='!!Loading')
        dlg.div(_class='pbl_roundedGroup', height='200px', width='300px').div(_class='waiting')


    def stats_center(self, bc):
        self.includedViewBox(bc.borderContainer(region='top', height='50%', splitter=True, margin='5px'),
                             label='!!Analyze Grid', datapath='.grids.total', nodeId='_grid_total',
                             storepath='.data', structpath='.struct', autoWidth=True, export_action=True)
        bc.dataRpc('#_grid_total.struct', 'stats_get_struct_total', tot_mode='^.tree.tot_mode')
        self.includedViewBox(bc.borderContainer(region='center', margin='5px'),
                             label=self._stats_detail_label,
                             datapath='.grids.detail', nodeId='_grid_detail',
                             storepath='.data', structpath='.struct',
                             table=self.maintable, autoWidth=True, export_action=True,
                             selectionPars=dict(method='stats_get_detail',
                                                flt_path='=stats.tree.currentTreePath',
                                                selectionName='=list.selectionName',
                                                _autoupdate='=.autoupdate', _if='_autoupdate',
                                                _else='null'))
        bc.dataRpc('#_grid_detail.struct', 'stats_get_struct_detail', tot_mode='^.tree.tot_mode')

    def _stats_detail_label(self, pane):
        fb = pane.formbuilder(cols=2, border_spacing='2px')
        fb.div(self.pluralRecordName())
        fb.checkbox(value='^.autoupdate', label='!!Auto update', default=False, lbl=' ', lbl_width='1em')
        fb.dataController("FIRE .reload;", _fired="^stats.tree.currentTreePath",
                          autoupdate='^.autoupdate')


    def rpc_stats_get_struct_total(self, tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct = self.stats_totals_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            if not 'dtype' in cellargs:
                if cellargs['field'].startswith('sum_') or cellargs['field'].startswith('avg_'):
                    cellargs['dtype'] = 'N'
                elif cellargs['field'] == 'count' or cellargs['field'].startswith('count_'):
                    cellargs['dtype'] = 'L'
            r.cell(**cellargs)
        return struct

    def rpc_stats_get_struct_detail(self, tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct = self.stats_detail_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            r.fieldcell(**cellargs)
        return struct

    def rpc_stats_get_detail(self, flt_path=None, selectionName=None, **kwargs):
        selection = self.unfreezeSelection(self.tblobj, selectionName)
        result = selection.output('grid', subtotal_rows=flt_path, recordResolver=False)
        return result

    def stats_modes_dict(self):
        """Override this"""
        return

    def stats_group_by(self, tot_mode=None):
        """Override this"""
        return

    def stats_sum_cols(self, tot_mode=None):
        """Override this"""
        return

    def stats_keep_cols(self, tot_mode=None):
        """Override this"""
        return

    def stats_collect_cols(self, tot_mode=None):
        """Override this"""
        return

    def stats_distinct_cols(self, tot_mode=None):
        """Override this"""
        return

    def stats_key_col(self, tot_mode=None):
        """Override this"""
        return

    def stats_tot_modes(self):
        """Override this"""
        return ''

    def stats_columns(self):
        """Override this"""
        return

    def stats_get_selection(self, selectionName):
        if self.stats_columns():
            cust_selectionName = '%s_cust' % selectionName
            if not os.path.exists(self.pageLocalDocument(cust_selectionName)):
                return self.stats_create_custom_selection(selectionName, cust_selectionName)
            else:
                selectionName = cust_selectionName
        return self.unfreezeSelection(self.tblobj, selectionName)

    def stats_create_custom_selection(self, selectionName, cust_selectionName):
        pkeys = self.unfreezeSelection(self.tblobj, selectionName).output('pkeylist')
        query = self.tblobj.query(columns=self.stats_columns(),
                                  where='t0.%s IN :pkeys' % self.tblobj.pkey,
                                  pkeys=pkeys, addPkeyColumn=True)
        return query.selection()


    def rpc_stats_totalize(self, selectionName=None, group_by=None, sum_cols=None, keep_cols=None,
                           collect_cols=None, distinct_cols=None, key_col=None, captionCb=None,
                           tot_mode=None, **kwargs):
        selection = self.stats_get_selection(selectionName)
        analyzer = AnalyzingBag()
        self.btc.batch_create(batch_id='%s_%s' % (selectionName, self.getUuid()),
                              title='Stats',
                              delay=.8,
                              note='Stats',userBatch=False)
        group_by = group_by or self.stats_group_by(tot_mode)
        sum_cols = sum_cols or self.stats_sum_cols(tot_mode)
        keep_cols = keep_cols or self.stats_keep_cols(tot_mode)
        collect_cols = collect_cols or self.stats_collect_cols(tot_mode)
        distinct_cols = distinct_cols or self.stats_distinct_cols(tot_mode)
        key_col = key_col or self.stats_key_col(tot_mode)
        captionCb = captionCb or self.stats_captionCb(tot_mode)
        if isinstance(group_by, basestring):
            group_by = group_by.split(',')
        if isinstance(sum_cols, basestring):
            sum_cols = sum_cols.split(',')
        if isinstance(keep_cols, basestring):
            keep_cols = keep_cols.split(',')
        if isinstance(collect_cols, basestring):
            collect_cols = collect_cols.split(',')
        if isinstance(distinct_cols, basestring):
            distinct_cols = distinct_cols.split(',')

        def date_converter(mode):
            datefield, formatmode = mode.split(':')
            return lambda r: toText(r[datefield], format=formatmode, locale=self.locale)

        for k, x in enumerate(group_by):
            if isinstance(x, basestring):
                if x.startswith('#DATE='):
                    group_by[k] = date_converter(x[6:])
                else:
                    group_by[k] = x.replace('@', '_').replace('.', '_')
        if keep_cols:
            keep_cols = [x.replace('@', '_').replace('.', '_') for x in keep_cols]
        if distinct_cols:
            distinct_cols = [x.replace('@', '_').replace('.', '_') for x in distinct_cols]
        result = Bag()
        analyzer.analyze(self.btc.thermo_wrapper(selection, 'stat_tot', message='Row', keep=True),
                            group_by=group_by, sum=sum_cols, keep=keep_cols,
                            collect=collect_cols, distinct=distinct_cols,
                            key=key_col, captionCb=captionCb)
        self.freezeSelection(selection, selectionName)
        result.setItem('data', analyzer, caption=self.stats_modes_dict()[tot_mode])
        return result

    def stats_captionCb(self, tot_mode):
        def cb(group, row, bagnode):
            return bagnode.label

        return cb

class HierarchicalViewHandler(BaseComponent):
    py_requires = 'gnrcomponents/selectionhandler'

    def hv_columns(self):
        return None

    def hv_defaultConf(self):
        return dict(parent_code='parent_code', code='code', child_code='child_code')

    def hv_main_form(self, bc):
        bc.dataController("SET .form.pkey=pkey; FIRE .form.doLoad;", pkey="^.current.pkey")
        left = bc.borderContainer(region='left', overflow='auto', width='40%', splitter=True)
        leftTb = left.contentPane(region='top').toolbar(height='20px')
        leftTb.button('!!Add child', float='right', action='FIRE .form.add ="child"',
                      visible='^list.canWrite')
        leftTb.button('!!Add sibling', float='right', action='FIRE .form.add ="sibling"',
                      visible='^list.canWrite')
        dfltConf = self.hv_defaultConf()
        defaults = dict()
        defaults['default_%s' % dfltConf['parent_code']] = '=.default_parent_code'
        leftTb.dataController("""
                                SET .default_parent_code = what=='child'? code:parent_code;
                                SET .form.pkey="*newrecord*"; FIRE .form.doLoad;
                                """,
                              what="^.form.add",
                              parent_code='=.current.parent_code', code='=.current.code')
        self.hv_tree_edit(left.contentPane(region='center'), )
        self.formLoader('hv_formPane', resultPath='.form.record', _fired='^.form.doLoad', lock='=form.lockAcquire',
                        readOnly='=form.readOnly', datapath='list.hv.edit',
                        table=self.maintable, pkey='=.form.pkey', method='loadRecordCluster',
                        loadingParameters='=gnr.tables.maintable.loadingParameters',
                        sqlContextName='sql_record', **defaults)
        self.formSaver('hv_formPane', resultPath='.form.save_result', method='saveRecordCluster',
                       datapath='list.hv.edit', table=self.maintable, _fired='^.form.save',
                       _onCalling='FIRE pbl.bottomMsg=msg;',
                       msg='!!Saving...', saveAlways=getattr(self, 'saveAlways', False))
        center = bc.borderContainer(region='center')
        centerTb = center.contentPane(region='top').toolbar(height='20px')
        if self.userCanWrite():
            centerTb.div(_class='button_placeholder', float='right').button('!!Save', fire=".form.save",
                                                                            iconClass="tb_button db_save",
                                                                            showLabel=False,
                                                                            hidden='^status.locked')
            centerTb.div(_class='button_placeholder', float='right').button('!!Revert', fire='.form.doLoad',
                                                                            iconClass="tb_button db_revert",
                                                                            disabled='== !_changed',
                                                                            _changed='^gnr.forms.formPane.changed',
                                                                            showLabel=False, hidden='^status.locked')
        self.formBase(center.borderContainer(), datapath='.form.record', disabled='^form.locked', region='center',
                      formId='hv_formPane')

    def hv_tree_edit(self, pane):
        selected = dict()
        dfltConf = self.hv_defaultConf()

        selected['selected_%s' % dfltConf['parent_code']] = '.current.parent_code'
        selected['selected_%s' % dfltConf['child_code']] = '.current.child_code'
        selected['selected_%s' % dfltConf['code']] = '.current.code'
        pane.dataRemote('.tree', 'hv_selectionAsTree', selectionName='^list.selectionName', _if='selectionName')
        pane.tree(storepath='.tree',
                  isTree=False,
                  hideValues=True,
                  inspect='shift',
                  labelAttribute='caption',
                  fired='^list.queryEnd',
                  selected_pkey='.current.pkey',
                  **selected)

    def hv_main_view(self, bc):
        self.hv_tree_view(bc.contentPane(region='left', overflow='auto', width='300px', splitter=True))
        self.hv_right_view(bc.borderContainer(region='center'))

    def hv_tree_view(self, pane):
        pane.dataRemote('.tree', 'hv_selectionAsTree', selectionName='^list.selectionName', _if='selectionName',
                        _fired='^list.queryEnd')
        pane.dataRecord('.current_record', self.maintable, pkey='^.selected_id')
        tree_kwargs = self.hv_tree_kwargs()
        pane.tree(storepath='.tree',
                  selected_pkey='.selected_id',
                  isTree=False,
                  hideValues=True,
                  selectedItem='.selectedItem',
                  selected_rec_type='.current_rec_type',
                  inspect='shift',
                  selectedLabelClass='selectedTreeNode',
                  labelAttribute='caption',
                  fired='^list.queryEnd',
                  **tree_kwargs)

    def hv_tree_kwargs(self):
        return dict()

    def hv_right_view(self, infocontainer):
        infocontainer.data('.conf', self.hierarchicalViewConf())
        infopane_top = infocontainer.contentPane(region='top', height='50%',
                                                 splitter=True, _class='infoGrid', padding='6px')
        infopane_top.dataController(
                """var current_rec_type= current_record.getItem('rec_type');
                var result = new gnr.GnrBag();
                var fields = info_fields.getNodes()
                for (var i=0; i<fields.length; i++){
                    var fld_rec_types = fields[i].getAttr('rec_types',null);
                    var fld_label = fields[i].getAttr('label');
                    if (fld_rec_types){
                        fld_rec_types=fld_rec_types.split(',');
                    }
                    var fld_val_path = fields[i].getAttr('val_path');
                    var fld_show_path = fields[i].getAttr('show_path');

                    var fld_value = current_record.getItem(fld_val_path);
                    var fld_show = current_record.getItem(fld_show_path);
                    if (!fld_rec_types || dojo.indexOf(fld_rec_types, current_rec_type)!=-1){
                        result.setItem('R_'+i,
                                        null,
                                       {'lbl':fld_label, 'val':fld_value,'show':fld_show})
                    }
                }
                SET .info_table = result
                """,
                info_fields='=.conf',
                current_record='=.current_record',
                fired='^.current_record.id')
        infopane_top.includedView(storepath='.info_table', struct=self._infoGridStruct())
        infoStackContainer = infocontainer.stackContainer(region='center',
                                                          selectedPage='^list.hv.stack.selectedPage')
        infoStackContainer.contentPane()
        callbacks = [(x.split('_')[1], x) for x in dir(self) if x.startswith('hv_info_')]
        infoStackContainer.data('.rec_types', ','.join([x[0] for x in callbacks]))
        infoStackContainer.dataController("""SET list.hv.stack.selectedPage='hv_info_'+rec_type;""",
                                          rec_type='^.current_rec_type',
                                          _if='rec_type')
        for cb in callbacks:
            print cb
            getattr(self, cb[1])(infoStackContainer.contentPane(padding='6px',
                                                                pageName=cb[1],
                                                                _class='pbl_roundedGroup',
                                                                datapath='.current_record'))

    def rpc_hv_selectionAsTree(self, selectionName=None, **kwargs):
        selection = self.getUserSelection(selectionName=selectionName, columns=self.hv_columns())
        if hasattr(self, 'selectionAsTree'):
            return self.selectionAsTree(selectionName)
        else:
            return self.tblobj.selectionAsTree(selection)
            