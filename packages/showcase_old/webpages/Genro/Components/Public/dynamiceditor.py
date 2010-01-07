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
        bc = root.borderContainer()
        extra='createLink,insertImage'
        top = bc.contentPane(region='top',height='3ex',background_color='green',splitter=True)
        left = bc.contentPane(region='left',width='5em',background_color='orange',splitter=True)
        top = bc.contentPane(region='bottom',height='3ex',background_color='red',splitter=True)
        self.dynamicEditor(bc, contentPars = dict(region='center'),
                          value='^description',disabled=False,
                          extraPlugins=extra)
        
    
        
            
                
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
