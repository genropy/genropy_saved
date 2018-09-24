
# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2013 Softwell. All rights reserved.

from gnr.core.gnrbaseservice import GnrBaseService
#from gnr.core.gnrlang import componentFactory

class Main(GnrBaseService):
    def write(self,*args):
        print 'write',args

    def delete(self,*args):
        print 'delete',args

