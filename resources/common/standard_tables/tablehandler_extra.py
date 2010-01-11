#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import toText
import os

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
        fb.filteringSelect(values=','.join(["%s:%s" %(k,v) for k,v in self.stats_modes_dict().items()]),
                            value='^.tree.tot_mode',lbl='!!Mode')
        #fb.button('Run',fire='.tree.totalize')
        
    def stats_left(self,pane):
        pane.tree(storepath='.root',inspect='shift',selectedPath='.currentTreePath',labelAttribute='caption',
                 selectedItem='#_grid_total.data',isTree=True,margin='10px',_fired='^.reload_tree',hideValues=True)
        pane.dataRpc('.root','stats_totalize',selectionName='=list.selectionName',
                        tot_mode='^.tot_mode',_if='tot_mode&&(selectedTab==1)',timeout=300000,
                        totalrecords='=list.rowcount',selectedTab='=list.selectedTab',
                        _onCalling="""genro.wdgById("_stats_load_dlg").show();
                                     SET #_grid_total.data = null;SET #_grid_detail.data = null;""",
                        _onResult='FIRE .reload_tree;genro.wdgById("_stats_load_dlg").hide();',
                        _fired='^.do_totalize')
        pane.dataController("""SET .root.data = null; FIRE .reload_tree; FIRE .do_totalize;""",_fired="^list.queryEnd")
        dlg = pane.dialog(nodeId='_stats_load_dlg',title='!!Loading')
        dlg.div(_class='pbl_roundedGroup',height='200px',width='300px').div(_class='waiting')
        
        
    def stats_center(self,bc):
        self.includedViewBox(bc.borderContainer(region='top',height='50%',splitter=True,margin='5px'),
                             label='!!Analyze Grid',datapath='.grids.total',nodeId='_grid_total',
                             storepath='.data',structpath='.struct',autoWidth=True,export_action=True)
        bc.dataRpc('#_grid_total.struct','stats_get_struct_total',tot_mode='^.tree.tot_mode')
        self.includedViewBox(bc.borderContainer(region='center',margin='5px'),
                            label=self._stats_detail_label,
                            datapath='.grids.detail',nodeId='_grid_detail',
                            storepath='.data',structpath='.struct',
                            table=self.maintable, autoWidth=True,export_action=True,
                            selectionPars=dict(method='stats_get_detail',
                                                flt_path='=stats.tree.currentTreePath',
                                                selectionName='=list.selectionName',
                                                _autoupdate='=.autoupdate',_if='_autoupdate',
                                                _else='null'))                     
        bc.dataRpc('#_grid_detail.struct','stats_get_struct_detail',tot_mode='^.tree.tot_mode')
    
    def _stats_detail_label(self,pane):
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        fb.div(self.pluralRecordName())
        fb.checkbox(value='^.autoupdate',label='!!Auto update',default=False,lbl=' ',lbl_width='1em')
        fb.dataController("FIRE .reload;",_fired="^stats.tree.currentTreePath",
                            autoupdate='^.autoupdate')

                        
    def rpc_stats_get_struct_total(self,tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct=self.stats_totals_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            if not 'dtype' in cellargs:
                if cellargs['field'].startswith('sum_') or cellargs['field'].startswith('avg_'):
                    cellargs['dtype'] = 'N' 
                elif cellargs['field'] == 'count' or cellargs['field'].startswith('count_'):
                    cellargs['dtype'] = 'L' 
            r.cell(**cellargs)
        return struct
    def rpc_stats_get_struct_detail(self,tot_mode='*'):
        struct = self.newGridStruct()
        r = struct.view().rows()
        grid_struct=self.stats_detail_cols(tot_mode=tot_mode)
        for cellargs in grid_struct:
            r.fieldcell(**cellargs)
        return struct
        
    def rpc_stats_get_detail(self, flt_path=None,selectionName=None, **kwargs):
        if not flt_path:
            return
        fieldpath = flt_path.split('.')[5:]
        fieldpath = '.'.join(fieldpath)
        selection = self.unfreezeSelection(self.tblobj, selectionName)
        result = selection.output('grid', subtotal_rows=fieldpath, recordResolver=False)
        return result

    def stats_modes_dict(self):
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
    
    def stats_columns(self):
        """Override this"""
        return 
        
    def stats_get_selection(self,selectionName):
        if self.stats_columns():
            cust_selectionName = '%s_cust' %selectionName
            if not os.path.exists(self.pageLocalDocument(cust_selectionName)):
                return self.stats_create_custom_selection(selectionName,cust_selectionName)
            else:
                selectionName = cust_selectionName
        return self.unfreezeSelection(self.tblobj, selectionName)
        
    def stats_create_custom_selection(self,selectionName,cust_selectionName):
        pkeys = self.unfreezeSelection(self.tblobj, selectionName).output('pkeylist')
        query = self.tblobj.query(columns=self.stats_columns(),
                                    where='t0.%s in :pkeys' % self.tblobj.pkey,
                                    pkeys=pkeys,addPkeyColumn=False)
        return query.selection()
        
        
    def rpc_stats_totalize(self,selectionName=None,group_by=None,sum_cols=None,keep_cols=None,
                            collect_cols=None,distinct_cols=None,key_col=None,captionCb=None,
                            tot_mode=None,**kwargs):
        selection = self.stats_get_selection(selectionName)
        selection.totalize()
        
        group_by = group_by or self.stats_group_by(tot_mode)
        sum_cols = sum_cols or self.stats_sum_cols(tot_mode)
        keep_cols = keep_cols or self.stats_keep_cols(tot_mode)
        collect_cols = collect_cols or self.stats_collect_cols(tot_mode)
        distinct_cols = distinct_cols or self.stats_distinct_cols(tot_mode)
        key_col = key_col or self.stats_key_col(tot_mode)
        captionCb = captionCb or self.stats_captionCb(tot_mode)
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
        def date_converter(mode):
            datefield,formatmode =mode.split(':')     
            return lambda r: toText(r[datefield],format=formatmode,locale=self.locale)
        for k,x in enumerate(group_by):
            if isinstance(x,basestring):
                if x.startswith('#DATE='):
                    group_by[k] = date_converter(x[6:])
                else:
                    group_by[k] = x.replace('@','_').replace('.','_')
        if keep_cols:
            keep_cols = [x.replace('@','_').replace('.','_') for x in keep_cols]
        if distinct_cols:
            distinct_cols = [x.replace('@','_').replace('.','_') for x in distinct_cols]
        result = Bag()
        data = selection.totalize(group_by=group_by,sum=sum_cols,keep=keep_cols,
                                    collect=collect_cols,distinct=distinct_cols,
                                    key=key_col,captionCb=captionCb)
        self.freezeSelection(selection,selectionName)
        result.setItem('data',data,caption=self.stats_modes_dict()[tot_mode])
        return result
        
    def stats_captionCb(self,tot_mode):
        def cb(group,row,bagnode):
            return bagnode.label
        return cb