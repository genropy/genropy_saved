#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'public:Public,public:StandardIndex'
    
    def windowTitle(self):
         return '!!Developer App'


    def main(self, root, **kwargs):
        center, top, bottom = self.pbl_rootBorderContainer(root, '',datapath='form')
        center.div('Developer Information', align='center', margin_top='20px')
