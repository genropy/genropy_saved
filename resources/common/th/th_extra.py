# -*- coding: UTF-8 -*-

# th_extra.py
# Created by Francesco Porcari on 2011-09-12.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

from gnr.core.gnrbag import Bag
from gnr.core.gnranalyzingbag import AnalyzingBag
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrstring import toText

import os

class THStatsHandler(BaseComponent):
    py_requires='foundation/includedview'
    @struct_method
    def th_slotbar_statisticalHandler(self,pane,**kwargs):
        pane.slotButton('!!Statistical View',iconClass='iconbox sum',action = 'SET .selectedPage="th_stats";')
        
    def stats_main(self, parent, **kwargs):
        """docstring for stats_mainpane"""
        frame = parent.framePane(frameCode='main_stats',datapath='.view',pageName='th_stats')
        bc = frame.center.borderContainer()
        self.stats_top(frame.top)
        self.stats_left(bc.contentPane(region='left', width='300px',splitter=True))
        self.stats_center(bc.borderContainer(region='center'))

    def stats_top(self, pane):
        bar = pane.slotToolbar('back,selector,*')
        bar.back.slotButton('!!Main view',action='SET .selectedPage="th_main";',iconClass='iconbox dismiss')
        fb = bar.selector.formbuilder(cols=2, border_spacing='0')
        fb.filteringSelect(values=','.join(["%s:%s" % (k, v) for k, v in self.stats_modes_dict().items()]),
                           value='^.stats.tree.tot_mode', lbl='!!Mode')

    def stats_left(self, pane):
        pane.tree(storepath='.stats.tree.root', inspect='shift', selectedPath='.stats.tree.currentTreePath', labelAttribute='caption',
                  selectedItem='#_grid_total.data', isTree=True, margin='10px', _fired='^.stats.tree.reload_tree', hideValues=True)
        pane.dataRpc('.stats.tree.root', self.stats_totalize, selectionName='=.store?selectionName',
                     tot_mode='^.stats.tree.tot_mode', _if='tot_mode&&(selectedTab=="th_stats") && selectionName', timeout=300000,
                     totalrecords='=.rowcount', selectedTab='=.selectedPage',
                    #_onCalling="""
                    #       batch_monitor.create_local_root(true);
                    #       PUBLISH batch_monitor_on;
                    #""",
                    #_onResult="""
                    #   genro.wdgById('localBatches_root').hide();
                    #   PUBLISH batch_monitor_off;
                    #   FIRE .stats.tree.reload_tree;
                    #""",
                    _onCalling="""genro.wdgById("_stats_load_dlg").show();
                                    SET #_grid_total.data = null;SET #_grid_detail.data = null;""",
                    _onResult='FIRE .stats.tree.reload_tree;genro.wdgById("_stats_load_dlg").hide();',
                     _fired='^.stats.tree.do_totalize')
        pane.dataController("""SET .stats.tree.root.data = null; FIRE .stats.tree.reload_tree; FIRE .stats.tree.do_totalize;""", _fired="^.queryEnd")
        dlg = pane.dialog(nodeId='_stats_load_dlg', title='!!Loading')
        dlg.div(_class='pbl_roundedGroup', height='200px', width='300px').div(_class='waiting')


    def stats_center(self, bc):
        self.includedViewBox(bc.borderContainer(region='top', height='50%', splitter=True, margin='5px'),
                             label='!!Analyze Grid', datapath='.stats.grids.total', nodeId='_grid_total',
                             storepath='.data', structpath='.struct', autoWidth=True, export_action=True)
        bc.dataRpc('#_grid_total.struct', 'stats_get_struct_total', tot_mode='^.stats.tree.tot_mode')
        self.includedViewBox(bc.borderContainer(region='center', margin='5px'),
                             label=self._stats_detail_label,
                             datapath='.stats.grids.detail', nodeId='_grid_detail',
                             storepath='.data', structpath='.struct',
                             table=self.maintable, autoWidth=True, export_action=True,
                             selectionPars=dict(method='stats_get_detail',
                                                flt_path='=%s.view.stats.tree.currentTreePath' %self.maintable.replace('.','_'),
                                                selectionName='=%s.view.store?selectionName' %self.maintable.replace('.','_'),
                                                _autoupdate='=.autoupdate', _if='_autoupdate',
                                                _else='null'))
        bc.dataRpc('#_grid_detail.struct', 'stats_get_struct_detail', tot_mode='^.stats.tree.tot_mode')

    def _stats_detail_label(self, pane):
        fb = pane.formbuilder(cols=2, border_spacing='2px')
        fb.div('^.table?name_plural')
        fb.checkbox(value='^.autoupdate', label='!!Auto update', default=False, lbl=' ', lbl_width='1em')
        fb.dataController("FIRE .reload;", _fired="^%s.view.stats.tree.currentTreePath" %self.maintable.replace('.','_'),
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

    @public_method
    def stats_totalize(self, selectionName=None, group_by=None, sum_cols=None, keep_cols=None,
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

class THHierarchical(BaseComponent):
    @struct_method
    def th_slotbar_hierarchicalHandler(self,pane,**kwargs):
        pane.slotButton('!!Hierarchical View',iconClass='iconbox sitemap',action = 'SET .selectedPage="th_hview";')
        
    def hv_columns(self):
        return None

    def hv_defaultConf(self):
        return dict(parent_code='parent_code', code='code', child_code='child_code')

    def hv_main(self, parent):
        bc = parent.borderContainer(datapath='.view',title='!!Hierarchical View',pageName='th_hview')
        self.hv_tree_view(bc.contentPane(region='left', overflow='auto', width='300px', splitter=True))
        self.hv_right_view(bc.contentPane(region='center',datapath='.hv'))

    def hv_tree_view(self, pane):
        pane.dataRecord('.hv.current_record', self.maintable, pkey='^.selected_id')
        pane.dataRemote('.hv.tree', self.hv_selectionAsTree, selectionName='^.store?selectionName', _if='selectionName')
        tree_kwargs = self.hv_tree_kwargs()
        pane.tree(storepath='.hv.tree',
                  selected_pkey='.hv.selected_id',
                  isTree=False,
                  hideValues=True,
                  selectedItem='.hv.selectedItem',
                  selected_rec_type='.hv.current_rec_type',
                  inspect='shift',
                  selectedLabelClass='selectedTreeNode',
                  labelAttribute='caption',
                  fired='^.queryEnd',
                  **tree_kwargs)

    def hv_tree_kwargs(self):
        return dict()

    def hv_right_view(self, pane):
        return
        infocontainer = pane.borderContainer()
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
        infopane_top.includedView(storepath='.info_table', struct=self.__infoGridStruct())
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
    @public_method
    def hv_selectionAsTree(self, selectionName=None, **kwargs):
        selection = self.getUserSelection(selectionName=selectionName, columns=self.hv_columns())
        if hasattr(self, 'selectionAsTree'):
            return self.selectionAsTree(selectionName)
        else:
            return self.tblobj.selectionAsTree(selection)

    def __infoGridStruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('lbl', name='Field', width='10em', headerStyles='display:none;', cellClasses='infoLabels', odd=False)
        r.cell('val', name='Value', width='10em', headerStyles='display:none;', cellClasses='infoValues', odd=False)
        return struct
