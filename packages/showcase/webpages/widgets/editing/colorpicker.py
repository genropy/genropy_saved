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
    def main(self,root,**kwargs):
        center=root.borderContainer(region='center')
        bottomleft=center.contentPane(region='left',width="300px",splitter=True)
        bottomleft.ColorPicker(value='^aux.color',showHsv=False,showRgb=False,webSafe=False,showHex=False)
        center.contentPane(region='center', background_color='^aux.color').div(innerHTML='^editors.cked1.data')
        bottomleft.checkbox(value='^editors.cked1.disabled')