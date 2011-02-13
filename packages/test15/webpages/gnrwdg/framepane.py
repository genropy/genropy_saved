# -*- coding: UTF-8 -*-

# slotbar.py
# Created by Francesco Porcari on 2011-01-30.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method
"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return 'SlotBar test'
         
    def _test_0_slotbar_base(self,pane):
        """Design headline"""
        frame = pane.framePane(frameCode='frame1',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom = frame.bottom.slotBar(slots='btoh,*,|,bt2,30',height='30px')
        bottom.btoh.slotButton(label='Ok')
        bottom.bt2.slotButton(label='ciao ciao')


    
    def _test_1_slotbar_sidebar(self,pane):
        """Design sidebar"""
        frame = pane.framePane(frameCode='frame2',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',
                                center_background='gray',rounded=20,design='sidebar')
        #top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        #left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px') 
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom.foo.button('!!Save',iconClass="icnBaseOk",showLabel=False)
        
    def _test_1_slotbar_headline(self,pane):
        """Design headline"""
        frame = pane.framePane(frameCode='frame2',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',rounded=20)
        #top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        #left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px') 
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
       
        
    
    def _test_2_slotbar_headline(self,pane):
        """Change gradients"""
        frame = pane.framePane(frameCode='frame3',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',rounded=10,rounded_bottom=0)
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')  
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px')
           
    def _test_2_slotbar_sidebar(self,pane):
        """Change gradients"""
        frame = pane.framePane(frameCode='frame3',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',design='sidebar')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')  
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        
    def test_3_slotbar_commands(self,pane):
        """Change gradients"""
        frame = pane.framePane(frameCode='frame4',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',rounded_top=10)
        top = frame.top.slotToolbar(slotbarCode='myslotbar',slots='*,foo,bar,xx,myaction,10',
                                    myaction_action='console.log(genro.getFrameNode("frame4"));',height='20px') 
        top.foo.slotButton(label='Add',iconClass='icnBaseAdd',publish='add')
        top.bar.slotButton(label='remove',iconClass='icnBaseDelete',publish='remove')
        frame.numberTextbox(value='^.value',default_value=1,width='5em',
                            subscribe_myslotbar_add="""SET .value=(GET .value)+1;""",
                            subscribe_myslotbar_remove='SET .value= (GET .value) -1;')
    @struct_method
    def mypage_slotbar_myaction(self,pane,_class=None,action=None,publish=None,**kwargs):
        pane.slotButton(label='action',iconClass='icnBaseAction',publish=publish,action=action,visible='^pippo')
    
    def test_4_slotbar_js(self,pane):
        pane.button('Test',
                    action="""
                    var dlg = genro.dlg.quickDialog('Test');
                    dlg.center._('div',{innerHTML:'Bella li'});
                    var slotbar = dlg.bottom._('slotBar',{slotbarCode:'chooser',slots:'discard,*,cancel,save'})
                    slotbar._('slotButton','discard',{label:'Discard',publish:'discard'});
                    slotbar._('slotButton','cancel',{label:'Cancel',publish:'cancel'});
                    slotbar._('slotButton','save',{label:'Discard',publish:'save'});
                    dlg.show_action();
                    """)

        

