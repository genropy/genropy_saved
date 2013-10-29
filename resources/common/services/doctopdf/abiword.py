#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
from subprocess import call
import os


class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.parent = parent

    def convert(self,path):
        print ddddokok
        result = call(['abiword', '--to=pdf',path])
        if result !=0:
            return None
        name,ext = os.path.splitext(path)

        return '%s.pdf' %name