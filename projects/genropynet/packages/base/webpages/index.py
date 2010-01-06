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
        root.div('hello genropy')
        root.div(width='20px',height='20px',background_color='red').menu(action="function(attributes){genro.gotoURL(attributes.href)}").remote('menu_browse',cacheTime=60)


