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

    def main(self,root,th_pkg=None,th_table=None,th_pkey=None,th_viewResource=None,th_loadEvent=None,**kwargs):
        call_args = self.getCallArgs('th_pkg','th_table')
        th_table = call_args['th_table']
        th_pkg = call_args['th_pkg']
        fulltable = '.'.join([th_pkg,th_table])
        tableCode = fulltable.replace('.','_')
        defaultName = 'th_%s' %th_table
        viewResource = th_viewResource or defaultName
        if not ':' in viewResource:
            viewResource = '%s:View' %viewResource
        self.mixinComponent(th_pkg,'tables',th_table,'%s:View' %viewResource,mangling_th=tableCode)
        root.attributes['datapath'] = tableCode
        listpage = root.listPage(frameCode='%s_list' %tableCode,table=fulltable,pageName='view')