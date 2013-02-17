# -*- coding: UTF-8 -*-

# notgetter.py
# Created by Francesco Porcari on 2011-05-14.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    user_polling=0
    auto_polling=0
    def windowTitle(self):
        return ''
         
    def test_0_first(self,pane):
        """First test description"""
        frame = pane.framePane(height='400px',width='600px')
        frame.top.slotBar('*,stackButtons,*',stackButtons_stackNodeId='xx')

        bc = frame.center.borderContainer()
        bc.contentPane(region='right',width='100px',splitter=True,background='pink')
        bc.contentPane(region='bottom',height='100px',splitter=True,background='blue')
        bc.contentPane(region='top',height='10px',splitter=True,background='blue')
        bc.contentPane(region='left',width='10px',splitter=True,background='lime')

        sc = bc.stackContainer(border='1px solid silver',region='center',nodeId='xx')
        sc.contentPane(title='Pagina 1').div(position='absolute',top='10px',left='10px',
            height='100px',width='200px',background='red')
        p2 = sc.contentPane(title='Pagina 2',onCreated="""
                    var cb = function(){
                        widget.domNode.style.display="block";
                        widget.domNode.style.position="absolute";
                        widget.domNode.style.zIndex=1;
                        widget.getParent().layout();
                    }
                    setTimeout(function(){cb()});
                    dojo.connect(widget,'onHide',cb);""")
        p2.div(position='absolute',bottom='10px',left='10px',height='100px',width='200px',background='orange')

    def test_1_first(self,pane):
        box = pane.div(height='400px',width='600px',position='relative')
        l0 = box.div(position='absolute',top=0,bottom=0,left=0,right=0)
        l0.div(position='absolute',top='10px',left='10px',
            height='100px',width='200px',background='red')
        l1 = box.div(position='absolute',top=0,bottom=0,left=0,right=0,z_index=1)
        l1.div(position='absolute',top='30px',left='10px',height='100px',width='200px',background='orange')

