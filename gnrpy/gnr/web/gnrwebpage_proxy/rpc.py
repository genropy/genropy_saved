#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  rpc.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag,BagNode
from gnr.core import gnrstring
from gnr.core.gnrdict import dictExtract
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrlang import GnrException
from time import time
import os
import base64
import mimetypes
import re



AUTH_FORBIDDEN = -1
AUTH_EXPIRED = 2
AUTH_NOT_LOGGED = 1

class GnrWebRpc(GnrBaseProxy):
    def __call__(self, method=None, _auth=AUTH_FORBIDDEN,**kwargs):
        page = self.page
        if _auth == AUTH_FORBIDDEN and method != 'main':
            result = None
            error = 'forbidden call'
        elif _auth == AUTH_EXPIRED:
            result = None
            error = 'expired'
        else:
            handler = page.getPublicMethod('rpc', method)
            if method == 'main':
                kwargs['_auth'] = _auth
            if handler:
                result = handler(**kwargs)
                error = None
            else:
                result = None
                error = 'missing handler: %s' % method
        if error:
            self.error = error
        return result

    def result_bag(self, result):
        error = getattr(self, 'error', None)
        page = self.page
        envelope = Bag()
        resultAttrs = {}
        if isinstance(result, BagNode):
            envelope['resultType'] = 'node'
            resultAttrs = result.attr
            result = result.getValue()
        if isinstance(result, tuple):
            resultAttrs = result[1]
            if len(result) == 3 and isinstance(result[2], Bag):
                page.setInClientData(result[2])
            result = result[0]
            if resultAttrs is not None:
                envelope['resultType'] = 'node'
        if error:
            envelope['error'] = error
        if isinstance(result, page.domSrcFactory):
            resultAttrs['__cls'] = 'domsource'
            self.checkNotAllowed(result)
        if page.isLocalizer():
            envelope['_localizerStatus'] = '*_localizerStatus*'
        for k in dir(page):
            if k.startswith('envelope_'):
                v = getattr(page,k)
                if v is not None:
                    envelope.setItem(k[9:],v)
        envelope.setItem('result', result, _attributes=resultAttrs)
        if not getattr(page,'_closed',False):
            dataChanges = self.page.collectClientDatachanges()
            if dataChanges:
                envelope.setItem('dataChanges', dataChanges)
        page.response.content_type = "text/xml"
        t0 = time()
        xmlresult = envelope.toXml(unresolved=True,
                                   translate_cb=page.localize, omitUnknownTypes=True,
                                   catalog=page.catalog)
        page.xml_deltatime = int((time()-t0)*1000)
        page.xml_size = len(xmlresult)
        return xmlresult

    def checkNotAllowed(self,src):
        node = True
        while node:
            node = src.getNodeByAttr('_notallowed',True)
            if node:
                if self.page.isGuest:
                    raise GnrException('!!User connection lost.')
                node.parentbag.popNode(node.label)


    def result_xml(self, result):
        self.page.response.content_type = "text/xml"
        if isinstance(result, Bag):
            return result.toXml(unresolved=True, omitUnknownTypes=True)
        return result

    def result_json(self, result):
        error = getattr(self, 'error', None)
        page = self.page
        if not error:
            return page.catalog.toJson(result)
        else:
            return page.catalog.toJson({'error': error})

    def result_text(self, result):
        error = getattr(self, 'error', None)
        return result or error

    def result_html(self, page, result, error):
        error = getattr(self, 'error', None)
        page = self.page
        page.response.content_type = "text/html"
        return result or error

    def rpc_upload_file(self, *args ,**kwargs):
        onUploadingMethod= kwargs.get('onUploadingMethod')
        if onUploadingMethod:
            onUploading = self.page.getPublicMethod('rpc', onUploadingMethod)
            onUploading(kwargs)
        file_handle = kwargs.get('file_handle')
        dataUrl = kwargs.get('dataUrl')
        uploadPath = kwargs.get('uploadPath')
        uploaderId = kwargs.get('uploaderId')
        onUploadedMethod = kwargs.get('onUploadedMethod')
        filename = kwargs.get('filename')
        site = self.page.site
        #kwargs = site.parse_kwargs(kwargs) it's provided by gnrwsgisite
        file_actions = dictExtract(kwargs, 'process_') or {}
        if not uploadPath:
            uploadPath = 'home:uploaded_files'
            if uploaderId:
                uploadPath = '%s/%s' % (uploadPath, uploaderId)
        if uploadPath is None:
            return
        file_path,file_url = site.uploadFile(file_handle=file_handle,dataUrl=dataUrl,
                                            filename=filename,uploadPath=uploadPath)
        if not file_path:
            return
        file_ext = os.path.splitext(file_path)
        action_results = dict()
        for action_name, action_params in file_actions.items():
            if action_params == True:
                action_params = getattr(self.page, 'process_%s' % action_name)()
            command_name = action_params.pop('fileaction', None)
            if not command_name:
                continue
            action_runner = getattr(self.page, 'fileaction_%s' % command_name)
            if action_runner:
                for action_param in action_params:
                    action_params[str(action_param)] = action_params.pop(action_param)
                action_results[action_name] = action_runner(file_url=file_url, file_path=file_path, file_ext=file_ext,
                                                            action_name=action_name, **action_params)
        if onUploadedMethod:
            handler = self.page.getPublicMethod('rpc', onUploadedMethod)
            if handler:
                #file_node = self.page.site.storage(file_path, autocreate=-1)
                #with file_node.local_path(mode='r') as local_path:
                #    result =handler(file_url=local_path, file_path=file_path, file_ext=file_ext,
                #           action_results=action_results,
                #               **kwargs)
                #return result
                return handler(file_url=file_url, file_path=file_path, file_ext=file_ext, action_results=action_results,
                               **kwargs)
        elif uploaderId:
            handler = getattr(self.page, 'onUploading_%s' % uploaderId,None)
            if handler:
                print 'deprecated use onUploaded_%s as name' %uploaderId
            else:
                handler = getattr(self.page, 'onUploaded_%s' % uploaderId,None)
            if handler:
                return handler(file_url=file_url, file_path=file_path, file_ext=file_ext, action_results=action_results,
                               **kwargs)
        return file_url

