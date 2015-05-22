# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""
from gnr.core.gnrbag import Bag
import xmlrpclib

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    css_requires='public'
    
    def windowTitle(self):
        return 'bageditor'
         
    def test_0_sum(self,pane):
        s = xmlrpclib.ServerProxy('http://localhost:8083/test15/soap/xmlrpc')
        print s.test("prova")
        