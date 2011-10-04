#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

""" specialita.py """
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage import GnrGenshiPage as page_factory
from gnr.web.gnrwsgisite import httpexceptions
from genshi import HTML


class GnrCustomWebPage(object):
    from tools import codeToPath
    css_requires='website'
    
    def _pageAuthTags(self, method=None, **kwargs):
           return 'user'
    
    def genshi_template(self):
        return 'specialita.html'
    
    def main(self, rootBC, **kwargs):
        pass

