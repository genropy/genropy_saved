#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return '!! touch test'

    def main(self, root, **kwargs):
        #root.tree(storepath='gnr',margin_top='30px',margin_left='30px')
        fb=root.div(font_size='20px').formbuilder(cols=1,margin_top='30px',margin_left='30px')
        fb.div('^gnr.touch.orientation',lbl='Orientation')
        fb.div('^gnr.touch.gesture.scale',lbl='Gesture Scale')
        fb.div('^gnr.touch.gesture.rotation',lbl='Gesture rotation')