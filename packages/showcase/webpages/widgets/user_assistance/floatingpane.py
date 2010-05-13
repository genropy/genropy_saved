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

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return ''
         
    def main(self, root, **kwargs):
        toolbar = root.toolbar(height='30px')
        toolbar.dock(id='mydocker')
        self.floating_one(toolbar)
        self.floating_picker(toolbar)
        self.floating_picker(toolbar)
        
    def floating_one(self,pane):
        floating=pane.floatingPane(title='I am a floating', nodeId='ccc',top='100px',left='300px',
                        _class='shadow_4',width='200px',height='300px',
                      closable=True,
                      dockable=True,
                      resizable=True,     #Allow resizing of pane true if true
                      maxable=True ,      # Allow maximize 
                    
                      resizeAxis= 'xy',   #One of: x | xy | y to limit pane's sizing direction
                    
                      dockTo='mydocker',        # DomNode.if empty, will create private layout.Dock that scrolls
                                        # with viewport on bottom span of viewport.
                                        	
                      duration=400,      # Time is MS to spend toggling in/out node
                    
                      contentClass=''     # The className to give to the inner node which has the 
                                        # content def: "dojoxFloatingPaneContent"
                      )
                      
                      
        bc=floating.borderContainer()
        top=bc.contentPane(region='top',height='30px',splitter=True)
        top.div('dddd')
        center=bc.contentPane(region='center',background='^zz.color')
        center.div('pippo',margin='10px')
        
    def floating_picker(self,pane):
        colorpickerpane=pane.floatingPane(title='ColorPicker', top='300px',left='20px', dockTo='mydocker',
                        _class='shadow_4',dockable=True,resizable=True)
        colorpickerpane.colorPicker(value='^zz.color')
        
        
    def floating_palette(self,pane):
        colorpalettepane=pane.floatingPane(title='Color Palette', top='300px',left='20px', dockTo='mydocker',
                        _class='shadow_4',dockable=True)
        colorpalettepane.colorPalette(value='^zz.color')
        


        
        