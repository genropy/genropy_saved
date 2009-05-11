#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = root.div(height='100%',padding='10px',gnrId='bigone',background_color='pink')
        lc = root.layoutContainer(height='100%')
        
        pane1a = lc.contentPane(layoutAlign='top', border='1px solid silver', height='30px', margin='1px')
        
        pane1a.button('remove first button', action="genro.getSource(genro.pane2).delItem('#0')")
        pane1a.button('remove layout in panel 2', action="genro.getSource(genro.pane3).delItem('#0')")
        pane1a.button('remove from pane 4', action="genro.getSource(genro.pane4).delItem('#0')")
        pane1a.button('remove all', action="genro.getSource(genro.bigone).delItem('#0')")
        
        pane1b = lc.contentPane(layoutAlign='top', border='1px solid silver', height='30px', margin='1px')
        
        pane1b.button('change first button',action="genro.getSource(genro.pane2)._('textbox','#0',{})")
        pane1b.button('remove layout in panel 2',action="genro.getSource(genro.pane3).delItem('#0')")
        pane1b.button('remove from pane 4',action="genro.getSource(genro.pane4).delItem('#0')")
        pane1b.button('remove all',action="genro.getSource(genro.bigone).delItem('#0')")
        
        pane2 = lc.contentPane(layoutAlign='top',border='1px solid silver',height='30px',margin='1px',gnrId='pane2')
        pane2.button('aaa', subscribe_alfa='console.log("alfa")',
                            subscribe_beta='console.log("beta")')  
        m1=pane2.dropdownbutton('bbb',name='b', subscribe_alfa='console.log("alfa")',).menu()
        m1.menuline('aaaaaa')
        m1.menuline('bbbbbb')
        
        pane2.button('ccc')
        pane2.button('ddd')
        pane2.textbox()
        pane2.button('eee')
        pane3=lc.contentPane(layoutAlign='top',border='1px solid silver',height='300px',margin='1px',gnrId='pane3')
        pane4=lc.contentPane(layoutAlign='top',border='1px solid silver',height='300px',padding='10px',gnrId='pane4')
        p=pane4
        for m in range(10):
            p=p.div(border='1px solid silver',height='%ipx' % (200-m*6),margin='2px')
        s=p.splitContainer(height='100%')
        s.contentPane(sizeShare=30)
        s.contentPane(sizeShare=70)
        innerlc=pane3.layoutContainer(height='100%')
        pane3_1=innerlc.contentPane(layoutAlign='top',border='1px solid silver',height='30px',margin='1px')
        pane3_2=innerlc.contentPane(layoutAlign='top',border='1px solid silver',height='30px',margin='1px',gnrId='pane3_2')
        pane3_3=innerlc.contentPane(layoutAlign='top',border='1px solid silver',height='30px',margin='1px')
        pane3_4=innerlc.contentPane(layoutAlign='top',border='1px solid silver',height='30px',margin='1px')
        pane3_1.button('remove first button',action="genro.getSource(genro.pane3_2).delItem('#0')")
        pane3_2.button('aaa3',name='a')  
        m2=pane3_2.dropdownbutton('bbb3',name='b').menu()
        m2.menuline('aaaaaa')
        m2.menuline('bbbbbb')
        pane3_2.button('ccc3',name='c')  
        pane3_2.button('ddd3',name='d')
    
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
