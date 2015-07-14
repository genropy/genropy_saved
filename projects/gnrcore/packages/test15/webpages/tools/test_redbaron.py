# -*- coding: UTF-8 -*-

# messages.py
# Created by Francesco Porcari on 2010-08-26.
# Copyright (c) 2010 Softwell. All rights reserved.

"""RedBaron"""

from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'RedBaron'
        
    def test_1_redbaron(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.module',lbl='Module')
        fb.dataRpc('.result',self.redBaronIndex,httpMethod='WSK',module='^.module')
        fb.div('^.result')

    @public_method
    def redBaronIndex(self,module=None):
        print 'module',module
        status = getattr(self,'_mystatus',None) or []
        status.append(module)
        self._mystatus = status
        return '<br/>'.join(status)
