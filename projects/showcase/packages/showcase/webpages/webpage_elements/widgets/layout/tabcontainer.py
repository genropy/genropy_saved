# -*- coding: UTF-8 -*-
"""tabContainer"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic tabs"""
        tc = pane.tabContainer(height='200px', selected='^.selected.tab')
        cp = tc.contentPane(title='first tab')
        cp.div("""A tabContainer with two contentPanes. The "title" attribute appears on tabs.
                  You find the tab selected in the datastore at the path specified in the
                  selected attribute (in this example, test/test_1_basic/selected/tab)""",
                  text_align='justify', margin='10px')
        tc.contentPane(title='Second tab').div('I\'m the second tab', font_size='.9em',
                                               text_align='justify', margin='10px')
                                               
    def test_2_tabPosition(self, pane):
        """tabPosition attribute"""
        bc = pane.borderContainer(height='460px')
        tc = bc.tabContainer(height='100px', margin='1em', tabPosition='top-h')
        tc.contentPane(title='One').div("""tabPosition=\'top-h\' (this is the default
                                           value for the tabPosition.)""", margin='1em')
        tc.contentPane(title='Two')
        tc = bc.tabContainer(height='100px', margin='1em', tabPosition='left-h')
        tc.contentPane(title='One').div('tabPosition=\'left-h\'', margin='1em')
        tc.contentPane(title='Two')
        tc = bc.tabContainer(height='100px', margin='1em', tabPosition='right-h')
        tc.contentPane(title='One').div('tabPosition=\'right-h\'', margin='1em')
        tc.contentPane(title='Two')
        tc = bc.tabContainer(height='100px', tabPosition='bottom')
        tc.contentPane(title='One').div('tabPosition=\'bottom\'', margin='1em')
        tc.contentPane(title='Two')
        
    def test_3_remote(self, pane):
        """remote tabContainer"""
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