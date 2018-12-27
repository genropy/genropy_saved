# -*- coding: utf-8 -*-
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
from gnr.core.gnrdecorator import public_method

class WorkbenchManager(BaseComponent):
    js_requires= 'gnrcomponents/workbench/workbench'
    css_requires = 'gnrcomponents/workbench/workbench'

    @struct_method
    def wb_workbenchPane(self,parent,code,**kwargs):

        workbench = parent.contentPane(nodeId=code,**kwargs)
        m = workbench.menu(_class='smallMenu',action='WorkbenchManager.addElement(this,$3,$1.dflt)')
        m.menuline('Add Squarebox',dflt=dict(tag='div',rounded=6,background='red',height='100px',width='100px',moveable=True))
        m.menuline('Add Textarea',dflt=dict(tag='SimpleTextArea',lbl='Textarea',height='100px',width='180px',moveable=True,value='^.$name'))
        m.menuline('Add Textbox',dflt=dict(tag='textbox',lbl='Textbox',width='12em',moveable=True,value='^.$name'))


        workbench.dataController("WorkbenchManager.onChanges(this,pane,elements,_triggerpars.kw,_reason)",
                             pane=workbench,elements='^#%s'%code,_if='elements')