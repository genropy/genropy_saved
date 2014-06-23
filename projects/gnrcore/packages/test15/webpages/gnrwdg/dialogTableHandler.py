# -*- coding: UTF-8 -*-

# dialogTableHandler.py
# Copyright (c) 2011 Softwell. All rights reserved.

"dialogTableHandler"

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,public:TableHandlerMain"
    maintable='glbl.provincia'
    def windowTitle(self):
        return 'dialogTableHandler'
         
    def test_0_dlg(self,pane):
        "simple"
        pane = pane.framePane(frameCode='provFrame')
        iv = pane.dialogTableHandler(table='glbl.provincia',
                                     dialog_height='280px',
                                     dialog_width='340px',
                                     dialog_title=u'Provincia')