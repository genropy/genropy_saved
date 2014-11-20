# -*- coding: UTF-8 -*-

# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Inline edit cases"""


"Palettes"
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler" #gnrcomponents/palette_manager"
    auto_polling = 0
    user_polling = 0
    
    def windowTitle(self):
        return 'Inline edit strange'

        
    def test_0_testCheckbox(self, pane):
        bc = pane.borderContainer(height='400px')
        bc.contentPane(region='center').stackTableHandler(table='glbl.regione',viewResource='TestDyinCheckbox',
                                                            formResource='TestDyinCheckboxForm',
                                                            pbl_classes=True,condition_onStart=True)


    def test_1_testCheckbox_b(self, pane):
        bc = pane.borderContainer(height='400px')
        bc.contentPane(region='center').inlineTableHandler(table='glbl.regione',viewResource='TestEditInlineCheckbox',
                                                            pbl_classes=True,condition_onStart=True,saveButton=True)


    def test_2_testCheckbox_c(self, pane):
        bc = pane.borderContainer(height='400px')
        bc.contentPane(region='center').stackTableHandler(table='glbl.regione',viewResource='TestDyinCheckboxNuts',
                                                            condition_onStart=True,
                                                            formResource='TestDyinCheckboxTree')


    def test_3_testCheckbox_c(self, pane):
        bc = pane.borderContainer(height='400px')
        bc.contentPane(region='center').inlineTableHandler(table='glbl.regione',viewResource='TestDyinCheckboxNutsEdit',
                                                            pbl_classes=True,condition_onStart=True,saveButton=True)
