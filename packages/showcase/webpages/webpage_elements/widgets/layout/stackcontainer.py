# -*- coding: UTF-8 -*-

# stackcontainer.py
# Created by Filippo Astolfi on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Stack container"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/layout/accordioncontainer.html
    
    def test_1_basic(self,pane):
        """Basic stack container"""
        bc = pane.borderContainer(height='300px')
        top = bc.contentPane(region='top',height='33px',background_color='#f2c922')
        top.button('page 1',action='SET stack_selected=0')
        top.button('page 2',action='SET stack_selected=1',disabled=False)
        top.button('page 3',action='SET stack_selected=2',disabled=False)
        sc = bc.stackContainer(region='center',selected='^stack_selected')
        sc.contentPane(???)
        sc.contentPane(???)
        sc.contentPane(???)