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
Component for referto:
"""
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/dynamicform'

         
    def main(self, root, **kwargs):
        self.dynamicForm(root,nodeId='myform',storepath='test',reloader='^gnr.onStart',
                        row_types={'phone':'!!Phone','email':"Email",'fax':'Fax'},
                        type_field='contact_type',height='300px',width='400pz')
        root.button('Save',action='var values = GET test; alert(values.toXml());')
                        
    def myform_row(self,row,disabled=None,**kwargs):
        fb = row.formbuilder(cols=2, border_spacing='2px',disabled=disabled)
        fb.combobox(value='^.location',values='Home,Work,Main',lbl='Loc.')
        fb.textbox(value='^.content')
    def myform_email_row(self,row,disabled=None,**kwargs):
        fb = row.formbuilder(cols=1, border_spacing='2px',disabled=disabled)
        fb.textbox(value='^.content',lbl='Url')