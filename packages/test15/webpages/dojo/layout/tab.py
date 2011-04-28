# -*- coding: UTF-8 -*-

# tab.py
# Created by Francesco Porcari on 2010-12-20.
# Copyright (c) 2010 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    css_requires = 'test'

    def windowTitle(self):
        return ''


    def test_2_tabcontainer(self, pane):
        """tab number"""
        bc = pane.borderContainer(height='200px')
        top = bc.contentPane(region='top', height='30px', background='red').numberTextbox(value='^.selected')
        tc = bc.tabContainer(region='center', selected='^.selected', nodeId='t0', _class='supertab')
        tc.contentPane(background='lime', title='lime').div('lime')
        tc.contentPane(background='pink', title='pink', closable=True).div('pink')
        pane = tc.contentPane(background='blue', title='blue')
        fb = pane.formbuilder(cols=1).simpleTextArea(value='^.blue', lbl='blue')
    
    def test_3_iframe(self, pane):
        tc = pane.tabContainer(height='400px')
        tc.contentPane(title='No iframe').div('hello')
        tc.contentPane(title='iframe genro',overflow='hidden').iframe(main='iframetest',height='100%',width='100%',border=0)
        tc.contentPane(title='iframe apple',overflow='hidden').iframe(src='http://www.apple.com',height='100%',width='100%',border=0)
        tc.contentPane(title='iframe html',overflow='hidden').iframe(src=self.getResourceUri('test.html'),height='100%',width='100%',border=0)
        
        
    def rpc_iframetest(self,pane,**kwargs):
        pane.div('hello again')
