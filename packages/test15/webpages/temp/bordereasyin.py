# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    css_requires='csstest'
    def windowTitle(self):
        return ''
         
    def main(self,pane,**kwargs):
        """First test description"""
        #pane.attributes['overflow'] = 'hidden'
        bc = pane.borderContainer()
        bc.contentPane(region='left',background='red',width='30px')
        bc.contentPane(region='top',background='lime').div(height='30px')
        bc.contentPane(region='center',background='white')