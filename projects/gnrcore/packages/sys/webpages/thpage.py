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
        pkgId = self._call_kwargs.get('th_from_package')
        if not pkgId:
            pkgId,tbl = self.maintable.split('.')
        if pkgId:
            return self.db.package(pkgId)
    
    @property
    def maintable(self):
        callArgs = self.getCallArgs('th_pkg','th_table','th_pkey')
        return '%(th_pkg)s.%(th_table)s' %callArgs

    
    #FOR ALTERNATE MAIN HOOKS LOOK AT public:TableHandlerMain component
    def main(self,root,**kwargs):
        root.data('gnr.windowTitle',self.db.table(self.maintable).name_plural)
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
    