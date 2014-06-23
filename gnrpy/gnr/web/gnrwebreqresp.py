#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import gnr.web.gnrcookie as Cookie

cookie_types = {'marshal': Cookie.MarshalCookie,
                'simple': Cookie.Cookie}

class GnrWebRequest(object):
    def __init__(self, request):
        self._request = request
        
    def __getattr__(self, name):
        if name in self.__dict__:
            return getattr(self, name)
        else:
            return getattr(self._request, name)
            
    def _get_path_info(self):
        return self._request.path_info
        
    path_info = property(_get_path_info)
        
    def get_header(self, header, default=None):
        return self._request.headers.get(header, default)
        
    def _get_filename(self):
        return self._request.filename
        
    filename = property(_get_filename)
        
    def _get_hlist(self):
        return self._request.hlist
        
    hlist = property(_get_hlist)
        
    def _get_headers(self):
        return self._request.headers
        
    headers = property(_get_headers)
    headers_in = property(_get_headers)
        
    def construct_url(self, *args, **kwargs):
        return self._request.relative_url(*args, **kwargs)
        
    def _get_remote_addr(self):
        return self._request.remote_addr
        
    remote_addr = property(_get_remote_addr)
        
    def write(self, *args, **kwargs):
        return self._request.write(*args, **kwargs)
        
    def _get_canonical_filename(self):
        return self._request.canonical_filename
        
    canonical_filename = property(_get_canonical_filename)
        
    def _get_document_root(self):
        return self._request.document_root()
        
    document_root = property(_get_document_root)
        
    def newMarshalCookie(self, name, value, secret=None, **kw):
        return Cookie.MarshalCookie(name, value, secret=secret, **kw)
        
    def newCookie(self, name, value, **kw):
        return Cookie.Cookie(name, value, **kw)
        
    def get_cookie(self, cookieName, cookieType, secret=None, path=None):
        cookieType = cookie_types[cookieType]
        cookie = Cookie.get_cookie(self._request, cookieName, cookieType, secret=secret)
        if type(cookie) is not cookieType:
            cookie = None
        if cookie is None and path:
            cookie = cookieType(cookieName, '', secret=secret)
            cookie.path = path
        return cookie
        
class GnrWebResponse(object):
    def __init__(self, response):
        self._response = response
        
    def __getattr__(self, name):
        if name in self.__dict__:
            return getattr(self, name)
        else:
            return getattr(self._response, name)
            
    def add_cookie(self, cookie):
        Cookie.add_cookie(self._response, cookie)
        
    def add_header(self, header, value):
        self._response.headers[header] = value
        
    def _get_content_type(self):
        return self._response.content_type
        
    def _set_content_type(self, value):
        self._response.content_type = value
        
    content_type = property(_get_content_type, _set_content_type)
        
    def write(self, *args, **kwargs):
        return self._response.write(*args, **kwargs)