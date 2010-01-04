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

from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    js_requires='ckeditor/ckeditor'
    def main(self,root,**kwargs):
        root.data('editors.cked1.data','My first line<br/>My second line')
        root.data('editors.cked1.disabled',True)
        toolbar="""[
                   ['Source','-','Bold', 'Italic', '-', 'NumberedList', 'BulletedList', '-', 'Link', 'Unlink'],
                   ['Image','Table','HorizontalRule','PageBreak'],
                   '/',
                   ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                   ['Styles','Format','Font','FontSize'],
                   ['TextColor','BGColor'],['Maximize', 'ShowBlocks']
                   ]"""
        
        bc=root.borderContainer()
        top=bc.contentPane(height='50%',region='top',splitter=True)
        top.ckeditor(value='^editors.cked1.data',nodeId='cked1',config_toolbar='Basic',
        config_uiColor= '#9AB8F3',readOnly='^editors.cked1.disabled', toolbar=toolbar)
        
        center=bc.borderContainer(region='center')
        bottomleft=center.contentPane(region='left',width="200px",splitter=True)
        center.contentPane(region='center').div(innerHTML='^editors.cked1.data')
        bottomleft.checkbox(value='^editors.cked1.disabled')