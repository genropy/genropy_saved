#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os, datetime

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    def main(self, root, **kwargs):
        root, top, bottom = self.pbl_rootContentPane(root)
        fb = root.formbuilder(cols=2)
        
        fb.button('tab 3', action='genro.dom.dispatchKey(9, genro.wdgById("input_3").focusNode)')
        fb.button('input 3', action="""var input = genro.wdgById("input_3").focusNode;
                                        input.focus();
                                        genro.dom.dispatchKey(9, genro.wdgById("input_3").focusNode);
        
                                        """)
        
        for x in range(10):
            fb.textbox(lbl='input %s' % x, value='^test.i_%s' % x, nodeId='input_%s' % x)
        
