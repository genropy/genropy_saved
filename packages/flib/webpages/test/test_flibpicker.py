# -*- coding: UTF-8 -*-

# test_flibpicker.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"FlibPicker test"
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,item_picker:FlibPicker"

    #def test_0_flib_floatingpane(self,pane):
    #    pane.button('show',action='genro.wdgById("fp").show()')
    #    pane.button('hide',action='genro.wdgById("fp").hide()')
    #    pane.button('centerOn',action='genro.dom.centerOn("fp","mainWindow")')
    #
    #    fp = pane.floatingPane(title='Test',height='100px',width='200px',nodeId='fp', dockable=False,visible=False,
    #                        top='80px',left='20px',resizable=True,_class='shadow_4')

    def test_1_flibpicker(self, pane):
        self.flibPicker(pane, pickerId='test_picker', datapath='.picker', rootpath=None,
                        current_items=None, selected_items=None)
        pane.button('Open picker', action='PUBLISH test_picker_open')





        #def test_0_flib_picker_dialog(self,pane):
        #    "Mode dialog"
        #    pane.button('Show Picker',action='PUBLISH flib_picker_1_open;')
        #    pane.div('^.curr_items')
        #    self.flibPicker(pane,pickerId='flib_picker_1',datapath='.picker',rootpath=None,
        #                  current_items='=.#parent.curr_items',
        #                  selected_items='.#parent.checked_items')
        #
        #def test_1_flib_picker_pane(self,pane):
        #    bc = pane.borderContainer(height='300px')
        #    self.flibPicker(bc.contentPane(region='left',width='500px'),
        #                    pickerId='flib_picker_2',datapath='.picker',rootpath=None,
        #                    editMode='bc',
        #                    current_items='=.#parent.curr_items',
        #                    selected_items='.#parent.checked_items')
        #    bc.contentPane(region='center').div('altro')