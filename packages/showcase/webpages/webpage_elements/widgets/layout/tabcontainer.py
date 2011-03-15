#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

"""Tab container"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic tabs - horizontal tabs"""
        tc = pane.tabContainer(height='200px', selected='^selected.tab')
        cp = tc.contentPane(title='first tab')
        cp.div("""In this example we show to you a standard tabContainer with some children
                  (contentPanes). The "title" attribute will appear on tab.
                  With the ``selected`` attribute Genro create a folder path (in this case ``/selected/tab``) in the
                  datastore where lies a number indicating the tab selected (for the first tab you'll find 0,
                  for the second one you'll find 1).""",
                  font_size='.9em', text_align='justify', margin='10px')
        tc.contentPane(title='Second tab').div('I\'m the second tab', font_size='.9em',
                                               text_align='justify', margin='10px')

    def test_2_tabPosition(self, pane):
        """Basic tabs - tabPosition attribute"""
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
        """Remote tabContainer"""
        bc = pane.borderContainer(height='300px')
        fb = bc.contentPane(region='top', height='3em').formbuilder(cols=2, border_spacing='4px')
        fb.numberspinner(value='^numtabs', lbl='Number of tabs')
        bc.data('numtabs', 0)
        fb.div('Move focus out of the textbox to update tabs.',
               font_size='.9em', text_align='justify', margin='10px')
        tc = bc.tabContainer(region='center')
        tc.remote('tabs', numtabs='^numtabs')

    def remote_tabs(self, tc, numtabs):
        for i in xrange(numtabs):
            tab = tc.contentPane(title='Tab #%d' % i, margin='40px')
            tab.div('This is tab #%d' % i)