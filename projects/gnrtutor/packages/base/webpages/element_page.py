# -*- coding: UTF-8 -*-

# element_page.py
# Created by Francesco Porcari on 2012-04-24.
# Copyright (c) 2012 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='public:Public,th/th_tree:TableHandlerTree'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
        return ''
         
    def main(self, root, **kwargs):
        frame = root.rootContentPane(datapath='main',design='sidebar')    
        frame.borderTableHandlerTree(table='base.element')