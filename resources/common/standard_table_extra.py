#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class StatsHandler(BaseComponent):
    
    def stats_main(self,parent,**kwargs):
        """docstring for stats_mainpane"""
        bc = parent.borderContainer(**kwargs)
        top = bc.contentPane(region='top',height='6ex',splitter=True)
        left = bc.contentPane(region='left',width='300px',datapath='.tree',splitter=True)
        center = bc.borderContainer(region='center')
        self.stats_top(top)
        self.stats_left(left)
        self.stats_center(center)
    
    def stats_top(self,pane):
        fb = pane.formbuilder(cols=2,border_spacing='4px')
        fb.filteringSelect(values=self.stats_mode_menu(),value='^.tree.tot_mode',lbl='!!Menu')
        fb.button('Run',fire='.tree.totalize')
        
    def stats_left(self,pane):
        pane.tree(storepath='.root',inspect='shift',selectedPath='.currentTreePath',selectedItem='#_grid_total.data')
        pane.data('.root.data',Bag())
        pane.dataRpc('.root.data','stats_totalize',selectionName='=list.selectionName',tot_mode='=.tot_mode',_fired='^.totalize')
        
    def stats_center(self,bc):
        self.includedViewBox(bc.borderContainer(region='top',height='50%',splitter=True),
                             label='!!Analyze Grid',datapath='.grids.total',nodeId='_grid_total',
                             storepath='.data',structpath='.struct',autoWidth=True)
        bc.dataRpc('#_grid_total.struct','stats_get_struct_total',tot_mode='^.tree.tot_mode')
        self.includedViewBox(bc.borderContainer(region='center'),label='!!Analyze Grid',
                             datapath='.grids.detail',nodeId='_grid_detail',
                             storepath='.data',structpath='.struct',autoWidth=True)
                             
        self.includedViewBox(bc.borderContainer(region='center'),
                            label='!!Detail grid',
                            datapath='.grids.detail',nodeId='_grid_detail',
                            storepath='.data',structpath='.struct',
                            table=self.maintable, autoWidth=True,
                            reloader='^stats.tree.currentTreePath',
                            selectionPars=dict(method='stats_get_detail',
                                                flt_path='=stats.tree.currentTreePath',
                                                selectionName='=list.selectionName'))  
                             
                             
                             
                             
                             
        bc.dataRpc('#_grid_detail.struct','stats_get_struct_detail',tot_mode='^.tree.tot_mode')

                        
    def rpc_stats_get_struct_total(self,tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct=self.stats_totals_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            r.cell(**cellargs)
        return struct
    def rpc_stats_get_struct_detail(self,tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct=self.stats_detail_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            r.cell(**cellargs)
        return struct
        
    def rpc_stats_get_detail(self, flt_path=None,selectionName=None, **kwargs):
        if not flt_path:
            return
        fieldpath = flt_path.split('.')[5:]
        print fieldpath
        fieldpath = '.'.join(fieldpath)
        selection = self.unfreezeSelection(self.tblobj, selectionName)
        result = selection.output('grid', subtotal_rows=fieldpath, recordResolver=False)
        return result

    def stats_mode_menu(self):
        """Override this"""
        return
        
    def stats_group_by(self,tot_mode=None):
        """Override this"""
        return
    def stats_sum_cols(self,tot_mode=None):
        """Override this"""
        return
    def stats_keep_cols(self,tot_mode=None):
        """Override this"""
        return
    def stats_collect_cols(self,tot_mode=None):
        """Override this"""
        return
    def stats_distinct_cols(self,tot_mode=None):
        """Override this"""
        return
    def stats_key_col(self,tot_mode=None):
        """Override this"""
        return
    def stats_captionCb(self,tot_mode=None):
        """Override this"""
        return
    def stats_tot_modes(self):
        """Override this"""
        return ''
        
    def rpc_stats_totalize(self,selectionName=None,group_by=None,sum_cols=None,keep_cols=None,
                            collect_cols=None,distinct_cols=None,key_col=None,captionCb=None,
                            tot_mode=None,**kwargs):
        selection = self.unfreezeSelection(self.tblobj, selectionName)
        selection.totalize()
        
        group_by = group_by or self.stats_group_by(tot_mode)
        sum_cols = sum_cols or self.stats_sum_cols(tot_mode)
        keep_cols = keep_cols or self.stats_keep_cols(tot_mode)
        collect_cols = collect_cols or self.stats_collect_cols(tot_mode)
        distinct_cols = distinct_cols or self.stats_distinct_cols(tot_mode)
        key_col = key_col or self.stats_key_col(tot_mode)
        captionCb = captionCb or self.stats_captionCb(tot_mode)
        
        print sum_cols
        if isinstance(group_by,basestring):
            group_by = group_by.split(',')
        if isinstance(sum_cols,basestring):
            sum_cols = sum_cols.split(',')
        if isinstance(keep_cols,basestring):
            keep_cols = keep_cols.split(',')
        if isinstance(collect_cols,basestring):
            collect_cols = collect_cols.split(',')
        if isinstance(distinct_cols,basestring):
            distinct_cols = distinct_cols.split(',')
        group_by = [x.replace('@','_').replace('.','_') for x in group_by]
        keep_cols = [x.replace('@','_').replace('.','_') for x in keep_cols]

        result = selection.totalize(group_by=group_by,sum=sum_cols,keep=keep_cols,
                                    collect=collect_cols,distinct=distinct_cols,
                                    key=key_col,captionCb=captionCb)
        self.freezeSelection(selection,selectionName)
        return result
        
    def stats_captionCb(self,tot_mode):
        def cb(group,row,bagnode):
            return bagnode.label
        return cb