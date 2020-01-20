# -*- coding: utf-8 -*-

# drop_uploader.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test drop uploader"""
from __future__ import print_function

from builtins import object
from gnr.core.gnrlist import XlsReader
from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                   gnrcomponents/drop_uploader"""
    css_requires='public'

    def test_0_base(self, pane):
        pane.bagField(value='^.pippo',resource='mybf/test:Test0')