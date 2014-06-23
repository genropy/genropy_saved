# -*- coding: UTF-8 -*-

# test.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"Palettes"

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    testOnly='_3_'
    py_requires="gnrcomponents/testhandler:TestHandlerFull"#,gnrcomponents/palette_manager"
    css_requires='public'
    
    def windowTitle(self):
        return 'test'
        
    def test_0_default_dock(self,pane):
        """test 0"""
        pane.div(height='30px').dock(id='default_dock')
        
    def test_1_palette(self,pane):
        """palette"""
        pane.div(height='30px').dock(id='mydock_1')
        pg = pane.pGroup(groupCode='first',dockTo='mydock_1')
        pg.pPane(paletteCode='aa',title='aa',background_color='pink').div('aaa')
        pg.pPane(paletteCode='bb',title='bb',background_color='red').div('bb')
       #pg = pane.pGroup(groupCode='second',dockTo='mydock_1')
       #pg.pPane('uu',title='uuu',background_color='yellow').div('uuu')
       #pg.pPane('ee',title='eeee',background_color='cream').div('eeeee')
       #pane.pPane('xx',title='xx',background_color='orange').div('xx')
       #pane.pPane('zz',title='zz',background_color='lime',dockTo='mydock_1').div('zz')
        
    def test_2_treepalette(self,pane):
        pane.div(height='30px').dock(id='mydock_2')
        pg = pane.paletteGroup('second',dockTo='mydock_2')
        pg.paletteTree('mytree',title='State',data=self.treedata())
        pg.palettePane('blue',title='aa',background_color='blue').div('blu')
        
    def test_3_gridpalette(self,pane):
        pane.div(height='30px').dock(id='mydock_3')
        pg = pane.paletteGroup('third',dockTo='mydock_3')
        pg.paletteGrid('mygrid',title='States',data=self.treedata(),struct=self.gridstruct,filterOn='Caption:caption')
        #pg.palettePane('blue',title='aa',background_color='blue').div('blu')
        
    def treedata(self):
        result=Bag()
        result.setItem('r1',None,code='CA',caption='California')
        result.setItem('r1.a1',None,code='SD',caption='San Diego')
        result.setItem('r1.a2',None,code='SF',caption='San Francisco')
        result.setItem('r1.a3',None,code='SF',caption='Los Angeles')
        result.setItem('r2',None,code='IL',caption='Illinois')
        result.setItem('r4',None,code='TX',caption='Texas')
        result.setItem('r4.a1',None,code='HU',caption='Huston')
        result.setItem('r5',None,code='AL',caption='Alabama')
        return result
        
    def griddata(self):
        result=Bag()
        result.setItem('r1',None,code='CA',caption='California')
        result.setItem('r2',None,code='IL',caption='Illinois',disabled=True)
        result.setItem('r3',None,code='NY',caption='New York',checked='^.checked')
        result.setItem('r4',None,code='TX',caption='Texas',disabled='^.disabled')
        result.setItem('r5',None,code='AL',caption='Alabama')
        return result
        
    def gridstruct(self,struct):
        r = struct.view().rows()
        r.cell('code', name='Code', width='2em')
        r.cell('caption', name='Caption', width='15em')
        