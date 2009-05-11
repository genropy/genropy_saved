#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrstring import templateReplace, splitAndStrip, countOf

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        #root = self.rootLayoutContainer(root)
        lc=root.layoutContainer(height='100%')
        top=lc.contentPane(layoutAlign='top',height='5em',background_color='silver').formbuilder(cols=4)
        top.textbox(lbl='Tabs',width='30em',value='^tabs')
        top.button('Create Tabs', action="genro.nodeById('tabContainer').updateContent({'tabs':'^tabs'})")
        
        client=lc.contentPane(layoutAlign='client')
        client.tabContainer(nodeId='tabContainer',height='100%',margin='1em').remote('tabContent', tabs='^tabs')
      
    def rpc_tabContent(self, tabs):
        pane = self.newSourceRoot()
        tabs=tabs.split(',')
        for t in tabs:
            p=pane.contentPane(title=t,height='100%')
            p.button(t)
        return pane
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()