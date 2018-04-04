#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Migration
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
import gzip
from StringIO import StringIO
import pickle

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="""public:Public,startupdata_manager/startupdata_manager:StartupDataManager"""
    pageOptions={'openMenu':False,'enableZoom':False}
    auth_main = 'admin'

    def windowTitle(self):
        return '!!Startup data'

    def main(self, root, **kwargs):
        bc = root.rootBorderContainer(title='Startup data manager',datapath='main',design='sidebar')
        tc = bc.tabContainer(region='center',margin='2px')
        tc.startupDataSaver(title='Startup Datasets',datapath='.saver')
        tc.startupDataDbTemplates(title='Db templates',datapath='.dbtemplates')

    

