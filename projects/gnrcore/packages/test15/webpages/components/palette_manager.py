# -*- coding: UTF-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""palette_manager"""

from gnr.core.gnrbag import Bag

"Palettes"
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull" #gnrcomponents/palette_manager"
    css_requires = 'public'
    auto_polling = 0
    user_polling = 0
    
    def windowTitle(self):
        return 'Palette manager'
        
    def test_0_default_dock(self, pane):
        pane.div(height='30px').dock(id='default_dock')
        
    def test_one(self, pane):
        bc = pane.borderContainer(height='300px')
        bc.contentPane(region='top',height='50px').contentPane(detachable=True,background='red')
        bc.contentPane(region='center')
        
    def test_1_palette(self, pane):
        pane.div(height='30px').dock(id='mydock_1')
        pane.palettePane('first', dockTo='mydock_1',maxable=True,background='red')
        #pg.palettePane('aa', title='aa', background_color='pink').div('aaa')
        #pg.palettePane('bb', title='bb', background_color='red').div('bb')
        #pg = pane.paletteGroup('second', dockTo='mydock_1')
        #pg.palettePane('uu', title='uuu', background_color='yellow').div('uuu')
        #pg.palettePane('ee', title='eeee', background_color='cream').div('eeeee')
        #pane.palettePane('xx', title='xx', background_color='orange').div('xx')
        #pane.palettePane('zz', title='zz', background_color='lime', dockTo='mydock_1').div('zz')
    
    def test_2_treepalette(self, pane):
        pane.div(height='30px').dock(id='mydock_2')
        pg = pane.paletteGroup('second', dockTo='mydock_2')
        pg.paletteTree('mytree', title='State', data=self.treedata())
        pg.palettePane('blue', title='aa', background_color='blue').div('blu')
    
    def test_3_gridpalette(self, pane):
        pane.div(height='30px').dock(id='mydock_3')
        pg = pane.paletteGroup('third', dockTo='mydock_3')
        pg.paletteGrid('mygrid', title='States', data=self.griddata(), struct=self.gridstruct
                       #filterOn='Caption:caption'
                       )
        #pg.palettePane('blue',title='aa',background_color='blue').div('blu')
    
    def treedata(self):
        result = Bag()
        result.setItem('r1', None, code='CA', caption='California')
        result.setItem('r1.a1', None, code='SD', caption='San Diego')
        result.setItem('r1.a2', None, code='SF', caption='San Francisco')
        result.setItem('r1.a3', None, code='SF', caption='Los Angeles')
        result.setItem('r2', None, code='IL', caption='Illinois')
        result.setItem('r4', None, code='TX', caption='Texas')
        result.setItem('r4.a1', None, code='HU', caption='Huston')
        result.setItem('r5', None, code='AL', caption='Alabama')
        return result
        
    def griddata(self):
        result = Bag()
        result.setItem('r1', None, code='CA', caption='California')
        result.setItem('r2', None, code='IL', caption='Illinois', disabled=True)
        result.setItem('r3', None, code='NY', caption='New York', checked='^.checked')
        result.setItem('r4', None, code='TX', caption='Texas', disabled='^.disabled')
        result.setItem('r5', None, code='AL', caption='Alabama')
        return result
        
    def gridstruct(self, struct):
        r = struct.view().rows()
        r.cell('code', name='Code', width='2em')
        r.cell('caption', name='Caption', width='15em')
        