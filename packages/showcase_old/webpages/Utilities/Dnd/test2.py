#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Drag&Drop test 1
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

"""  Drag&Drop test 1 """
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):    

    def main(self, root, **kwargs):
        #root.script("dojo.subscribe('/dnd/start',function(foo){console.debug(foo);})")
        root.css('.dojoDndItemSelected {border:1px dotted red;}')
        root.css('.dojoDndItemAnchor {border:1px dotted green;}')

        a1=root.textarea(width='30em',height='30ex')
        a2=root.textarea(width='30em',height='30ex')

