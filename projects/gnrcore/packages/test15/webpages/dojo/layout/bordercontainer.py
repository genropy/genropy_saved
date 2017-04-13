# -*- coding: UTF-8 -*-

# bordercontainer.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""bordercontainer"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"

    
    
    def windowTitle(self):
        return 'borderContainer'
        
    def test_bordercontainer_inside_cb(self, pane):
        bc = pane.contentPane(height='200px',background='green').borderContainer(background='red')
        
    def test_bordercontainer_cb_splitter(self, pane):
        bc = pane.borderContainer(height='200px')
        bc.contentPane(region='left',width='500px',splitter=True,background='lime').contentPane().remote('xxx',_fired='^aaa')
        bc.contentPane(region='center')
        
    def remote_xxx(self,pane,**kwargs):
        fb = pane.formbuilder(cols=2, border_spacing='3px')
        fb.textbox(lbl='aaa')
        fb.textbox(lbl='bbb')
        
    def test_bordercontainer_inside_cb_2(self, pane):
        bc = pane.tabContainer(height='200px',background='green')
        bc.contentPane(background='red',title='aa').borderContainer(background='pink')
        
    def _test_bordercontainer_mixedlayout(self, pane):
        bc = pane.borderContainer(height='300px')
        bc.contentPane(region='top', height='20px', background='red', splitter=True)
        tc = bc.tabContainer(region='left', width='400px')
        tc.contentPane(title='aa')
        tc.contentPane(title='bb')
        ac = bc.accordionContainer(region='right', width='400px')
        bc2 = ac.borderContainer(title='aa', background='black')
        bc2.contentPane(region='bottom', height='30px', background='silver')
        bc2.contentPane(region='center', background='lime')
        ac.contentPane(title='bb')
        bc.contentPane(region='center', background='yellow')

    def test_5_opener(self,pane):
        bc = pane.borderContainer(height='500px',margin='10px',border='1px solid silver',nodeId='xxxx')
        bc.contentPane(region='bottom',height='60px',background='wheat',drawer='close',splitter=True,border_top='1px solid silver')
        bc.contentPane(region='top',height='60px',background='wheat',drawer=True,splitter=True,border_top='1px solid silver')
        bc.contentPane(region='left',width='100px',background='lightgray',drawer=True,splitter=True,border_right='1px solid silver')
        bc.contentPane(region='right',width='100px',background='lightgray',drawer='close',splitter=True,
                        border_left='1px solid silver',drawer_background='red')
        bc.contentPane(region='center')

    def test_6_regions(self,pane):
        bc = pane.borderContainer(height='600px')
        fb = bc.contentPane(region='top',height='50px').formbuilder(cols=4,border_spacing='3px',datapath='.regions')
        fb.textBox(value='^.top',lbl='top')
        fb.textBox(value='^.left',lbl='left')
        fb.textBox(value='^.bottom',lbl='bottom')
        fb.textBox(value='^.right',lbl='right')

        bc = bc.borderContainer(regions='^.regions',region='center')
        bc.contentPane(region='top',background='red',splitter=True)
        bc.contentPane(region='bottom',background='green',splitter=True)
        bc.contentPane(region='left',background='blue',splitter=True)
        bc.contentPane(region='right',background='green',splitter=True)
        bc.contentPane(region='center',background='white')

    def test_7_splitter_margins(self,pane):
        frame = pane.framePane(height='600px',design='sidebar')
        left = frame.left
        left.attributes.update(splitter=True)
        bar = frame.left.slotBar('pippo,pluto,0',width='200px',border_right='1px solid silver')
        bar.pippo.div('slot 1')
        bar.pluto.div('slot 2')

        frame.div('Pippo',font_size='30px')



