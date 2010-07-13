#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import datetime

class GnrCustomWebPage(object):
    def windowTitle(self):
         return '!!Hello world'
         
    def main(self, root, **kwargs):
        root.button('What is the time?',action='FIRE get_time;')
        root.dataRpc('result','giveMeTime',_fired='^get_time')
        root.div('^result')
        
    def rpc_giveMeTime(self):
        return datetime.datetime.now()