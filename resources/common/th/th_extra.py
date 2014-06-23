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
                  #selectedItem='#totalizer_grid.data',
                  xisTree=True, margin='10px', #_fired='^.stats.tree.reload_tree', 
                  hideValues=True)

        pane.dataController("""var data = this.getRelativeData('.stats.tree.root.'+currpath);
                                SET #totalizer_grid.data = data?data.deepCopy():null;""",currpath='^.stats.tree.currentTreePath')

        pane.dataRpc('.stats.tree.root', self.stats_totalize, selectionName='=.store?selectionName',
                     tot_mode='^.stats.tree.tot_mode', _if='tot_mode&&(selectedTab=="th_stats") && selectionName', timeout=300000,
                     totalrecords='=.rowcount', selectedTab='=.selectedPage',
                    _onCalling="""SET #totalizer_grid.data = null;""",
                    _lockScreen=True,
                    _onResult="""
                    FIRE .stats.tree.reload_tree;""",
                     _fired='^.stats.tree.do_totalize',_else='SET .stats.tree.root = new gnr.GnrBag();')
        pane.dataController("""SET #totalizer_grid.data = null; SET .stats.tree.tot_mode = null; FIRE .stats.tree.reload_tree;
                            """, _fired="^.queryEnd")
        dlg = pane.dialog(nodeId='_stats_load_dlg', title='!!Loading')
        dlg.div(_class='pbl_roundedGroup', height='200px', width='300px').div(_class='waiting')


    def stats_center_analyzer(self,bc,**kwargs):
        frame = bc.frameGrid('totalizer',margin='2px',rounded=5,storepath='.data',
                                datapath='.stats.totalizer',
                                grid__newGrid=False,**kwargs)
        frame.top.slotToolbar('titleslot,*,export',titleslot='!!Analyze Grid')
        frame.dataRpc('.grid.struct', self.stats_get_struct_total, tot_mode='^#main_stats_frame.stats.tree.tot_mode')
    
    def stats_center_detail(self,bc,**kwargs):
        frame = bc.frameGrid('detail',margin='2px',rounded=5,border='1px solid silver',_newGrid=True,
                                datapath='.stats.detail',#structpath='#main_stats_frame.grid.struct',
                                **kwargs)
        frame.dataRpc('.grid.struct', self.stats_get_struct_detail, tot_mode='^#main_stats_frame.stats.tree.tot_mode')
        frame.top.slotToolbar('titleslot,*,export',titleslot='!!Details Grid')
        frame.grid.selectionStore(table=self.maintable,
                                    method=self.stats_get_detail,
                                    flt_path='^#main_stats_frame.stats.tree.currentTreePath',
                                    selectionName='=#main_stats_frame.store?selectionName',
                                    _if='flt_path',_else='this.store.clear();')
        
    def stats_center(self,bc):
        self.stats_center_analyzer(bc,region='top',height='50%')
        self.stats_center_detail(bc,region='center')
        
    @public_method
    def stats_get_struct_total(self, tot_mode='*'):
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
    
    @public_method
    def stats_get_struct_detail(self, tot_mode='*'):
        struct = self.newGridStruct(maintable=self.maintable)
        r = struct.view().rows()
        grid_struct = self.stats_detail_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            r.fieldcell(**cellargs)
        return struct
    
    @public_method
    def stats_get_detail(self, flt_path=None, selectionName=None, **kwargs):
        selection = self.unfreezeSelection(self.tblobj, selectionName)
        if flt_path == 'data':
            flt_path = None
        else:
            flt_path = flt_path.replace('data.','')
        result = selection.output('grid', subtotal_rows=flt_path,limit=500, recordResolver=False)
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
                                  pkeys=pkeys, addPkeyColumn=True,excludeDraft=False,ignorePartition=True)
        return query.selection()

    @public_method
    def stats_totalize(self, selectionName=None, group_by=None, sum_cols=None, keep_cols=None,
                           collect_cols=None, distinct_cols=None, key_col=None, captionCb=None,
                           tot_mode=None, **kwargs):
        print 'totalizing'
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
        analyzer.analyze(selection,group_by=group_by, sum=sum_cols, keep=keep_cols,
                            collect=collect_cols, distinct=distinct_cols,
                            key=key_col, captionCb=captionCb)
        selection.analyzeBag = analyzer
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
        frame = parent.framePane(datapath='.view',pageName='th_hview',center_widget='BorderContainer')
        bar = frame.top.slotToolbar('back,*,hvtitle,*,hv_lock')
        bar.back.slotButton('!!Main view',action='SET .selectedPage="th_main";',iconClass='iconbox dismiss')
        bar.hvtitle.div('^.hv.form.record?caption',font_weight='bold',color='gray')
        self.hv_tree_view(frame.contentPane(region='left', overflow='auto', width='300px', splitter=True))
        form = frame.frameForm(frameCode='hv_center',table=self.maintable,region='center',
                        form_locked=True,datapath='.hv.form',store=True)
        form.dataController("""
                            var currPkey = currPkey || "*norecord*";
                            frm.load({destPkey:currPkey});""",
                            currPkey='^.#parent.selected_id',frm=form.js_form)
        self.hv_form(form)
        bar.hv_lock.slotButton('!!Locker',iconClass='iconbox lock',
                    action='frm.publish("setLocked","toggle");',
                    frm=form.js_form,
                    subscribe_form_hv_center_form_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'iconbox lock':'iconbox unlock');"""
                    )
        
        
        self.hv_frame(frame)
    
    def hv_frame(self,frame):
        return

    def hv_form(self,form):
        pass
        
    def hv_tree_view(self, pane):
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
                  fired='^.rebuildTree',
                  **tree_kwargs)
        pane.dataController('FIRE .rebuildTree;', _fired='^.queryEnd', _delay='1') #waiting resolver data

    def hv_tree_kwargs(self):
        return dict()

   
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
