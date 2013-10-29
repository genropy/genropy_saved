#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
from subprocess import call


class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.parent = parent

    def convert(self,path):
        try:
            call(['abiword', '--to=pdf',path])
        except Exception:
            return path
        return path.replace('.doc','.pdf')