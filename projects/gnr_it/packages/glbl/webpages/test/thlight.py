# -*- coding: UTF-8 -*-

# thlight.py
# Created by Francesco Porcari on 2011-03-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"
         
    def test_0_localita(self,pane):
        """First test description"""
        sc = pane.stackTableHandler(height='400px',table='glbl.localita',virtualStore=True)
        sc.form.store.handler('load',default_provincia='MI')
    
    def test_1_provincia(self,pane):
        """First test description"""
        sc = pane.stackTableHandler(height='400px',table='glbl.provincia',formInIframe=False,virtualStore=True)
        sc.view.store.attributes.update(_onStart=True)
        sc.form.store.handler('load',default_regione='LOM')
    
    def test_11_provincia(self,pane):
        """First test description"""
        sc = pane.stackTableHandler(height='400px',table='glbl.provincia',formInIframe=True)
        sc.view.store.attributes.update(_onStart=True)
       # sc.form.store.handler('load',default_regione='LOM')
            
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
    
    def test_4_provincia_border(self,pane):
        """First test description"""
        th = pane.borderTableHandler(height='400px',table='glbl.provincia',virtualStore=True)
        th.form.store.handler('load',default_regione='LOM')
    
    def test_5_provincia_view(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='400px')
        th = bc.plainTableHandler(region='center',table='glbl.provincia',virtualStore=True,grid_canSort='function(k){console.log(this,k);}')
        th.view.top.attributes['detachable'] = True
        th.view.bottom.slotBar('*,label,count',label='Totali:')

    def test_6_provincia_iframeDialog(self,pane):
        """First test description"""
        pane = pane.borderContainer(height='400px')
        pane.dialogTableHandler(region='center',dialog_height='300px',dialog_width='500px',dialog_title='provincia',
                                table='glbl.provincia',virtualStore=True,formInIframe=True)
        
    def test_7_complexLayout(self,pane):
        bc = pane.borderContainer(height='400px')

        th = bc.dialogTableHandler(region='center',table='glbl.regione',formResource=':FormBug',dialog_height='500px',dialog_width='800px')
        th.view.store.attributes.update(_onStart=True)
    