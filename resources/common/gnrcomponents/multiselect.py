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
    js_requires='gnrcomponents/multiselect'
    def multiSelect(self,bc,nodeId=None,table=None,datapath=None,struct=None,label=None,values=None,readColumns=None,
                             reloader=None,filterOn=None,hiddencolumns=None,selectionPars=None,order_by=None,
                             showSelected=False, readCol=None,**kwargs):
        assert not 'footer' in kwargs, 'remove footer par'

        assert struct, 'struct is mandatory'
        if callable(struct):
            struct = struct(self.newGridStruct(table))
        values= values or '=.checkedList'           
        readCol = readCol or '_pkey' 
        if readCol != '_pkey':
            assert showSelected==False, 'to use this mode readCol must be "_pkey"'
        struct['#0']['#0'].cell('_checkedrow',name=' ',width='2em',
                    format_trueclass='checkboxOn',
                    cellStyles='background:none!important;border:0;',
                    format_falseclass='checkboxOff',classes='row_checker',
                    #format_onclick='MultiSelectComponent.toggle_row(kw.rowIndex, e, this,"%s");' %values, 
                    format_onclick="""var readCol = '%s';
                                      var result = [];
                                      var idx = kw.rowIndex;
                                      var nodes = this.widget.storebag().getNodes();
                                      var row = nodes[idx];
                                      var rowattrs = row.getAttr();
                                      rowattrs['_checkedrow'] = !rowattrs['_checkedrow'];
                                      row.setAttr(rowattrs);
                                      var cb = function(n){
                                                        if(n.attr._checkedrow){
                                                            if(readCol=='*'){
                                                                result.push(n.attr);
                                                            }else{
                                                                result.push(n.attr[readCol]);
                                                            }
                                                        }
                                                     };
                                      dojo.forEach(nodes,cb);
                                      this.setRelativeData('%s',result);
                                      """ %(readCol,values),
                    dtype='B',calculated=True,_pos=0)
        if not selectionPars:
            if order_by:
                selectionPars=dict(order_by=order_by) 
            else:
                selectionPars=dict()
        viewpars = dict(label=label,struct=struct,filterOn=filterOn,table=table,
                         hiddencolumns=hiddencolumns,reloader=reloader,autoWidth=True)
        checkboxGridBC = bc
        checkboxGridDatapath = datapath
        if showSelected:
            footer = bc.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
            footer.button('Back',action='SET %s.selectedGrid=0;' %datapath)
            footer.button('Next',action='FIRE #%s_result.reload; SET %s.selectedGrid=1;' %(nodeId,datapath))
            stack = bc.stackContainer(region='center',datapath=datapath,selected='^.selectedGrid')
            checkboxGridBC = stack.borderContainer()
            checkboxGridDatapath = '.gridcheck'
        
        if 'applymethod' in selectionPars:
            selectionPars['apply_callAfter'] = selectionPars['applymethod']
        selectionPars['apply_checkedRows'] = '=%s' %values
        selectionPars['applymethod'] = 'ms_setCheckedOnReload'
        
        checkboxGridBC.dataController("""var nodes = selection.getNodes();
                                         var result = [];
                                         dojo.forEach(nodes,function(row){
                                            var attrs = row.getAttr();
                                            attrs._checkedrow = (selectrows=='all');
                                            if(selectrows=='all'){
                                                if(readCol=='*'){
                                                    result.push(row.attr);
                                                }else{
                                                    result.push(row.attr[readCol]);
                                                }
                                            }
                                            row.setAttr(attrs);
                                        })
                                        SET %s = result;
                                          """ %values,
                                        selectrows="^.selectrows",selection='=.selection',_if='selection',
                                        readCol=readCol,datapath=checkboxGridDatapath)
        self.includedViewBox(checkboxGridBC,datapath=checkboxGridDatapath,
                            selectionPars=selectionPars,nodeId=nodeId,footer=self.ms_footer,**viewpars)
        if showSelected:
            selectionPars_result = dict(where='$%s IN :checked' %self.db.table(table).pkey,
                                    checked='=%s' %values,_if='checked')

            self.includedViewBox(stack.borderContainer(_class='hide_row_checker'),nodeId='%s_result' %nodeId,
                                    datapath='.resultgrid',selectionPars=selectionPars_result,
                                    **viewpars)
                                    
    def ms_footer(self,pane,**kwargs):
        pane.button('!!Select All',fire_all='.selectrows')
        pane.button('!!Unselect All',fire_none='.selectrows')

        
        
    def rpc_ms_setCheckedOnReload(self,selection,checkedRows=None,callAfter=None,**kwargs):
        checkedRows = checkedRows or []
        print checkedRows
        def cb(row):
            result = dict(_checkedrow=False)
            if row['pkey'] in checkedRows:
                result['_checkedrow'] = True
            else:
                result['_checkedrow'] = False
            return result
        selection.apply(cb)
        if callAfter:
            callAfter = getattr(self,'rpc_%s' %callAfter,None)
            if callAfter:
                callAfter(selection,**kwargs)
        