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
        bc = root.borderContainer(height='100%',regions='^regions')
        top = bc.contentPane(region='top',height='3ex',background_color='green')
        left = bc.contentPane(region='left',width='5em',background_color='orange',splitter=True)
        center= bc.contentPane(region='center',background_color='silver')
        center.textbox(value='^regions.left')
        center.checkbox('show',value='^regions.left?show')
            
                
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
