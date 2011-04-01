# -*- coding: UTF-8 -*-

# tablehandler.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    """
    http//mysite/adm/th/thrunner/package/table/pkey? widget='se diverso da stack' && formName='' && viewName= && iframe='v||f||b'
    """

    def onIniting(self, url_parts, request_kwargs):
        self.mixin_path = '/'.join(url_parts)
        pkg = url_parts.pop(0)
        tablename = url_parts.pop(0)
        table = '%s.%s' %(pkg,tablename)
        name = request_kwargs.pop('formName','default')
        self.maintable = table
        self.mixinComponent(pkg,'tables',tablename,'thform','%s:Main' %name)
        if url_parts:
            request_kwargs['pkey'] = url_parts.pop(0)
        while len(url_parts)>0: 
            url_parts.pop(0)


    def main_stack(self, rootBC, **kwargs):
        sc = pane.stackTableHandler(height='400px',table='glbl.localita',inputForm='thform/default')
        sc.form.store.handler('load',default_provincia='MI')
        
    def main_frame(self, rootBC, **kwargs):
        bc = pane.borderContainer(height='600px')
        gridpane = bc.contentPane(region='top',height='50%')
        formpane = bc.contentPane(region='center')
        formpane.dataController("",dbevent="^gnr.dbevent.glbl_localita.id")
        gridpane.iframeTableHandler(table='glbl.localita',inputPane=formpane) 