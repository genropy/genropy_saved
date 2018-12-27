# -*- coding: utf-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.


class GnrCustomWebPage(object):
    py_requires='public:TableHandlerMain'
    auth_main='user'
    
    @classmethod
    def getMainPackage(cls,request_args=None,request_kwargs=None):
        return request_kwargs.get('th_from_package') or request_args[0]

    def onIniting(self, request_args, request_kwargs):
        pageResource = request_kwargs.get('th_pageResource')
        maintable = None
        if len(request_args)==3:
            pkg,tbl,pkey = request_args
            maintable = '%s.%s' %(pkg,tbl)
        else:
            pkg,tbl = request_args
            maintable = '%s.%s' %(pkg,tbl)
        if not maintable:
            return

        defaultModule = 'th_%s' %tbl
        resourcePath = self._th_getResourceName(pageResource,defaultModule,'Page')
        self.mixinComponent(resourcePath,safeMode=True,only_callables=False)
        self.mixinComponent('tables',tbl,resourcePath,pkg=pkg,pkgOnly=True,safeMode=True,only_callables=False)
        self.mixinComponent('tables','_packages',pkg,tbl,resourcePath,pkg=self.packageId,pkgOnly=True,safeMode=True,only_callables=False)

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
    