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
        bc=root.borderContainer(height='100%')
        top=bc.contentPane(height='150px',region='top')
        top.button('sss',action="console.log(genro.nodeById('myedit').editorData())")
        center=bc.contentPane(region='center')
        center.ckeditor(nodeId='myedit')