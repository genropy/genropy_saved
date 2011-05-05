# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdict import dictExtract
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
        mainKwargs['th_pkey'] = pkey

    def onTableHandlerBuilt(self,th,th_options=None,mainKwargs=None):
        dialog_pars = self._th_hook('dialog',mangler=th.form)()
        dialog_pars = dialog_pars or dict(height='600px',width='900px')
        th.dataController("""
        if(parentId!='null'){
            genro.publish({"topic":"resize","parent":true,nodeId:parentId},dialog_pars);
        }
        """,_init=True,dialog_pars=dialog_pars,parentId=self.th_parentId or 'null')