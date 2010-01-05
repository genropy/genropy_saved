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

"""
Component for thermo:
"""
from gnr.web.gnrwebpage import BaseComponent

class DynamicEditor(BaseComponent):
    def dynamicEditor(self, container, value,contentPars=None,disabled=None,
                      nodeId=None,editorHeight='',**kwargs):
        nodeId = nodeId or self.getUuid()
        stackId = "%s_stack"%nodeId
        editorId = "%s_editor"%nodeId
        st = container.stackContainer(nodeId=stackId,**contentPars)
        viewPane = st.contentPane(_class='pbl_viewBox')
        viewPane.div(innerHTML=value,_class='formattedBox')
        editPane = st.contentPane(overflow='hidden',connect_resize="""var editor = genro.wdgById('%s');
                                                   var height = this.widget.domNode.clientHeight-30+'px';
                                                   dojo.style(editor.iframe,{height:height});"""%editorId)
        editPane.editor(value=value,nodeId=editorId,**kwargs)
        st.dataController('genro.wdgById("%s").setSelected(disabled?0:1)'%stackId,
                        disabled=disabled,fired='^gnr.onStart')
                        
class PeriodCombo(BaseComponent):
    def _pc_datesHints(self):
        today = datetime.date.today()
        dates = []
        dates.append(str(today.year))
        dates.append(str(today.year - 1))
        for k,v in DATEKEYWORDS[self.locale[:2]].items():
            if k != 'to':
                if isinstance(v,tuple):
                    v = v[0]
                dates.append(v)
        dates = ','.join(dates)
        return dates
        
    def periodCombo(self, fb,period_store = None,value=None , lbl=None,**kwargs):
        value = value or '^.period_input'
        period_store = period_store or '.period'
        fb.dataRpc(period_store, 'decodeDatePeriod', datestr=value, 
                    _fired='^gnr.onStart',
                    _onResult="""if (result.getItem("valid")){
                                 }else{
                                 result.setItem('period_string','Invalid period');
                                 }""")
        fb.combobox(lbl=lbl or '!!Period',value=value, width='16em',tip='^%s.period_string'%period_store,
                    values=self._pc_datesHints(), margin_right='5px',padding_top='1px',**kwargs)