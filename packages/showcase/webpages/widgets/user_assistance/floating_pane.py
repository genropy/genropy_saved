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
    def main(self, root, **kwargs):
        #   combobox - DEFAULT parameters:
        #       hasDownArrow=True --> create the selection arrow
        #       ignoreCase=True   --> user can write ignoring the case
        
        #   floatingPane - DEFAULT parameters:
        #       closable=True       --> if True, allow to close the floatingPane
        #       dockable=True       --> if True, allow to append the floatingPane to the dock
        #       duration=400        --> time in milliseconds to perform the action of "docking"
        #       resizable=False     --> if True, allow to resize floatingPane dimensions
        #       maxable=False       --> if True, allow to maximize floatingPane
        #       resizeAxis=None     --> one of: x | xy | y to limit pane's sizing direction
        #       dockTo=None         --> DomNode. If empty, will create private layout. Dock that
                                            # scrolls with viewport on bottom span of viewport.
        #       contentClass=''     --> The className to give to the inner node which
                                            # has the content def: "dojoxFloatingPaneContent"
        #       nodeId=None
        
        root.data('zz.color','#ffa500')
        toolbar = root.toolbar(height='30px')
        toolbar.dock(id='mydocker')
        
        cp = root.contentPane()
        self.floating_one(toolbar)
        self.floating_picker(toolbar)
        self.floating_palette(toolbar)
        fb = cp.formbuilder(cols=2)
        fb.radiobutton(value='^zz.radiopalette',group='radio',label='color palette')
        fb.radiobutton(value='^zz.radiopicker',group='radio',label='color picker')
        fb.dataController("""var color;
                             if(radiopalette){SET color = palettecolor};
                             if(radiopicker){SET color = pickercolor};
                             zz.color = color;""",
                             radiopalette='^zz.radiopalette',radiopicker='^zz.radiopicker',
                             palettecolor='^zz.palette.color',pickercolor='^zz.picker.color')
        
    def floating_one(self,pane):
        floating=pane.floatingPane(title='I\'m a floating one',_class='shadow_4',
                                   top='80px',left='20px',width='200px',height='470px',
                                   closable=True,resizable=True,resizeAxis='xy',maxable=True,
                                   dockable=True,dockTo='mydocker',duration=400)
        
        bc=floating.borderContainer()
        top=bc.contentPane(region='top',height='45px',splitter=True)
        top.div('Some text')
        center=bc.contentPane(region='center',background='^zz.color')
        center.div('Other text',margin='10px')
        
    def floating_palette(self,pane):
        colorpalettepane=pane.floatingPane(title='Color Palette',_class='shadow_4',
                                           top='80px',left='240px',dockTo='mydocker',dockable=True)
        colorpalettepane.colorPalette(value='^zz.palette.color')
        
    def floating_picker(self,pane):
        colorpickerpane=pane.floatingPane(title='ColorPicker',_class='shadow_4',
                                          top='280px',left='240px',width='500px',height='270px',
                                          dockable=True,dockTo='mydocker',resizable=True)
        colorpickerpane.colorPicker(value='^zz.picker.color')
