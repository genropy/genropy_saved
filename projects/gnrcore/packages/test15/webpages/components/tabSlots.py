# -*- coding: UTF-8 -*-

# tabSlots.py
# Created by Francesco Porcari on 2011-10-20.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_testFrameStack(self,pane):
        """First test description"""
        frame = pane.framePane(height='300px')
        toolbar = frame.top.slotToolbar('*,stackButtons,deletetab,addtab,*')
        sc = frame.center.stackContainer(selectedPage='^.selectedPage')
        toolbar.deletetab.slotButton(iconClass='iconbox delete_record',action="""
                                            sc._value.popNode(sc.widget.getSelected().sourceNode.label);
                                        """,sc=sc)
        toolbar.addtab.slotButton(iconClass='iconbox add_record',
                                action="""var len = +sc._value.len();
                                          var pane = sc._("contentPane",{title:"Pippo " +len,pageName:"pippo_"+len});
                                          pane._('div',{innerHTML:"Pippo " +len});
                                        """,sc=sc)
        sc.contentPane(title='Orange',pageName='orange',background='orange')
        sc.contentPane(title='Green',pageName='green',background='green')
    
    def test_1_testInStack(self,pane):
        sc = pane.stackContainer(height='300px')
        frame_1 = sc.framePane(background='orange',pageName='orange',title='orange')
        frame_1.top.slotToolbar('titulo,*,parentStackButtons',titulo='pierozzo')
        frame_2 = sc.framePane(background='green',pageName='green',title='green')
        frame_2.bottom.slotToolbar('titulo,*,parentStackButtons,*',titulo='pancrazio')
        frame_2.div('bbb')



    def test_3_testFrameStack(self,pane):
        """First test description"""
        frame = pane.framePane(height='300px')
        bc = frame.center.borderContainer()
        top = bc.contentPane(region='top').div('Io sono il top dei top')
        sc = bc.stackContainer(selectedPage='^.selectedPage',region='center')
        toolbar = frame.top.slotToolbar('*,stackButtons,deletetab,addtab,*',stackButtons_stackNode=sc)

        toolbar.deletetab.slotButton(iconClass='iconbox delete_record',action="""
                                            sc._value.popNode(sc.widget.getSelected().sourceNode.label);
                                        """,sc=sc)
        toolbar.addtab.slotButton(iconClass='iconbox add_record',
                                action="""var len = +sc._value.len();
                                          var pane = sc._("contentPane",{title:"Pippo " +len,pageName:"pippo_"+len});
                                          pane._('div',{innerHTML:"Pippo " +len});
                                        """,sc=sc)
        sc.contentPane(title='Orange',pageName='orange',background='orange')
        sc.contentPane(title='Green',pageName='green',background='green')