# -*- coding: UTF-8 -*-

# thlight.py
# Created by Francesco Porcari on 2011-03-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,tablehandler/th_components:TableHandlerBase"
         
    def test_0_localita(self,pane):
        """First test description"""
        sc = pane.stackTableHandler(height='400px',table='glbl.localita',virtualStore=True)
        sc.form.store.handler('load',default_provincia='MI')
    
    def test_1_provincia(self,pane):
        """First test description"""
        sc = pane.stackTableHandler(height='400px',table='glbl.provincia',virtualStore=True)
        sc.form.store.handler('load',default_regione='LOM')
            
    def test_2_provincia_dialog(self,pane):
        """First test description"""
        pane = pane.borderContainer(height='400px')
        th = pane.dialogTableHandler(region='center',dialog_height='300px',dialog_width='500px',dialog_title='provincia',
                                    table='glbl.provincia',virtualStore=True)
        th.form.store.handler('load',default_regione='LOM')
        
    def test_3_provincia_palette(self,pane):
        """First test description"""
        pane = pane.borderContainer(height='400px')
        th = pane.paletteTableHandler(region='center',palette_height='300px',palette_width='500px',dialog_title='provincia',
                                    table='glbl.provincia',virtualStore=True)
        th.form.store.handler('load',default_regione='LOM')
    
    def test_4_provincia_view(self,pane):
        """First test description"""
        viewer = pane.tableViewer(frameCode='provinciali',height='400px',table='glbl.provincia',virtualStore=True)
        viewer.top.attributes['detachable'] = True
        viewer.bottom.slotBar('*,label,count',label='Totali:')