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
        lc=root.LayoutContainer(background_color='green',height='100%')
        left=lc.contentPane(layoutAlign='left',background_color='blue',width='4em',margin='2px')
        top=lc.contentPane(layoutAlign='top',background_color='red',height='2em',margin='2px')
        bottom=lc.contentPane(layoutAlign='bottom',background_color='gray',height='1em',margin='2px')
        right=lc.contentPane(layoutAlign='right',background_color='pink',width='6em',margin='2px')
        client=lc.contentPane(layoutAlign='client',background_color='yellow')
        client.button('genuflesso',tooltip='aiuto a genuflettersi')
        client.button('pignattino')
