# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        pane.dataRpc('dummy',self.testDebug,_onResult="""alert(pippo)
                                                       """,_onStart=2000)

    @public_method
    def testDebug(self):
        return Bag(dict(pipo='pipo'))
        