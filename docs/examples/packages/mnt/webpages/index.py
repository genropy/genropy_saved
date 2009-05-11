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
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'public:Public,public:StandardIndex'
    
    def windowTitle(self):
         return '!!Manettiani.org'
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'

    def main(self, root, **kwargs):
        center, top, bottom = self.pbl_rootBorderContainer(root, 'mnt',datapath='form')
        center.iframe(height='100%',width='100%',src='http://www.manettiani.org',border='0px')

        
#    def pageMenues(self):
#        self.addPageMenu('!!Tables management','backoffice/index.py')
    
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
