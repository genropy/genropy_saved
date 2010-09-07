# -*- coding: UTF-8 -*-

# hello.py
# Created by Francesco Porcari on 2010-08-19.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return ''
         
    def main_root(self, root, **kwargs):
        root.div('hello')
        root.button('rpcrun',fire='run')
        root.dataRpc('dummy','dummy',_fired='^run')
    
    def rpc_dummy(self):
        return ''
        