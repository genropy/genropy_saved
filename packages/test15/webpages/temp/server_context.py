# -*- coding: UTF-8 -*-

"""Context tester"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_version = '11'
    dojo_theme = 'tundra'
    
    def test_1_context_creation(self, pane):
        """Context creation """
        center = self.common_pages_container(pane, height='350px', background='whitesmoke',
                                             datapath='test')
        fb = center.formbuilder(cols=1, border_spacing='3px', fld_width='8em', datapath='bar.mycontext')
        center.defineContext('context_foo', 'bar.mycontext', value=Bag(dict(egg='spam')), savesession=True)
        fb.textbox(value='^.egg', lbl='Context value')
        fb.textbox(value='^.egg?attribute_1', lbl='Context attr')