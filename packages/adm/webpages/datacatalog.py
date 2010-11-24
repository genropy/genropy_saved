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


class GnrCustomWebPage(object):
    maintable='adm.datacatalog'
    py_requires='public:Public,gnrcomponents/htablehandler:HTableHandler'
    
    def windowTitle(self):
         return '!!Categories'
         
    def main(self, rootBC, **kwargs):
        bc,top,bottom = self.pbl_rootBorderContainer(rootBC,'Categories')
        self.htableHandler(bc,table='adm.datacatalog',nodeId='datacatalog',rootpath=None,
                            datapath='datacatalog',editMode='bc')
        
    def datacatalog_form(self,parentBC,table=None,disabled=None,**kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='6px',width='440px',dbtable=table,disabled=disabled)
        fb.field('child_code')
        fb.field('description')
