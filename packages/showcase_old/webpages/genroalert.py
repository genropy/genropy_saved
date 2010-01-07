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
        mydiv = root.div(nodeId='aaa',height='20ex',width='20em',border='1px solid black')
        root.button('Crea sul client',fire='build')
        root.dataController("page.buildOnClient()",_fired="^build")

            
                
            
