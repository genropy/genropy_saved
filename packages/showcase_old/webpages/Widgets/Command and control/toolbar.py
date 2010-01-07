#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Toolbar example """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='public:Public,standard_tables:TableHandler'

    def main(self, root, **kwargs):     
        root.css('.specialToobar .dijitToolbar', """background-image:none; background-color:#d5d5d5;""")
        rootBc,top,bottom = self.pbl_rootBorderContainer(root,title='toolbar')
        leftpane = rootBc.contentPane(region='left',width='200px')
        center = rootBc.borderContainer(region='center')
        ctop = center.borderContainer(region='top',height='30%',margin='10px')
        cbottom = center.borderContainer(region='center')
        bc1 = ctop.borderContainer(region='left',width='300px',_class='specialToobar')
        top = bc1.toolbar(region='top',_class='pbl_viewBoxLabel')
        #tb=top.toolbar(height='18px',padding='0px')
        containerNode = top.div(tip='^aux.deleteMsg',_class='floatRight')
        containerNode.button(iconClass="buttonIcon icnBaseDelete" ,
                    margin='0px',padding='0',showLabel=False,action='alert("cutting...")',
                    disabled='^aux.disable')
        top.data('aux.deleteMsg','Delete')
        top.data('aux.disable',False)


        center = bc1.contentPane(region='center',_class='pbl_viewBox')  
        center.textbox(value='^aux.deleteMsg',tip='ppp')
        center.checkbox(value='^aux.disable')
        


