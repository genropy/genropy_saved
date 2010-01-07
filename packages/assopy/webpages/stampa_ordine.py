#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

import os

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        pass

def stampa(req, ordine_id, locale, **kwargs):
    localelang = locale.split('-')[0]
    page = GnrWebPage(req, GnrCustomWebPage, __file__, ordine_id=ordine_id, locale=locale, **kwargs)
    
    ordine = page.db.table('assopy.ordine').record(ordine_id, mode='record', ignoreMissing=True)
    if not ordine:
        from mod_python import apache
        raise apache.SERVER_RETURN, apache.HTTP_UNAUTHORIZED 
    if ordine['numero'].startswith('D'):
        tipodoc = 'ricevuta.tpl'
    else:
        tipodoc = 'fattura.tpl'
        
    tplfile = page.getResource(os.path.join('doc_templates', locale, tipodoc))
    if not tplfile or not os.path.exists(tplfile):
        tplfile = page.getResource(os.path.join('doc_templates', tipodoc))
        
    return page.index(mako=tplfile)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
