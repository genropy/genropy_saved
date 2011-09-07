#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" galleria.py """
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
        return 'galleria.html'
    
    def main(self, rootBC, **kwargs):
        pass
        
    def getGallery(self):
        immagini=self.db.table('flib.item_category').query(columns='@item_id.url AS url', where='@category_id.code=:codice', codice='galleria').fetch()
        chunks =list(self.chunks(immagini, 4))
        return chunks

    def chunks(self,l,n):
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

