# -*- coding: utf-8 -*-
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag


class SelectionCompare(BaseComponent):
    py_requires='th/th:TableHandler,public:Public'
    #css_requires='gnrcomponents/pagededitor/pagededitor'
    #js_requires='gnrcomponents/pagededitor/pagededitor'

    @extract_kwargs(left=True,right=True,onDropRpc=True)
    @struct_method
    def comp_compareSelections(self, parent, nodeId=None, datapath=None,table=None, condition=None, 
                                viewResource=None, left_kwargs=None, compareField=None,
                                right_kwargs=None, onDropRpc=None,onDropRpc_kwargs=None,**kwargs):
        nodeId = nodeId or '%s_comp' %table.replace('.','_')
        frame = parent.framePane(frameCode=nodeId, datapath=datapath, _anchor=True,**kwargs)
        left_kwargs['condition'] = left_kwargs.get('condition') or condition
        right_kwargs['condition'] = right_kwargs.get('condition') or condition
        bc=frame.center.borderContainer()
        compareField = compareField or '_pkey'
        self.comp_toolbar(frame.top)
        left_frame = bc.roundedGroupFrame(title=left_kwargs.pop('title','Left selection'), region='left', width='50%')
        left_th = self._comparingGrid(left_frame,table=table,
                                                 viewResource=viewResource,
                                                 datapath='.left',
                                                 sections_channel=nodeId,
                                                 nodeId='%s_left' % nodeId,
                                                 compareField=compareField,
                                                 **left_kwargs)
        frame.left_side = left_frame
        right_frame = bc.roundedGroupFrame(title=right_kwargs.pop('title','Right selection'), region='center')
        right_th = self._comparingGrid(right_frame, table=table,
                                       viewResource=viewResource,
                                       datapath='.right',
                                       sections_channel=nodeId,
                                       sections_hidden=True,
                                       nodeId='%s_right' % nodeId,
                                       compareField=compareField,
                                       **right_kwargs)
        frame.right_side = right_frame
        leftgrid = left_th.view.grid
        leftgridattr = leftgrid.attributes
        rightgrid = right_th.view.grid
        rightgridattr = rightgrid.attributes
        if onDropRpc:
            rpcNodeId = '%s_rpcdrop' %nodeId
            ondropcb="""
                        if(data && data.table==this.attr.table){
                            var side = this.attr.nodeId.split('_')[2];
                            genro.nodeById('%s').publish('rowsFromSide',{pkeys:data.pkeys,side:side});
                        }""" %rpcNodeId
            leftgridattr.update(onDrop_dbrecords =ondropcb,dropTarget_grid='dbrecords')
            rightgridattr.update(onDrop_dbrecords = ondropcb,dropTarget_grid='dbrecords')
            bc.dataRpc(None,onDropRpc,selfsubscribe_rowsFromSide=True,nodeId=rpcNodeId,**onDropRpc_kwargs)

        leftgridattr.update(
            filteringGrid=rightgrid.js_sourceNode(),
            filteringColumn=compareField,
            filteringMode='^#ANCHOR.filteringMode'
        )

        rightgridattr.update(
            filteringGrid=leftgrid.js_sourceNode(),
            filteringColumn=compareField,
            filteringMode='^#ANCHOR.filteringMode'
        )

        return frame

    def comp_toolbar(self, top):
        bar = top.slotToolbar('*,mb_filters,*')
        bar.mb_filters.multibutton(value='^.filteringMode' , values='disabled:All,include:Intersection,exclude:Differences')


    def _comparingGrid(self, pane,sections_channel=None,sections_hidden=None,**kwargs):
        return pane.plainTableHandler(view_sections_ALL_channel=sections_channel,
                                    view_sections_ALL_hidden=sections_hidden,
                                    **kwargs)
