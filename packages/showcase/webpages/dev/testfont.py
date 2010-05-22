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
         return '!! test font'

    def main(self, root, **kwargs):
        root.script(src="http://use.typekit.com/tji2xhd.js")
        root.script("try{Typekit.load();}catch(e){}")
        #root.tree(storepath='gnr',margin_top='30px',margin_left='30px')
        fb=root.div(font_size='20px').formbuilder(cols=1,margin_top='30px',margin_left='30px')
        fb.div('ssssss')
