#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
AUTH_FORBIDDEN=-1

class GnrWebRpc(GnrBaseProxy):    
    def __call__(self, method=None, _auth=AUTH_FORBIDDEN, **kwargs):
        page = self.page
        if _auth==AUTH_FORBIDDEN and method!='main':
            result = None
            error = 'forbidden call'
        elif _auth=='EXPIRED':
            result=None
            error='expired'
        else:
            handler=page.getPublicMethod('rpc', method)
            if method=='main':
                kwargs['_auth'] = _auth
            if handler:
                if page.debug_mode:
                    result = handler(**kwargs)
                    error=None
                else:
                    if True:
#                    try:
                        result = handler(**kwargs)
                        error = None
#                    except GnrWebClientError, err:
#                        result = err.args[0]
#                        error = 'clientError'
#                    except Exception, err:
#                        raise err
#                        result = page._errorPage(err,method,kwargs)
#                        mode='bag'
#                        error = 'serverError'

            else:
                result = None
                error = 'missing handler:%s' % method
        return result
    
    def result_bag(self, result):
        error = getattr(self,'error',None)
        page = self.page
        envelope=Bag()
        resultAttrs={}
        if isinstance(result,tuple):
            resultAttrs=result[1]
            if len(result)==3 and isinstance(result[2],Bag):
                self.page.setLocalClientDataChanges(result[2])
            result=result[0]
            if resultAttrs is not None:
                envelope['resultType'] = 'node'
        if error:
            envelope['error'] = error
        if isinstance(result, page.domSrcFactory):
            resultAttrs['__cls']='domsource'
        if page.isLocalizer():
            envelope['_localizerStatus']='*_localizerStatus*'
        envelope.setItem('result', result, _attributes=resultAttrs)
        dataChanges = self.page.collectClientDataChanges()      
        if dataChanges :
            envelope.setItem('dataChanges', dataChanges)
        page.response.content_type = "text/xml"
        xmlresult= envelope.toXml(unresolved=True, jsonmode=True, jsonkey=page.page_id, 
                              translate_cb=page.localizer.translateText, omitUnknownTypes=True, catalog=page.catalog)
        if page.isLocalizer():
            xmlresult=xmlresult.replace('*_localizerStatus*', page.localizer.status)
            
        return xmlresult

    def result_json(self,  result):
        error = getattr(self,'error',None)
        page = self.page
        if not error:
            return page.catalog.toJson(result)
        else:
            return page.catalog.toJson({'error':error})
        
    def result_text(self, result):
        error = getattr(self,'error',None)
        return result or error
    
    def result_html(self, page, result, error):
        error = getattr(self,'error',None)
        page = self.page
        page.response.content_type = "text/html"
        return result or error

