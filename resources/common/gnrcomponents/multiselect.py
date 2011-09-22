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
"""
multiselect.py

Created by Saverio Porcari on 2010-01-25.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.core.gnrbag import Bag
from gnr.web.gnrbaseclasses import BaseComponent

class MultiSelect(BaseComponent):
    py_requires = 'foundation/includedview:IncludedView'
    js_requires = 'gnrcomponents/multiselect'

    def multiSelect(self, bc, nodeId=None, table=None, datapath=None, struct=None, label=None, values=None,
                    readColumns=None,
                    reloader=None, filterOn=None, hiddencolumns=None, selectionPars=None, order_by=None,
                    showSelected=False, readCol=None, hasToolbar=False, _onStart=False, showFooter=True, **kwargs):
        assert struct, 'struct is mandatory'
        if callable(struct) and not isinstance(struct, Bag):
            struct = struct(self.newGridStruct(table))
        values = values or '=.checkedList'
        readCol = readCol or '_pkey'
        if readCol != '_pkey':
            assert showSelected == False, 'to use this mode readCol must be "_pkey"'
        r = struct['#0']['#0'] # view.rows
        r.cell('_checkedrow', name=' ', width='2em',
               format_trueclass='checkboxOn',
               # styles='background:none!important;border:0;',
               format_falseclass='checkboxOff', classes='row_checker',
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
                                      """ % (readCol, values),
               dtype='B', calculated=True, _pos=0)
        if not selectionPars:
            if order_by:
                selectionPars = dict(order_by=order_by)
            else:
                selectionPars = dict()
        viewpars = dict(label=label, struct=struct, filterOn=filterOn, table=table,
                        hiddencolumns=hiddencolumns, reloader=reloader, autoWidth=True,
                        hasToolbar=hasToolbar, _onStart=_onStart)
        checkboxGridBC = bc
        checkboxGridDatapath = datapath
        if showSelected and showFooter:
            footer = bc.contentPane(region='bottom', _class='pbl_roundedGroupBottom')
            footer.button('Back', action='SET %s.selectedGrid=0;' % datapath)
            footer.button('Next', action='FIRE #%s_result.reload; SET %s.selectedGrid=1;' % (nodeId, datapath))
            stack = bc.stackContainer(region='center', datapath=datapath, selected='^.selectedGrid')
            checkboxGridBC = stack.borderContainer()
            checkboxGridDatapath = '.gridcheck'

        if 'applymethod' in selectionPars:
            selectionPars['apply_callAfter'] = selectionPars['applymethod']
        selectionPars['apply_checkedRows'] = '=%s' % values
        selectionPars['apply_readCol'] = readCol
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
                                          """ % values,
                                      selectrows="^.selectrows", selection='=.selection', _if='selection',
                                      readCol=readCol, datapath=checkboxGridDatapath)
        if showFooter:
            footer = self.ms_footer
        else:
            footer = None
        self.includedViewBox(checkboxGridBC, datapath=checkboxGridDatapath,
                             selectionPars=selectionPars, nodeId=nodeId, footer=footer, **viewpars)
        if showSelected:
            selectionPars_result = dict(where='$%s IN :checked' % self.db.table(table).pkey,
                                        checked='=%s' % values.strip('^='), _if='checked')

            self.includedViewBox(stack.borderContainer(_class='hide_row_checker'), nodeId='%s_result' % nodeId,
                                 datapath='.resultgrid', selectionPars=selectionPars_result,
                                 **viewpars)

    def ms_footer(self, pane, **kwargs):
        pane.button('!!Select All', fire_all='.selectrows')
        pane.button('!!Unselect All', fire_none='.selectrows')


    def rpc_ms_setCheckedOnReload(self, selection, checkedRows=None, callAfter=None, readCol=None, **kwargs):
        checkedRows = checkedRows or []
        if readCol == '_pkey' or readCol == '*':
            readCol = 'pkey'

        def cb(row):
            result = dict(_checkedrow=False)
            if row[readCol] in checkedRows:
                result['_checkedrow'] = True
            else:
                result['_checkedrow'] = False
            return result

        selection.apply(cb)
        if callAfter:
            callAfter = getattr(self, 'rpc_%s' % callAfter, None)
            if callAfter:
                callAfter(selection, **kwargs)
        