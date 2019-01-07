#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-


from gnr.lib.services import GnrBaseService

class LdapsService(GnrBaseService):
    def __init__(self,parent,**kwargs):
        self.parent = parent
