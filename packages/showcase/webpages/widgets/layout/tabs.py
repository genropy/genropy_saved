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
        tc = root.tabContainer(height='100%',nodeId='ppp',selected='^aux.selected')
        tc.contentPane(title='one').button('jj',action='genro.test()')
        tc.contentPane(title='two',url='border')
        tc.contentPane(title='three',iconClass='icnBaseAction',tip='Action').button('pp',tooltip='aaa')
        tc.contentPane(title='aaa',nodeId='panex')

            
                
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
