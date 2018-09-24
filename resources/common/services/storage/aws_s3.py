
# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2013 Softwell. All rights reserved.

from gnr.services import GnrBaseService
#from gnr.core.gnrlang import componentFactory

class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.parent = parent
    
    def write(self,*args):
        print 'write s3'