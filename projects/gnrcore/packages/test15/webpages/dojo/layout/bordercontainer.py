# -*- coding: UTF-8 -*-

# bordercontainer.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""bordercontainer"""
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase,th/th:TableHandler,gnrcomponents/dashboard_component/dashboard_component:DashboardItem"

    
    
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
        bc = pane.borderContainer(height='500px',margin='10px',border='1px solid silver',_class='tinySplitter')
       #bc.contentPane(region='bottom',height='60px',background='wheat',closable='close',splitter=True,border_top='1px solid silver')
       #bc.contentPane(region='top',height='60px',background='wheat',closable=True,splitter=True,border_top='1px solid silver')
       #bc.contentPane(region='left',width='100px',background='lightgray',closable=True,splitter=True,border_right='1px solid silver')
        #right = bc.contentPane(region='right',width='100px',background='lightgray',closable='close',splitter=True,
        #                border_left='1px solid silver',closable_background='red')
        left = bc.tabContainer(region='bottom',height='200px',closable='close',splitter=True,
                            closable_background='green',margin='2px',border_top='1px solid silver')
        left.contentPane(title='Pippo')
        left.contentPane(title='Paperino')

      #right.button('foo')
      #right.button('bar')

        bc.contentPane(region='center')

    def test_15_regions(self,pane):
        """Design: headline"""
        frame = pane.framePane(height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',design='sidebar')     
        sidebar = frame.right.slotBar(slots='*,mytree,*',width='60px',border_left='1px solid gray',closable='close',splitter=True)
        sidebar.mytree.div('aaa<br/>bbb')
        

    def test_16_regions(self,pane):
        """Design: headline"""
        frame = pane.framePane(height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',design='sidebar')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px',closable='close',closable_backround='blue')
        bottom = frame.bottom.slotBar(slots='btoh,*,|,bt2,30',height='30px',closable='close',border_top='1px solid gray')
        bottom.btoh.slotButton(label='Ok',action='alert("Hello!")')
        bottom.bt2.slotButton(label='ciao ciao',action='alert("Hello again!")')
        
        
        left = frame.left
        sidebar = left.slotBar(slots='*,mytree,*',border_right='1px solid gray',closable='close',
                    closable_background='darkblue',closable_transition='2s',splitter=True)
        sidebar.mytree.button('Pippo')        
        sidebar = frame.right.slotBar(slots='*,mytree,*',width='60px',border_left='1px solid gray',closable='close',splitter=True)
       
        sidebar.mytree.div('aaa<br/>bbb')
        frame.textbox(value='^.placeholder',placeholder='puzza',margin='20px')
        frame.textbox(value='^.aaa',placeholder='^.placeholder',margin='20px')
        frame.input(value='^.ccc',placeholder='^.aaa',margin='20px')



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


    def test_10_bordercontainer_filled(self,pane):
        bc = pane.borderContainer(height='400px',border='1px solid silver')
        bc.contentPane(region='top',background='red').div(height='^.pippo')
        bc.contentPane(region='center').textbox(value='^.pippo')



    def test_8_remoteLayout(self,pane):
        bc = pane.borderContainer(height='400px',width='800px')
        left = bc.contentPane(region='left',width='200px',background='lime')
        top = bc.contentPane(region='top')
        fb = top.formbuilder()
        fb.button('Build',fire='.build')
        bc.contentPane(region='center').remote(self.remoteLayout,_fired='^.build')
  
    @public_method
    def remoteLayout(self,pane,dobuild=None):
        if not dobuild:
            pane.div('ciao')
            return
        sc = pane.stackContainer()

        sc.contentPane(title='Ciao')
        sc.contentPane(title='Bao').plainTableHandler(table='adm.user')
        
        pane.dataController("sc.switchPage(1)",_onBuilt=100,sc=sc.js_widget)

    
    def test_99_region(self,pane):
        bc = pane.borderContainer(height='400px',width='700px')
        bc.contentPane(region='right',width='40',background='red',closable='close')
        bc.closablePane(region='right',width='40',background='red',closable='close')

        bc.contentPane(region='center',background='pink').div()