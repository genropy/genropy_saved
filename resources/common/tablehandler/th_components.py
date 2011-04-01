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
print_utils.py

Created by Saverio Porcari on 2009-06-29.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

from gnr.core.gnrbag import Bag



class StackTableHandler(BaseComponent):
    py_requires='tablehandler/th_list:TableHandlerListBase,tablehandler/th_form:TableHandlerFormBase'
    @struct_method
    def th_stackTableHandler(self,pane,table=None,datapath=None,formName=None,viewName=None,**kwargs):
        pkg,tablename = table.split('.')
        tableCode = table.replace('.','_')
        defaultName = 'th_%s' %tablename
        formName = formName or defaultName
        viewName = viewName or defaultName
        self.mixinComponent(pkg,'tables',tablename,'%s:Form' %formName)
        self.mixinComponent(pkg,'tables',tablename,'%s:View' %viewName)
        sc = pane.stackContainer(datapath=datapath or '.%s'%tableCode,selectedPage='^.selectedPage',**kwargs)
        viewpage = sc.listPage(frameCode='%s_list' %tableCode,table=table,
                                linkedForm='%s_form' %tableCode,pageName='view')
        formpage = sc.formPage(frameCode='%s_form' %tableCode,table=table,pageName='form')
        formpage.attributes['formsubscribe_onLoaded'] = 'SET .#parent.selectedPage="form";'
        formpage.attributes['formsubscribe_onDismissed'] = 'SET .#parent.selectedPage="view";'
        formpage.store.attributes['parentStore'] = '%s_list_grid' %tableCode
        viewpage.iv.attributes['selfsubscribe_add'] = 'genro.getForm(this.attr.linkedForm).load({destPkey:"*newrecord*"});'
        viewpage.iv.attributes['selfsubscribe_del'] = 'var pkeyToDel = this.widget.getSelectedPkeys(); console.log(pkeyToDel);' #'genro.getForm(this.attr.linkedForm).deleteItem({});'
        return sc