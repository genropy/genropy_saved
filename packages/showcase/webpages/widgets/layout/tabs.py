#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" GnrDojo Hello World """
import os

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        tc = root.tabContainer(selected='^selected.tab', margin='1em')
        tc.contentPane(title='First tab', tip='I appear during cursor passage on content pane')
        tc.contentPane(title='Second tab', iconClass='icnBaseAction').button('Dummy button (no action)',
                       tooltip='I appear during cursor passage on the button')