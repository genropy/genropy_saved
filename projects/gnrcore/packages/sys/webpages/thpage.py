# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdict import dictExtract
from gnr.core.gnrstring import boolean

class GnrCustomWebPage(object):
    py_requires='public:TableHandlerMain'
    
    @property
    def package(self):
        pkgId,tbl = self.maintable.split('.')
        if pkgId:
            return self.db.package(pkgId)
    
    @property
    def maintable(self):
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')
        return '%(th_pkg)s.%(th_table)s' %callArgs

    def resizeIframeContainer(self,th,th_options=None,mainKwargs=None):
        dialog_pars = self._th_hook('dialog',mangler=th.form)()
        
        dialog_pars = dialog_pars or dict(height='600px',width='900px')
        th.dataController("""
        if(parentId!='null'){
            genro.publish({"topic":"resize","parent":true,nodeId:parentId},dialog_pars);
        }
        """,_init=True,dialog_pars=dialog_pars,parentId=self.th_iframeContainerId or 'null')

    def main(self,root,**kwargs):
        th_options = dict(formResource=None,viewResource=None,formInIframe=False,widget='stack',readOnly=False,virtualStore=True,public=True)
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')    
        self.th_iframeContainerId = kwargs.pop('th_iframeContainerId',None)
        pkey = callArgs.pop('th_pkey',None)   
        resource = self._th_getResClass(table=self.maintable,resourceName=th_options.get('resourceName'),defaultClass='View')()
        resource_options = resource.th_options() if hasattr(resource,'th_options') else dict()
        th_options.update(resource_options)
        th_options.update(dictExtract(kwargs,'th_'))
        th_options['public'] = boolean(th_options.get('public',True))
        kwargs['th_pkey'] = pkey
        th = self._th_main(root,th_options=th_options,**kwargs)
        if self.th_iframeContainerId:
            self.resizeIframeContainer(th,th_options=th_options,mainKwargs=kwargs)
        
    def rpc_form(self, root,**kwargs):
        callArgs =  self.getCallArgs('th_pkg','th_table','th_pkey') 
        pkey = callArgs.pop('th_pkey',None)
        form = self._th_prepareForm(root,pkey=pkey,**kwargs)
        self._th_hook('form',mangler=self.maintable)(form)