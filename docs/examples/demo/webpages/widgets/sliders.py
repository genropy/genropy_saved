#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os


# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.data('aa',60)
        fb=root.formbuilder(cols=2)
        fb.horizontalSlider(lbl="People",width='400px')
        root.verticalSlider(height='140px',labels="['30','60','90']::JS",
                                discreteValues="3",value='^xx',default=60,
                                 minimum=30,maximum=90)
        root.div('^xx')

       
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
