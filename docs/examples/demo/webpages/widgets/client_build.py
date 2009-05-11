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
    def main(self, root,cols='3', **kwargs):
        root = self.rootLayoutContainer(root)
        split = root.splitContainer(height='100%')
        sp1=split.splitContainer(sizeShare='30',orientation='vertical')
        tree = sp1.contentPane(sizeShare='50',background_color='smoke').tree(storepath='*D',
                                                  selected='datatree.selectedLabel',
                                                  selected_treecaption='datatree.selectedCaption',
                                                  inspect='shift',label="Data")
          
        tree = sp1.contentPane(sizeShare='50',background_color='smoke').tree(storepath='*S',
                                                    selectedLabel='srctree.selectedLabel',
                                                    selectedItem='srctree.selectedItem',
                                                    selectedPath='srctree.selectedPath',
                                                    connect_onClick='genro.src.highlightNode($1)',
                                                    inspect='shift',label="Structure")
                                                            
        lc = split.layoutContainer(sizeShare='70', height='100%')
        top = lc.contentPane(layoutAlign='top', height='4em')
        fb = top.formbuilder(cols=2)
        fb.textBox(value='^check_num')

        paneCheck =lc.contentPane(layoutAlign='client').div(nodeId='paneCheck',margin='5px',padding='5px',margin='1px solid red')

        root.dataScript('dummy', """var node = genro.nodeById('paneCheck').freeze().clearValue()
                              if (num){
                                  for (var i = 0; i < num; i++) {
                                       node._('div')._('checkbox', {value:'^check.r_'+i,margin:'2px', label:'Check r_'+i});
                                  }
                              }
                              node.unfreeze()
                                    """, num='^check_num')     
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
        