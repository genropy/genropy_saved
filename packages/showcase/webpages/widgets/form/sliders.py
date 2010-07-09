#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" GnrDojo Hello World """
import os

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb=root.formbuilder(cols=2)
        fb.horizontalslider(lbl='!!People', value = '^people', width='400px', 
                                         minimum=4, maximum=50,intermediateChanges=True)
        fb.numberTextBox(value = '^people',width='5em')