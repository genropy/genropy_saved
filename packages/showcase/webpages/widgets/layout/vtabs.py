#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" GnrDojo Hello World """
import os

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        tc = root.tabContainer(margin='1em',tabPosition='left-h')
        tc.contentPane(title='One')
        tc.contentPane(title='Two')