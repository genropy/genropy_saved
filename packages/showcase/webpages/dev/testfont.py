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
         return '!! test font'

    def main(self, root, **kwargs):
        pane=root.div(font_size='20px')

        for k in range (7,48):
            pane.div('This is museo font %ipx'%k,_class='tk-museo',font_size='%ipx' %k)
            
        for k in range (7,48):
            pane.div('This is cocon font %ipx'%k,_class='tk-ff-cocon-web-pro',font_size='%ipx' %k)
            
            
            
