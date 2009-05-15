#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import DirectoryResolver

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    
    def main(self, root, **kwargs):
        bc = root.borderContainer()
        left = bc.contentPane(region='left',background_color='pink',width='30%',
                             splitter=True,padding='3em')
        center = bc.contentPane(region='center',background_color='whitesmoke',padding='3em')
        self.left_pane(left)
        self.center_pane(center)
    
    def left_pane(self,pane):
        tbl = pane.table(border='1px solid red')
        head = tbl.thead()
        body = tbl.tbody()
        for x in range(10):
            pane.dataController("alert('sono il bottone %i - '+msg)" %x,msg="^buttons.b_%i" %x)
            r = body.tr()
            r.td().div('sono la cella %i' %x)
            r.td().button('Push it',fire="buttons.b_%i" %x)
            
    def center_pane(self,pane):
        """docstring for center_pane"""
        pane.data('mydata.disk',self.get_diskdir('/Users'))
        tree = pane.tree(storepath='mydata.disk',inspect='shift',
                        persist=False, label="Disk Directory")
        
    def get_diskdir(self,path):
        """docstring for get_diskdir"""
        return  DirectoryResolver(path)()
        
    