# -*- coding: UTF-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.
    


"Palettes"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/palette_manager"

    def windowTitle(self):
        return 'Palette manager'
         
    def test_0_common(self,pane):
        pane.div(height='30px').dock(id='mydock')
        
         

    def test_1_palette(self,pane):
        pg = pane.paletteGroup('second',dockTo='mydock')
        pg.palettePane('aa',title='aa',background_color='pink').div('aaa')
        pg.palettePane('bb',title='bb',background_color='red').div('bb')
    
    def test_2_palette_nogroup(self,pane):
        pane.palettePane('cc',title='cc',background_color='orange',dockTo='mydock').div('cc')

       #pg.paletteTree(title='bb').div('bb')
       #pg.paletteGrid(title='bb').div('bb')

       #self.paletteTree(pg,title='bb')
       #self.paletteGrid(pg,title='bb')
 #    
 # 
 # def _test_2_palette(self,pane):
 #     palette = self.paletteGrid('second',dockTo='mydock')
 #     self.palette.paletteTree(palette,title='aa',background_color='pink').div('aaa')
 #     self.palettePane(palette,title='bb').div('bb')
 # 

