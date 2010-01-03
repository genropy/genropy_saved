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

from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    js_requires='ckeditor/ckeditor'
    def main(self,root,**kwargs):
        root.data('editors.cked1.data','My first line<br/>My second line')
        bc=root.borderContainer()
        top=bc.contentPane(height='50%',region='top',splitter=True)
        top.ckeditor(value='^editors.cked1.data',nodeId='cked1')
        center=bc.contentPane(region='center')
        center.div(innerHTML='^editors.cked1.data')