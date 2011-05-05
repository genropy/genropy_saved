# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdict import dictExtract
from gnr.core.gnrstring import boolean

class GnrCustomWebPage(object):
    py_requires='public:TableHandlerMain'
    def onTableHandlerBuilding(self,root,th_options=None,mainKwargs=None):
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')    
        pkg = callArgs.pop('th_pkg',None)
        table = callArgs.pop('th_table',None)
        pkey = callArgs.pop('th_pkey',None)
        self.maintable = '%s.%s' %(pkg,table)
        self.th_parentId = mainKwargs.pop('th_parentId',None)        
        th_options.update(dictExtract(mainKwargs,'th_'))
        mangler = str(id(root))
        self._th_mixinResource(mangler,table=self.maintable,resourceName=th_options.get('resourceName'),defaultClass='View')
        resource_options = self._th_hook('options',mangler=mangler,dflt=dict())()
        th_options.update(resource_options)
        th_options['public'] = boolean(th_options.get('public',True))
        mainKwargs['th_pkey'] = pkey

    def onTableHandlerBuilt(self,th,th_options=None,mainKwargs=None):
        dialog_pars = self._th_hook('dialog',mangler=th.form)()
        
        dialog_pars = dialog_pars or dict(height='600px',width='900px')
        th.dataController("""
        if(parentId!='null'){
            genro.publish({"topic":"resize","parent":true,nodeId:parentId},dialog_pars);
        }
        """,_init=True,dialog_pars=dialog_pars,parentId=self.th_parentId or 'null')