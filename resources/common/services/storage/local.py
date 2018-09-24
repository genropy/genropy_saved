#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.services import GnrBaseService

class Main(GnrBaseService):
    def __init__(self, parent=None,**kwargs):
        self.parent = parent