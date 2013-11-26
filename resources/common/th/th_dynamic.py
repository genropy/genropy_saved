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

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method

from gnr.core.gnrbag import Bag

class DynamicTableHandler(BaseComponent):
    @extract_kwargs(th=True)
    @struct_method
    def th_dynamicTableHandler(self,pane,datapath=None,nodeId=None,table=None,th_kwargs=None,**kwargs):
        rootId = nodeId or 'lookup_root'
        datapath = datapath or 'main'
        pane.contentPane(nodeId=rootId,datapath=datapath,_anchor=True,overflow='hidden',**kwargs).remote(self.dh_remoteTh,table=table,
                                            _onRemote='FIRE #ANCHOR.load_data;',rootId=rootId,th_kwargs=th_kwargs)

    def dh_lookupTablesDefaultStruct(self,struct):
        r = struct.view().rows()
        for k,v in struct.tblobj.model.columns.items():
            attr = v.attributes
            if attr.get('counter'):
                r.fieldcell(k,hidden=True,counter=True)
            elif not (attr.get('_sysfield') or attr.get('dtype') == 'X'):
                r.fieldcell(k,edit=attr['cell_edit'] if 'cell_edit' in attr else True)

    @public_method
    def dh_remoteTh(self,pane,table=None,fixeed_table=None,rootId=None,th_kwargs=None):
        pane.data('.mainth',Bag())
        if not table:
            pane.div('!!Select a table from the popup menu',margin_left='5em',margin_top='5px', color='#8a898a',text_align='center',font_size='large')
        else:
            wdg = th_kwargs.get('wdg','inline')
            tblobj= self.db.table(table)
            getattr(pane,'%sTableHandler' %wdg)(table=table,viewResource='LookupView',datapath='.dynamith',autoSave=False,
                                    nodeId='%s_mainth' %rootId,configurable='*',
                                    view_structCb=self.dh_lookupTablesDefaultStruct,condition_loaddata='^#ANCHOR.load_data',
                                    grid_selfDragRows=tblobj.attributes.get('counter'),**th_kwargs)


