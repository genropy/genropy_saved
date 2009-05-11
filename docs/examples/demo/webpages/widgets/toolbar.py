#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Toolbar example """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        tb=root.toolbar()
        tb.button(iconClass="dijitEditorIcon dijitEditorIconCut" , showLabel="false",action='alert("cutting...")')
        tb.button(iconClass="dijitEditorIcon dijitEditorIconCopy" , showLabel="false",action='alert("copying...")')
        tb.button(iconClass="dijitEditorIcon dijitEditorIconPaste" , showLabel="false",action='alert("pasting...")')
        root.button('ggggg')
    


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
