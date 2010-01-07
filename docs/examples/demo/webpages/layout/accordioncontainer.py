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


class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        
        lc=root.accordionContainer(height='100%',margin='4px',border='1px solid black',selected='^selpage')
        lc.accordionPane(title="One").button('One')
        lc.accordionPane(title="Two").button('Two')
        lc.accordionPane(title="Three").button('Three')
        lc.accordionPane(title="Four").button('Four')

               
