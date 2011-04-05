#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#   form _runner
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = """tablehandler/th_form:TableHandlerFormBase"""

    def onIniting(self, url_parts, request_kwargs):
        self.mixin_path = '/'.join(url_parts)
        if request_kwargs.get('method') == 'main':
            request_kwargs['th_pkg'] = url_parts.pop(0)
            request_kwargs['th_table'] = url_parts.pop(0)
            if url_parts:
                request_kwargs['th_pkey'] = url_parts.pop(0)
        while len(url_parts)>0: 
            url_parts.pop(0)

    def main(self,root,th_pkg=None,th_table=None,th_pkey='*norecord*',th_formName=None,th_storeType=None,**kwargs):
        fulltable = '.'.join([th_pkg,th_table])
        tableCode = fulltable.replace('.','_')
        defaultName = 'th_%s' %th_table
        formName = th_formName or defaultName
        root.attributes['datapath'] = tableCode
        self.mixinComponent(th_pkg,'tables',th_table,'%s:Form' %formName,mangling_th=tableCode)
        form = root.formPage(frameCode='%s_form' %tableCode,table=fulltable,startKey=th_pkey,**kwargs)
