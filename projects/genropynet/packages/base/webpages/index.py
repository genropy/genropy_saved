#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='public:Public'
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return '!!Genropynet'

    def main(self, root, **kwargs):
        center, top, bottom = self.pbl_rootBorderContainer(root,
                                                           title='gggggggggg')

        tb=center.contentPane(region='top',height='30px',border_bottom='1px solid gray').toolbar()
        center.contentPane(region='center').div('xxx')
        menu=tb.dropdownbutton(label='Browse')
        menu.menu(_class='browsemenu',action="function(attributes){genro.gotoURL(attributes.file)}",
                      storepath='gnr.appmenu.root')
      