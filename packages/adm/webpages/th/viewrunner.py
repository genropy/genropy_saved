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
    py_requires = """tablehandler/th_list:TableHandlerListBase"""

    def onIniting(self, url_parts, request_kwargs):
        self.mixin_path = '/'.join(url_parts)
        if request_kwargs.get('method') == 'main':
            request_kwargs['th_pkg'] = url_parts.pop(0)
            request_kwargs['th_table'] = url_parts.pop(0)
        while len(url_parts)>0: 
            url_parts.pop(0)

    def main(self,root,th_pkg=None,th_table=None,th_pkey=None,th_viewName=None,th_loadEvent=None,**kwargs):
        fulltable = '.'.join([th_pkg,th_table])
        tableCode = fulltable.replace('.','_')
        defaultName = 'th_%s' %th_table
        viewName = th_viewName or defaultName
        self.mixinComponent(th_pkg,'tables',th_table,'%s:View' %viewName,mangling_th=tableCode)
        root.attributes['datapath'] = tableCode
        listpage = root.listPage(frameCode='%s_list' %tableCode,table=fulltable,pageName='view')