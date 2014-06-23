# -*- coding: UTF-8 -*-
# 
"""ServerStore tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme = 'claro'

    def test_1_current_page(self, pane):
        """On current page """
        self.common_form(pane, datapath='test_1')

    def test_2_external_page(self, pane):
        """Set in external store"""
        center = self.common_pages_container(pane, height='350px', background='whitesmoke',
                                             datapath='test_2')
        self.common_form(center)

    def test_3_server_data(self, pane):
        """Server shared data """
        center = self.common_pages_container(pane, height='350px', background='whitesmoke',
                                             datapath='test_3')
        center.data('.foo.bar', _serverpath='xx')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.foo.bar', lbl='Server store value')
        fb.textbox(value='^.foo.baz', lbl='Value not in server subscribed path')
        fb.button('Ping', action='genro.ping()')

