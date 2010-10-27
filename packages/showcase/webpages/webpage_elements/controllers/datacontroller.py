# -*- coding: UTF-8 -*-

# dataController.py
# Created by Filippo Astolfi on 2010-10-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataController"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """dataController"""
        bc = pane.borderContainer(height='300px')
        top = bc.contentPane(region='top',height='100px')
        top.button('Build',fire='build')

        top.button('Add element',fire='add')
        top.dataController("""var pane = genro.nodeById('remoteContent')
                              pane._('div',{height:'200px',width:'200px',background:'lightBlue',
                                            border:'1px solid blue','float':'left',
                                            remote:{'method':'test'}});

                            """,_fired="^add")
                            
        center = bc.contentPane(region = 'center').div(nodeId='remoteContent')
        center.div().remote('test',_fired='^build')
        
    def remote_test(self,pane,**kwargs):
        print 'pippo'
        pane.div('hello',height='40px',width='80px',background='lime')