#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services import GnrBaseService

class QueueService(GnrBaseService):
    def __init__(self,parent,**kwargs):
        self.parent = parent

    