# -*- coding: utf-8 -*-

# dataremote.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

import datetime
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_conn(self, pane):
        """Connection"""
        pane.iframe(src='/sys/thpage/adm/connection',height='500px',width='900px',border='1px solid silver',id='pippo')
        
    def test_2_sp(self, pane):
        """Served page"""
        pane.iframe(src='/sys/thpage/adm/served_page',height='500px',width='900px',border='1px solid silver')
