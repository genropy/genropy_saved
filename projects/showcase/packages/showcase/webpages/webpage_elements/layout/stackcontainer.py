# -*- coding: UTF-8 -*-

# stackcontainer.py
# Created by Filippo Astolfi on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Stack container"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_0_stackcontainer_named(self, pane):
        """Stack page"""
        bc = pane.borderContainer(height='100px')
        top = bc.contentPane(region='top', height='18px', rounded=5, background='#2B65AC').filteringSelect(value='^.selectedPage',
                                                                                            values='lb:light blue,le:light yellow,blue:blue',
                                                                                            rounded=5)
        sc = bc.stackContainer(region='center', selectedPage='^.selectedPage')
        sc1 = sc.contentPane(background='#7CBEF8', pageName='lb', rounded=5)
        sc1.div('Hello!', color='white')
        sc2 = sc.contentPane(background='#EFE237', pageName='le', rounded=5)
        sc3 = sc.contentPane(background='blue', pageName='blue', rounded=5)