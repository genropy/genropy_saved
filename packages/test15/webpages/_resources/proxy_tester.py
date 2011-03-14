# -*- coding: UTF-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-09.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class Proxy_test(BaseComponent):
    proxy=True

    def ciao(self):
        return 'ciao'

    def rpc_ciao(self):
        return 'ciao'

class Proxy_test2(BaseComponent):
    proxy='proxy_test'

    def rpc_ciao(self):
        return 'ciao2'