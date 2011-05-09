#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

""" Google Chart """

from gnr.core.gnrbag import Bag
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def main(self, root, **kwargs):
        root.css('.roundedright', self.cssmake(rounded='right:12',
                                               shadow='2,2,6,red',
                                               style='margin:10px;'))
        root.css('.roundedall', self.cssmake(rounded='all:12', shadow='2,2,6,red', style='margin:10px;'))

        bc, top, bottom = self.pbl_rootBorderContainer(root)
        left = self.left_pane(bc.contentPane(region='left', width='25%',
                                             _class='roundedright', background_color='silver'))
        self.center_pane(bc.borderContainer(region='center'))

    def left_pane(self, pane):
        pane.div('hhh')

    def center_pane(self, bc):
        bc = bc.borderContainer(region='center', _class='roundedall', background_color='silver')
        tc = bc.tabContainer(region='center', margin='20px')
        self.page_0(tc.contentPane(title='Page 0', nodeId='tab0', _class='roundedall', background_color='whitesmoke'))

    def page_0(self, pane):
        pane.div('jjj', margin='20px')