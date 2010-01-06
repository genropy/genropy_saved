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
        tb = root.toolbar()
       #box = tb.div(width='20px',height='20px',background_color='red')
       #menu = box.menu(modifiers='*',action="function(attributes){genro.gotoURL(attributes.file)}",
       #                storepath='gnr.appmenu')
       #