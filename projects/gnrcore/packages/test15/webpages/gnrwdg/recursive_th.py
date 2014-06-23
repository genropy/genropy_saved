
# # -*- coding: UTF-8 -*-

# recursive_th.py
# Created by Francesco Porcari on 2011-09-18.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='public:TableHandlerMain'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
        return ''
         
    def main(self, rootBC, **kwargs):
        pass