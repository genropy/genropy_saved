# -*- coding: UTF-8 -*-

# stack_tab.py
# Created by Francesco Porcari on 2010-12-19.
# Copyright (c) 2010 Softwell. All rights reserved.

"""stackContainer"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    auto_polling = 0
    user_polling = 0
    
    def windowTitle(self):
        return 'Stack e tab'
        
    def test_0_stackcontainer_pos(self, pane):
        """Stack number"""
        bc = pane.borderContainer(height='100px')
        top = bc.contentPane(region='top', height='30px', background='red').numberTextbox(value='^.selected')
        sc = bc.stackContainer(region='center', selected='^.selected', nodeId='s0')
        sc.contentPane(background='lime')
        sc.contentPane(background='pink')
        sc.contentPane(background='blue')
        
    def test_1_stackcontainer_named(self, pane):
        """Stack page"""
        bc = pane.borderContainer(height='100px')
        top = bc.contentPane(region='top', height='30px', background='red').filteringSelect(value='^.selectedPage',
                                                                                            values='lime:lime,pink:pink,blue:blue')
        sc = bc.stackContainer(region='center', selectedPage='^.selectedPage', nodeId='s1')
        sc.contentPane(background='lime', pageName='lime')
        sc.contentPane(background='pink', pageName='pink')
        sc.contentPane(background='blue', pageName='blue')
        
    def test_2_tabcontainer_pos(self, pane):
        """tab number"""
        bc = pane.borderContainer(height='100px')
        top = bc.contentPane(region='top', height='30px', background='red').numberTextbox(value='^.selected')
        tc = bc.tabContainer(region='center', selected='^.selected', nodeId='t0')
        tc.contentPane(background='lime', title='lime')
        tc.contentPane(background='pink', title='pink')
        tc.contentPane(background='blue', title='blue')
        
    def test_3_tabcontainer_named(self, pane):
        """tab page"""
        bc = pane.borderContainer(height='100px')
        top = bc.contentPane(region='top', height='30px', background='red').filteringSelect(value='^.selectedPage',
                                                                                            values='lime:lime,pink:pink,blue:blue')
        tc = bc.tabContainer(region='center', selectedPage='^.selectedPage', nodeId='t1')
        tc.contentPane(background='lime', pageName='lime', title='lime')
        tc.contentPane(background='pink', pageName='pink', title='pink')
        tc.contentPane(background='blue', pageName='blue', title='blue')
        
    def test_4_stackcontainer_mixed(self, pane):
        """Mixed page"""
        bc = pane.borderContainer(height='100px')
        top = bc.contentPane(region='top', height='30px', background='red')
        top.filteringSelect(value='^.selectedPage', values='lime:lime,pink:pink,blue:blue')
        top.numberTextBox(value='^.selected')
        sc = bc.stackContainer(region='center', selectedPage='^.selectedPage', selected='^.selected', nodeId='s1')
        sc.contentPane(background='lime', pageName='lime')
        sc.contentPane(background='pink', pageName='pink')
        sc.contentPane(background='blue', pageName='blue')
        
    def test_5_tabcontainer_mixed(self, pane):
        """Mixed number"""
        bc = pane.borderContainer(height='100px')
        top = bc.contentPane(region='top', height='30px', background='red').numberTextbox(value='^.selected')
        tc = bc.tabContainer(region='center', selected='^.selected', nodeId='t0')
        tc.contentPane(background='lime', title='lime')
        tc.contentPane(background='pink', title='pink')
        tc.contentPane(background='blue', title='blue')
