# -*- coding: utf-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"
    css_requires='public'
    def test_1_gridscale(self,pane):
        bc = pane.borderContainer(height='600px',width='800px')
        th = bc.plainTableHandler(table='glbl.provincia',view_store__onStart=True,
                            grid_scaleX='^.scaleX',
                            grid_scaleY='^.scaleY',
                            region='center')
        fb = th.view.bottom.slotToolbar('10,fbscale,*').fbscale.formbuilder(cols=2)
        fb.horizontalSlider(value='^.grid.scaleX',lbl='Scale X',minimum=0.3, maximum=1,
                            intermediateChanges=True,width='10em')
        fb.horizontalSlider(value='^.grid.scaleY',lbl='Scale Y',minimum=0.3, maximum=1,
                            intermediateChanges=True,width='10em')