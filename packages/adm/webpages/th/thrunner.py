# -*- coding: UTF-8 -*-

# tablehandler.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrstring import boolean
class GnrCustomWebPage(object):
    py_requires = """public:Public,tablehandler/th_components:TableHandlerBase"""
    css_requires='public'
    plugin_list=''
    def onMain_pbl(self):
        pass
    
    def main(self,root,**kwargs):
        kwargs.update(self.getCallArgs('th_pkg','th_table','th_pkey'))
        th_widget = kwargs.pop('th_widget','sc')
        handler = getattr(self,'main_%s' %th_widget)
        assert handler, 'not exitsting handler for widget %s' %th_widget
        handler(root,**kwargs)

    def main_sc(self, root,th_pkg=None,th_table=None,th_public=True,**kwargs):
        th_public = boolean(th_public)
        table = '%s.%s' %(th_pkg,th_table)
        self.maintable = table
        if th_public:
            tblobj = self.db.table(table)
            root = root.rootContentPane(title=tblobj.name_long)
        else:
            root_attributes = root.attributes
            root_attributes['tag'] = 'ContentPane'
            root_attributes['_class'] = ''
        root.stackTableHandler(table=table,datapath=table.replace('.','_'),**kwargs)
