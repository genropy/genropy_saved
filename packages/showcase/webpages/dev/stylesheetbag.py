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

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='foundation/tools:CSSHandler'
    css_requires='public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return ''
         
    def main(self, rootBC, **kwargs):
        rootBC.css('.pieretto','height:100px;width:300px;margin:5px;background-color:red;border:1px solid green;')
        bc = rootBC.borderContainer(region='center')
        top = bc.contentPane(region='top',_class='pbl_roundedGroupLabel')
        #top.button('Create',action='SET gnr.stylesheet.root = genro.dom.styleSheetsToBag();')
        left = bc.contentPane(region='left',background_color='silver',width='300px')
        #left.data('gnr.stylesheet.root',Bag(),caption='Styles')
        #this._main.subscribe('sourceTriggers',{'any':dojo.hitch(this, "nodeTrigger")});
       #left.dataController("""var root=genro._('gnr.stylesheet');
       #                           root.setBackRef();
       #                           root.subscribe('styleTrigger',{'any':dojo.hitch(genro.dom, "styleTrigger")});""",
       #                            _onStart=True)
        left.tree(storepath='gnr',inspect ='shift',labelAttribute='selectorText')
        center = bc.contentPane(region='center')
        center.div(_class='pieretto')
        