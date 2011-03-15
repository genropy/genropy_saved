# -*- coding: UTF-8 -*-

# thframe.py
# Created by Francesco Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

"Tablehandler"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,tablehandler/th_iframepage:TableHandler"
         
    def test_0_firsttest(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='600px')
        gridpane = bc.contentPane(region='top',height='50%')
        formpane = bc.contentPane(region='center')
        formpane.dataController("",dbevent="^gnr.dbevent.glbl_localita.id")
        gridpane.iframeTableHandler(table='glbl.localita',inputPane=formpane) 
