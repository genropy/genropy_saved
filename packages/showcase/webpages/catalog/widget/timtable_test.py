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
import random

class GnrCustomWebPage(object):
    #py_requires='public:Public'
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return 'Scrolltest'
         
    def main(self, root, **kwargs):
        root.data('zoomFactor',1)
        root.css('.zoommed',"""z-index:99; 
                                 -moz-transform-origin: center; 
                                 -moz-transform: scale(2);
                                 cursor:pointer;
                                 """)
        root.horizontalSlider(value='^zoomFactor', minimum=0, maximum=1,
                                intermediateChanges=True,width='15em',float='right')
        box = root.div(height='500px',width='800px',border='1px solid black',
                        overflow_x='auto',overflow_y='auto')
        inner = box.div(zoomFactor='^zoomFactor',
                        border='1px dotted navy',position='relative')
        h = 90
        w = 140
        for y in range(36):
            cy = y*100+1
            for x in range(36):
                cx = x*150+1
                if random.random() > .5:
                    disp = random.random()
                    if disp > .7:
                        color = 'green'
                    elif disp > .3:
                        color = 'red'
                    else:
                        color = 'orange'
                        
                    app = inner.div(background=color,position='absolute',top='%ipx' %cy,left='%ipx' %cx,
                            height='%ipx' %h,width='%ipx' %w,border='1px solid gray',
                            _class='rounded_max shadow_2',connect_onclick='genro.dom.setClass(this.domNode,"zoommed","toggle")')
                            
                    if disp> .3:
                        app.div('dottor pierone')
                        app.div('ore 13:22')
                        app.div('paziente mario')
        