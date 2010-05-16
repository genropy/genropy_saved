#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'public:Public' # ,public:StandardIndex
    
    def windowTitle(self):
         return '!!Developer App'

    # def pageAuthTags(self, method=None, **kwargs):
    #     return 'user'

    def main(self, root, **kwargs):
        center, top, bottom = self.pbl_rootBorderContainer(root, '',datapath='form')
        center.div('Developer Information', align='center', margin_top='20px', color='silver', font_size='16pt')
