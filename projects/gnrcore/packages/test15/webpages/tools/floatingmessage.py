# -*- coding: UTF-8 -*-
# 
"""css3make tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme = 'tundra'
    def test_1_floating_message(self, pane):
        bc = pane.borderContainer(height='300px',width='700px',_class='pbl_roundedGroup',nodeId='pippo')
        pane.button('Test',action="""genro.dlg.floatingMessage(bc,{message:'Saving record',messageType:'error',duration:10})""",bc=bc)
