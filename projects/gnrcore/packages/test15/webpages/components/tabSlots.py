# -*- coding: UTF-8 -*-

# tabSlots.py
# Created by Francesco Porcari on 2011-10-20.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        frame = pane.framePane(height='300px')
        toolbar = frame.top.slotToolbar('*,tabButtons,deletetab,addtab,*')
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