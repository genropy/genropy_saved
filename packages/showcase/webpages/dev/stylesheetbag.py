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
    py_requires = 'foundation/tools:CSSHandler'
    css_requires = 'public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''

    def windowTitle(self):
        return ''

    def main(self, rootBC, **kwargs):
        rootBC.styleSheet(
                '.myrect {height:100px;width:100px;float:right;margin:5px;background-color:red;border:1px solid green;}'
                , cssTitle='test')
        bc = rootBC.borderContainer(region='center')
        left = bc.contentPane(region='left', width='200px', splitter=True)
        left.dataController("""var kw = $2.kw;
                            if(kw.reason){
                                genro.dom.styleSheetBagSetter($1.getValue(),kw.reason.attr);                                   
                            }
                            """, _fired="^csshandler")

        fb = left.formbuilder(cols=1)
        fb.horizontalSlider(value='^csshandler.rect.size', lbl='Height', minimum=50, width='120px',
                            maximum=300, intermediateChanges=True, _set_height='.myrect:#+"px"',
                            _set_font_size='.myrect:#-30+"px"')
        center = bc.contentPane(region='center')
        for k in range(100):
            x = center.div(_class='myrect')
            x.span('%i' % k)
        