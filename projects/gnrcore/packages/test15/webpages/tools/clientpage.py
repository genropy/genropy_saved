# -*- coding: UTF-8 -*-

"""ClientPage tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme = 'claro'
    
    def test_1_clientpage_page_setter(self, pane):
        """Set in external store"""
        center = self.common_pages_container(pane, height='350px', background='whitesmoke',
                                             datapath='test_1')
        self.common_form(center, common_rpc=False)
        center.dataRpc('dummy', 'setInClientPage', changepath='=.item_key',
                       value='=.item_value_w', pageId='=.info.pageId', _fired='^.set_item')
                       
    def test_2_clientpage_page_receiver(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px', datapath='test_2')
        for k in range(10):
            fb.textbox(value='^.value_%i' % k, lbl='value_%i' % k)
            