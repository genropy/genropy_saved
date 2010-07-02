#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" GnrDojo Hello World """
import os

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        bc = root.borderContainer(regions='^regions')
        top = bc.contentPane(region='top',height='5em',background_color='#f2c922')
        left = bc.contentPane(region='left',width='100px',background_color='orange',splitter=True)
        center = bc.contentPane(region='center',background_color='silver', padding='10px')
        
        center.data('regions.left?show',False)
        center.data('regions.top',show=False)
        
        center.checkbox(value='^regions.top?show',label='Show top pane')
        center.br()
        
        center.checkbox(value='^regions.left?show',label='Show left pane')
        center.textbox(value='^regions.left', margin_left='5px')