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
        lc=root.LayoutContainer(height='100%')
        left=lc.contentPane(layoutAlign='left',background_color='blue',width='100px')
        top=lc.contentPane(layoutAlign='top',background_color='red',height='20px')
        bottom=lc.contentPane(layoutAlign='bottom',background_color='gray',height='20px')
        right=lc.contentPane(layoutAlign='right',background_color='pink',width='100px')
        client=lc.contentPane(layoutAlign='client',background_color='yellow')
        client.button('Do This !', tooltip='Hey you can do this...', action='alert("Doing this now...")')
        client.button('Do That', tooltip='Hey you can do also that...', action='alert("Doing that too...")')

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
