# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.


class GnrCustomWebPage(object):
    py_requires='public:TableHandlerMain'
    
    @classmethod
    def getMainPackage(cls,request_args=None,request_kwargs=None):
        return request_kwargs.get('th_from_package') or request_args[0]
        
    @property
    def maintable(self):
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')
        return '%(th_pkg)s.%(th_table)s' %callArgs

    def deferredMainPageAuthTags(self,page):
        if hasattr(self,'root_tablehandler') and self.root_tablehandler.view.attributes.get('_notallowed'):
            return False
        if hasattr(self,'root_form') and self.root_form.attributes.get('_notallowed'):
            return False
        return True
    
    @property
    def pagename(self):
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')  
        return 'thpage_%(th_pkg)s_%(th_table)s' %callArgs

    #FOR ALTERNATE MAIN HOOKS LOOK AT public:TableHandlerMain component
    def main(self,root,th_pkey=None,**kwargs):
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')  
        root.data('gnr.pagename', self.pagename)
        pkey = callArgs.pop('th_pkey',None)  
        th_pkey = pkey or th_pkey
        root.rootTableHandler(th_pkey=th_pkey,**kwargs)
    