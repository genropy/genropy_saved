# -*- coding: UTF-8 -*-

# filtering.py
# Created by Francesco Porcari on 2011-10-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"FilteringSelect"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """Zero code"""
        pane.filteringSelect(value='^.pippo',values='0:Zero,1:One,2:Two')