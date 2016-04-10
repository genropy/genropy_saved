# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    css_requires='public'
    def test_1_gridgallery(self,pane):
        bc = pane.borderContainer(height='800px',width='700px')
        bc.contentPane(region='top').filteringSelect(value='^.current_store',values='gg_store_1,gg_store_2')

        top = bc.borderContainer(region='center')
        g1 = top.contentPane(region='left',width='50%').quickGrid(value='^gg_store_1')
        g1.column('label',edit=True,name='Label')
        g1.column('content',edit=True,name='Content')
        g1.tools('addrow,delrow')


        g1 = top.contentPane(region='center').quickGrid(value='^gg_store_2')
        g1.column('label',edit=True,name='Label')
        g1.column('content',edit=True,name='Content')
        g1.tools('addrow,delrow')



        bc.gridGallery(region='bottom',items='^.current_store',height='500px')