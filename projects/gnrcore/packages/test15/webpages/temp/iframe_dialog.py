# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """dbselect with auxcol"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.button('Show',action="""genro.dlg.iframeDialog('crediti',{height:'300px',width:'400px',title:'Test',
                                                            src:'iframe_dialog_content',
                                                            openKw:{topic:'dialog_open',pippo:new Date()},
                                                            selfsubscribe_duplica:function(kw){
                                                                console.log('test',kw)
                                                                this.dialog.hide();
                                                            }});""")

        #fb.dataController('console.log(bar,foo)',subscribe_crediti_duplica=True)
        fb.dataController('console.log(xxx);PUBLISH crediti_close;',subscribe_crediti_azzera=True)

