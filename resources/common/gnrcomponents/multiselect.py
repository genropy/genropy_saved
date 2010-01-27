#!/usr/bin/env python
# encoding: utf-8
"""
multiselect.py

Created by Saverio Porcari on 2010-01-25.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip

import os


class MultiSelect(BaseComponent):
    py_requires='foundation/includedview:IncludedView'
    def multiSelect(self,bc,nodeId=None,table=None,datapath=None,struct=None,label=None,values=None,
                             reloader=None,filterOn=None,hiddencolumns=None,selectionPars=None,order_by=None,
                             showSelected=False,
                             **kwargs):
        assert not 'footer' in kwargs, 'remove footer par'

        assert struct, 'struct is mandatory'
        if callable(struct):
            struct = struct(self.newGridStruct(table))
        struct['#0']['#0'].cell('_checkedrow',name=' ',width='2em',
                    format_trueclass='checkboxOn',
                    styles='background:none!important;border:0;',
                    format_falseclass='checkboxOff',classes='row_checker',
                    format_onclick='IVSelectionSearchComponent.check_row(kw.rowIndex, e, this,"tags");',
                    dtype='B',calculated=True)
        if not selectionPars:
            if order_by:
                selectionPars=dict(order_by=order_by) 
            else:
                selectionPars=dict()
        viewpars = dict(label=label,struct=struct,filterOn=filterOn,table=table,
                         hiddencolumns=hiddencolumns,reloader=reloader,autoWidth=True)
        
        checkboxGridBC = bc
        if showSelected:
            footer = bc.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
            footer.button('Back',action='SET %s.selectedGrid=0;' %datapath)
            footer.button('Next',action='FIRE #%s_result.reload; SET %s.selectedGrid=1;' %(nodeId,datapath))
            checked= values or '=.#parent.checkedList'
            stack = bc.stackContainer(region='center',datapath=datapath,selected='^.selectedGrid')
            checkboxGridBC = stack.borderContainer()
        self.includedViewBox(checkboxGridBC,datapath='.gridcheck',
                            selectionPars=selectionPars,nodeId=nodeId,**viewpars)
        selectionPars_result = dict(where='$%s IN :checked' %self.db.table(table).pkey,
                                    checked=checked,_if='checked')

        self.includedViewBox(stack.borderContainer(_class='hide_row_checker'),nodeId='%s_result' %nodeId,
                             datapath='.resultgrid',selectionPars=selectionPars_result,
                             **viewpars)