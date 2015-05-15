# -*- coding: UTF-8 -*-

# filtering.py
# Created by Francesco Porcari on 2011-10-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"FilteringSelect"
class GnrCustomWebPage(object):
    dojo_source=True
    #py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''

    def isDeveloper(self):
        return True
         
    def main_root(self,root,**kwargs):
        """Zero code"""
        box = root.div(datapath='main')
        box.data('.pippo','1')
        box.button('Set value',action='SET .pluto=null;')
        box.filteringSelect(value='^.pippo',values='0:Zero,1:One,2:Two')
        box.filteringSelect(value='^.pluto',values='0:Zero,1:One,2:Two')
        box.dbselect(value='^.user',dbtable='adm.user',hasDownArrow=True)