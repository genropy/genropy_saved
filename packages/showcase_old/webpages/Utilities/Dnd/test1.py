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
        root.css('.dojoDndItemSelected {border:4px dotted silver;}')
        root.css('.dojoDndItemAnchor {border:4px dotted blue;}')
        src=dict(width='40px',height='40px',margin='10px')
        tgt=dict(width='80px',height='80px',margin='10px')
        root=root.div(width='40px')
        draggable=root.div(dnd_source=True,dnd_singular=False)
        draggable.div(background_color='green',dnd_itemType='green',**src)
        draggable.div(background_color='red',dnd_itemType='red',**src)
        draggable.div(background_color='pink',dnd_itemType='pink',**src)
        draggable.div(background_color='yellow',dnd_itemType='yellow',**src)
        targets=root.div(dnd_target=True,isSource=False,dnd_accept='green,red',
                        height='240px',width='120px',
                        border='1px solid green')
        #targets.div(border='3px solid green',**tgt)
        #targets.div(border='3px solid red',**tgt)
        #targets.div(border='3px solid pink',**tgt)
        #targets.div(border='3px solid yellow',**tgt)
