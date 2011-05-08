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
    py_requires = """tablehandler/th_form:TableHandlerBase"""


    def main(self,root,th_formResource=None,**kwargs):
        call_args = self.getCallArgs('th_pkg','th_table','th_pkey')
        th_table = call_args['th_table']
        th_pkg = call_args['th_pkg']
        fulltable = '.'.join([th_pkg,th_table])
        tableCode = fulltable.replace('.','_')
        defaultName = 'th_%s' %th_table
        formResource = th_formResource or defaultName
        if not ':' in formResource:
            formResource = '%s:Form' %formResource
        root.attributes['datapath'] = tableCode
        self.mixinComponent(th_pkg,'tables',th_table,formResource,mangling_th=tableCode)
        form = root.formPage(frameCode='%s_form' %tableCode,table=fulltable,startKey=call_args['th_pkey'],**kwargs)
