#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        return ''

    def windowTitle(self):
        return '!! touch test'

    def main(self, root, **kwargs):
        #root.tree(storepath='gnr',margin_top='30px',margin_left='30px')
        bc = root.borderContainer(font_size='20px')
        left = bc.contentPane(region='left', splitter=True, width='30%')
        #left.tree(storepath='touch.event')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=1, margin_top='30px', margin_left='30px')
        fb.div('^touch.orientation', lbl='Orientation')
        #fb.div('^touch.event.gesture.scale',lbl='Gesture Scale')
        # fb.div('^touch.event.gesture.rotation',lbl='Gesture rotation')
        fb.div('^touch.event.gesture', lbl='Gesture event')

