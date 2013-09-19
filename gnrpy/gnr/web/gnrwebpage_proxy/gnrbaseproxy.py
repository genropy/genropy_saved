#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  gnrbaseproxy.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrBaseProxy(object):
    """TODO"""
    def __init__(self, page, **kwargs):
        self.page = page
        [self.page._subscribe_event(attr[6:], self) for attr in dir(self) if attr.startswith('event_')]
        ## For every method starting with 'event_' self.page._subscribe_event is called
        self.init(**kwargs)

    @property
    def debugger(self):
        return self.page.debugger

        
    def init(self, **kwargs):
        """Hook method. You can customize the ``__init__`` method"""
        pass