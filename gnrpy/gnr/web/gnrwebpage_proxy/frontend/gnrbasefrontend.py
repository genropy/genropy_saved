#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------

from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy


class GnrBaseFrontend(GnrBaseProxy):
    
    def init(self, **kwargs):
        pass
        
    def importer(self):
        return ''
    
    def event_onBegin(self):
        pass
        
    def frontend_arg_dict(self):
        pass