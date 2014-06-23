# -*- coding: UTF-8 -*-

# framepane.py
# Created by Francesco Porcari on 2011-01-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"""framePane"""

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def windowTitle(self):
        return 'framePane'
         
    def test_0_slotbar_base(self,pane):
        """Design: headline"""
        frame = pane.framePane(frameCode='frame0',height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                               center_background='gray')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom = frame.bottom.slotBar(slots='btoh,*,|,bt2,30',height='30px')
        bottom.btoh.slotButton(label='Ok',action='alert("Hello!")')
        bottom.bt2.slotButton(label='ciao ciao',action='alert("Hello again!")')
        
    def test_1_slotbar_sidebar(self,pane):
        """Design: sidebar"""
        frame = pane.framePane(frameCode='frame1',height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',xmargin='10px',
                               center_background='gray',rounded=20,design='sidebar')
        #top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        #left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        right = frame.right.slotToolbar(slots='30,pp,*',width='100px',_class='icon48')
        right.pp.slotButton('aaa',iconClass='iconbox tray') 
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom.foo.slotButton('!!Save',iconClass="icnBaseOk",showLabel=False)
        
    def test_2_slotbar_headline(self,pane):
        """rounded"""
        frame = pane.framePane(frameCode='frame3',height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                               center_background='gray',rounded=10,rounded_bottom=0)
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')  
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        
    def test_3_slotbar_commands(self,pane):
        """subscribe"""
        frame = pane.framePane(frameCode='frame5',height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                               center_background='gray',rounded_top=10)
        top = frame.top.slotToolbar(slotbarCode='myslotbar',slots='*,foo,bar,xx,myaction,10',
                                    myaction_action='console.log(genro.getFrameNode("frame5"));',height='20px') 
        top.foo.slotButton(label='Add',iconClass='icnBaseAdd',publish='add')
        top.bar.slotButton(label='remove',iconClass='icnBaseDelete',publish='remove')
        frame.numberTextbox(value='^.value',default=1,width='5em',
                            subscribe_myslotbar_add="""SET .value=(GET .value)+1;""",   # It doesn't work!
                            subscribe_myslotbar_remove='SET .value= (GET .value) -1;')  # It doesn't work!
    @struct_method
    def mypage_slotbar_myaction(self,pane,_class=None,action=None,publish=None,**kwargs):
        pane.slotButton(label='action',iconClass='icnBaseAction',publish=publish,action=action,visible='^pippo')
        
    def test_4_slotbar_js(self,pane):
        """Javascript slotbar"""
        pane.button('Test',action="""var dlg = genro.dlg.quickDialog('Test');
                                     dlg.center._('div',{innerHTML:'Hi there!'});
                                     var slotbar = dlg.bottom._('slotBar',{slotbarCode:'chooser',slots:'*,discard,cancel,save'})
                                     slotbar._('slotButton','discard',{label:'Discard',publish:'discard'});
                                     slotbar._('slotButton','cancel',{label:'Cancel',publish:'cancel'});
                                     slotbar._('slotButton','save',{label:'Save',publish:'save'});
                                     dlg.show_action();""")


    def test_6_retinaIcons(self,pane):
        frame = pane.framePane(height='200px',width='800px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',design='sidebar')
        bar = frame.top.slotToolbar('5,first,prev,next,last,*')
        bar.first.slotButton(iconClass='rbox24 first')
        bar.prev.slotButton(iconClass='rbox24 prev')
        bar.next.slotButton(iconClass='rbox24 next')
        bar.last.slotButton(iconClass='rbox24 last')

    def test_5_regions(self,pane):
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



       #                          
    def test_10_framepanebug(self,pane):
        palette = pane.palettePane(paletteCode='xxx',height='600px',width='400px',dockTo=False)

    def test_11_framepanebug(self,pane):
        pane.dataController("""
        datapath ='aa'
        genro.src.getNode()._('div', 'kkk');
        var node = genro.src.getNode('kkk').clearValue();
        node.freeze();
        var pane = node._('palettePane',{paletteCode:'aaa',dockTo:false});
        var frame = pane._('framePane',{'frameCode':'bbb'});
        var topbar = frame._('slotBar',{'side':'top','slots':'*,aa',toolbar:true});
        topbar._('div','aa',{innerHTML:'aa'});
        frame._('div',{'height':'13px',background:'red'});
        node.unfreeze();

        """,_onStart=True)

    def test_12_framepanebug(self,pane):
        pane.dataController("""
        datapath ='aa'
        genro.src.getNode()._('div', '_advancedquery_');
        var node = genro.src.getNode('_advancedquery_').clearValue();
        node.freeze();
        var pane = node._('palettePane',{paletteCode:this.th_root+'_queryEditor',
                                        'title':'Query Tool',dockTo:false,
                                        datapath:datapath+'.query.where',height:'200px',width:'340px'});
        var frame = pane._('borderContainer');
        var topbar = frame._('ContentPane',{'region':'top',datapath:'.#parent',
                                })._('slotBar',{'slots':'queryname,*,savebtn,deletebtn',toolbar:true});
        topbar._('div','queryname',{innerHTML:'^.queryAttributes.description',font_size:'.8em',color:'#555',font_weight:'bold'})
        topbar._('slotButton','savebtn',{'label':_T('!!Save'),iconClass:'save16'});
        topbar._('slotButton','deletebtn',{'label':_T('!!Delete'),iconClass:'trash16'});
        frame._('ContentPane',{'region':'center',background:'lime'});
        node.unfreeze();

        """,_onStart=True)
        
        