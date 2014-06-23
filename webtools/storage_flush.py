#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.web.gnrbaseclasses import BaseWebtool

class StorageFlush(BaseWebtool):
    def __call__(self, *args, **kwargs):
        if kwargs['environ']['REMOTE_ADDR'] == '127.0.0.1':
            self.site.shared_data.flush_all()
