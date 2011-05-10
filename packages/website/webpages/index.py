#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage import GnrGenshiPage as page_factory
from gnr.web.gnrwsgisite import httpexceptions

class GnrCustomWebPage(object):
    from tools import codeToPath
    css_requires='website'
    
    def _pageAuthTags(self, method=None, **kwargs):
           return 'user'
    
    def genshi_template(self):
        return 'index.html'
    
    def main(self, rootBC, **kwargs):
        pass