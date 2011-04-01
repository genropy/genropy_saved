# -*- coding: UTF-8 -*-

# tablehandler.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = """tablehandler/th_components:StackTableHandler"""
    """
    http//mysite/adm/th/thrunner/package/table/pkey? th_widget='se diverso da stack' && th_formName='' && th_viewName= && th_iframe='v||f||b'
    """
    def onIniting(self, url_parts, request_kwargs):
        self.mixin_path = '/'.join(url_parts)
        if request_kwargs.get('method') == 'main':
            request_kwargs['th_pkg'] = url_parts.pop(0)
            request_kwargs['th_table'] = url_parts.pop(0)
            if url_parts:
                request_kwargs['th_pkey'] = url_parts.pop(0)
        while len(url_parts)>0: 
            url_parts.pop(0)
    
    def main(self,root,**kwargs):
        th_widget = kwargs.pop('th_widget','sc')
        handler = getattr(self,'main_%s' %th_widget)
        assert handler, 'not exitsting handler for widget %s' %th_widget
        #pane = root.rootContentPane(title='Test',datapath='test')
        handler(root,**kwargs)

    def main_sc(self, root,th_pkg=None,th_table=None, **kwargs):
        table = '%s.%s' %(th_pkg,th_table)
        sc = root.stackTableHandler(table=table,datapath=table.replace('.','_'),**kwargs)
        #sc.form.store.handler('load',default_provincia='MI')
        
  # def main_frame(self, rootBC, **kwargs):
  #     bc = root.borderContainer(height='600px')
  #     gridpane = bc.contentPane(region='top',height='50%')
  #     formpane = bc.contentPane(region='center')
  #     formpane.dataController("",dbevent="^gnr.dbevent.glbl_localita.id")
  #     gridpane.iframeTableHandler(table='glbl.localita',inputPane=formpane) 