#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
""" GnrDojo : Show request object """

from gnr.web.gnrwebcore import GnrWebPage

#-------  configure: customize this configuration ------
class GnrCustomWebPage(object):
    
    def main(self, root, **kwargs):
        client = self.rootLayoutContainer(root,padding='5px')
        lc = client.layoutContainer(height='100%')
        pane=lc.contentPane(layoutAlign='bottom',background_color='silver', height='1em')
        req=self.request
        requestData=[]
        for name in dir(req):
            value=getattr(req, name)
            requestData.append(self.rowCompose(name,value))
        xx=len(req.filename.replace(req.hlist.directory,'').split('/'))-1
        requestData.append({'Id':'usrreq','type':'hh','value':xx*'../'})
        
        pane=lc.contentPane(layoutAlign='client',background_color='#84a3d1', height='100%')
        if True:
            reqTable = pane.filteringTable(alternateRows='true',rows=self.toJson(requestData),
                                           maxSelect='0', _class='dojo')
            reqTable.column('Key',field='Id') 
            reqTable.column('Type')
            reqTable.column('Value')


    def rowCompose(self, name,value):
        row={'Id':name}
        if callable(value):
            row['type']='callable'
            value=value.__doc__
            if not value:
                value='no doc'
            row['value']=value.strip()
        elif isinstance(value,basestring):
            row['type']='string'
            row['value']=value.strip()
        elif hasattr(value,'keys'):
            row['type']='keyed'
            if len(value)==0:
                row['value']=str(value)
            else:
                inner=[]
                for k,v in value.items():
                    inner.append('%s = %s' % (k,str(v)))
                row['value']='\n'.join(inner)
        else:
            if hasattr(value,'__class__'):
                row['type']= value.__class__.__name__
            else:
                row['type']= 'unknown'
            row['value']=str(value)
        return row
        
#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()