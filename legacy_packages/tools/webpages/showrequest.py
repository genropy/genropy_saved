#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
""" GnrDojo : Show request object """

import os.path
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

#-------  configure: customize this configuration ------
class GnrCustomWebPage(object):
    def strval(self,value):
        value=str(value)
        try:
            unicode(value)
        except:
            value = '***err***'
        return value
    def main(self, root, **kwargs):
        def notcallables():
            req=self.request
            for k in dir(req):
                v=getattr(req,k)
                if not callable (v):
                    yield (k,v)
        def callables():
            req=self.request
            for k in dir(req):
                v=getattr(req,k)
                if callable (v):
                    yield (k,v)
                
        client = self.rootLayoutContainer(root)
        lc = client.layoutContainer(height='100%')
        pane=lc.contentPane(layoutAlign='top',border_bottom='1px solid silver', height='5em')
        
        tc=lc.tabContainer(layoutAlign='client')
        req=self.request
        self.attrPane(tc.contentpane(title='Attributes'),notcallables())
        self.callPane(tc.contentpane(title='Callables'),callables ())
        self.testPane(tc.contentpane(title='Test'))
        
    def attrPane(self,pane,attributes):
        fb=pane.formbuilder(margin_left='5px',margin_top='5px',cols=2,lblclass='labels',border_spacing='1px')
        for name,value in attributes:
            if isinstance(value,basestring):
                if value=='' :
                    value='&nbsp'
                fb.div(self.strval(value.strip()),lbl=name, _class='values')
                fb.div('string',_class='types',lbl_display='none')
            elif hasattr(value,'keys'):
                if len(value)==0:
                    fb.div(self.strval(value),lbl=name,_class='values')
                    fb.div('keyed',_class='types',lbl_display='none')
                else:
                    innerfb=fb.div(lbl=name,_class='values').formbuilder(cols=1,lblclass='labels',border_spacing='1px')
                    fb.div('keyed',_class='types',lbl_display='none')
                    for k,v in value.items():
                        innerfb.div(self.strval(v),lbl=k,_class='valuesInner')
            else:
                if hasattr(value,'__class__'):
                    rtype= value.__class__.__name__
                else:
                    rtype= 'unknown'
                    
                fb.div('%s &nbsp'%self.strval(value),lbl=name,_class='values')
                fb.div(rtype,_class='types',lbl_display='none')
            
       # xx=len(req.filename.replace(req.hlist.directory,'').split('/'))-1
       # requestData.append({'Id':'usrreq','type':'hh','value':xx*'../'})
       # data.rowchild(_attributes=self.rowCompose(name,value))
    def callPane(self,pane,callables):
        fb=pane.formbuilder(cols=1,margin_left='5px',margin_top='5px',lblclass='labels',border_spacing='1px')
        for name,value in callables:
            if name.startswith('get_') or name in ['document_root'] :
                try:
                    value=value()
                except:
                    value='err in call'
            else:
                value=value.__doc__
            fb.div('%s &nbsp' % value,lbl=name,_class='values')
            
    def externalUrl(self,path):
        siteroot=self.request.headers_in['Referer'].replace(self.request.filename.replace(self.request.hlist.directory,''),'')
        return os.path.join(siteroot,path)
        
    def absUrlNew(self,path=''):
        path=os.path.join(self.request.hlist.directory.replace(self.request.document_root(),''),path)
        return self.request.construct_url(path)
        
    def testPane(self,pane):
        fb=pane.formbuilder(cols=1,margin_left='5px',margin_top='5px',lblclass='labels',border_spacing='1px')
        fb.div(self.request.filename,lbl='self.request.filename',_class='values')
        fb.div(self.request.document_root(),lbl='self.request.document_root()',_class='values')
        fb.div(self.request.hlist.directory,lbl='directory',_class='values')
        rel_directory=self.request.hlist.directory.replace(self.request.document_root(),'')
        fb.div(rel_directory,lbl='rel_directory',_class='values')
        fb.div(self.request.construct_url(rel_directory),lbl='url(rel_directory)',_class='values')
        fb.div(self.siteUri,lbl='siteUri',_class='values')
        fb.div(self.request.construct_url(self.siteUri),lbl='url(self.siteUri)',_class='values')
        fb.div(self.absUrlNew(),lbl='absUrlNew',_class='values')
        fb.div(self.absUrlNew('pippo'),lbl='absUrlNew',_class='values')


        

#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()