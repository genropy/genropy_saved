# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdict import dictExtract
from gnr.core.gnrstring import boolean

class GnrCustomWebPage(object):
    py_requires='public:TableHandlerMain'
    def __prepareKwargs(self,mainKwargs=None):
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')    
        pkg = callArgs.pop('th_pkg',None)
        table = callArgs.pop('th_table',None)
        pkey = callArgs.pop('th_pkey',None)
        self.maintable = '%s.%s' %(pkg,table)
        self.th_iframeContainerId = mainKwargs.pop('th_iframeContainerId',None)
        return pkey

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
        pkey = self.__prepareKwargs(kwargs)     
        mangler = str(id(root))
        self._th_mixinResource(mangler,table=self.maintable,resourceName=th_options.get('resourceName'),defaultClass='View')
        resource_options = self._th_hook('options',mangler=mangler,dflt=dict())()
        th_options.update(resource_options)
        th_options.update(dictExtract(kwargs,'th_'))
        th_options['public'] = boolean(th_options.get('public',True))
        kwargs['th_pkey'] = pkey
        th = self._th_main(root,th_options=th_options,**kwargs)
        if self.th_iframeContainerId:
            self.resizeIframeContainer(th,th_options=th_options,mainKwargs=kwargs)
        
    def rpc_form(self, root,th_formResource=None,**kwargs):
        pkey = self.__prepareKwargs(kwargs) or '*newrecord*'
        form = self._th_prepareForm(root,pkey=pkey,**kwargs)
        self._th_hook('form',mangler=self.maintable)(form)