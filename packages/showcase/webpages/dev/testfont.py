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
        root.script(src="http://use.typekit.com/nrc3upi.js")
        root.dataController("try{Typekit.load();console.log('okkkkkkkkkkk')}catch(e){}",_onStart=True)
        fb=root.div(font_size='20px').formbuilder(cols=1,margin_top='30px',margin_left='30px')
        fb.div('Abcde effe',_class='tk-ff-cocon-web-pro',font_size='48px')
        fb.div('Abcde effe',_class='tk-museo',font_size='48px')
