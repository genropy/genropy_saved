#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):    
    py_requires = 'public:Public,public:StandardIndex'
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
    
    
    def indexTitle(self):
        return "Softwell"
    
    def main(self, root, **kwargs):
        center, top, bottom = self.pbl_rootBorderContainer(root, 'Softwell',datapath='form')
        center.iframe(height='100%',width='100%',src='_resources/indexcontent.html',border='0px')

            

