# -*- coding: UTF-8 -*-
"""remote"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_remote(self, pane):
        """Basic remote"""
        bc = pane.borderContainer(height='300px')
        fb = bc.contentPane(region='top', height='30px').formbuilder(cols=2)
        fb.numberspinner(value='^.numtabs', lbl='Number of tabs', min=0, max=20)
        bc.data('.numtabs', 0)
        fb.div('Move focus out of the NumberSpinner to update tabs (max tab numbers set to 20)',
               font_size='.9em', text_align='justify', margin='10px')
        tc = bc.tabContainer(region='center')
        tc.remote('tabs', numtabs='^.numtabs')
        
    def remote_tabs(self, tc, numtabs):
        for i in range(numtabs):
            tab = tc.contentPane(title='Tab %d' % i, position='absolute', margin='60px')
            tab.div('This is tab n.%d' % i)