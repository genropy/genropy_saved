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

    def main_sc(self, root,th_pkg=None,th_table=None,th_public=True,th_parentId=None,**kwargs):
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
        th = root.stackTableHandler(table=table,datapath=table.replace('.','_'),virtualStore=True,**kwargs)
        dialog_pars = self._th_hook('dialog',mangler=th.form)()
        dialog_pars = dialog_pars or dict(height='600px',width='900px')
        root.dataController("""
        if(parentId!='null'){
            genro.publish({"topic":"resize","parent":true,nodeId:parentId},dialog_pars);
        }
        """,_init=True,dialog_pars=dialog_pars,parentId=th_parentId or 'null')
