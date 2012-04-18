#-*- coding: UTF-8 -*-

#--------------------------------------------------------------------------
# package            : GenroPy web - see LICENSE for details
# module gnrhtmlpage : Genro Web structures implementation
# Copyright (c)      : 2004 - 2009 Softwell sas - Milano 
# Written by         : Giovanni Porcari, Michele Bertoldi
#                      Saverio Porcari, Francesco Porcari
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
from gnr.web.gnrwebpage import GnrWebPage
from soaplib.core.service import DefinitionBase
from soaplib.core._base import MethodContext
from soaplib.core.mime import collapse_swa
from soaplib.core.model.exception import Fault
from soaplib.core.model.primitive import string_encoding
from soaplib.core import Application
from lxml import etree


class GnrSoapApplication(Application):

    def get_service_class(self, method_name):
        """This call maps method names to the services that will handle them.

        Override this function to alter the method mappings. Just try not to get
        too crazy with regular expressions :)
        """
        return self.call_routes[method_name]

    def get_service(self, service, http_req_env=None):
        """The function that maps service classes to service instances.
        Overriding this function is useful in case e.g. you need to pass
        additional parameters to service constructors.
        """
        return service



class GnrSoapPage(GnrWebPage, DefinitionBase):
    
    __tns__ = 'xs'
    
    def __init__(self, *args, **kwargs):
        GnrWebPage.__init__(self, *args, **kwargs)
        
        
        
    def get_in_object(self, ctx, in_string, in_string_charset=None):
        in_object = None
        root, xmlids = self.soap_app.parse_xml_string(in_string, in_string_charset)

        try:
            in_object = self.soap_app.deserialize_soap(ctx, self.soap_app.IN_WRAPPER,
                                                                   root, xmlids)
        except Fault,e:
            if getattr(self, 'debug_soap',False):
                raise
            ctx.in_error = e

        return in_object

    def get_out_object(self, ctx, in_object):
        out_object = self.soap_app.process_request(ctx, in_object)

        if isinstance(out_object, Fault):
            ctx.out_error = out_object
        else:
            assert not isinstance(out_object, Exception)

        return out_object

    def get_out_string(self, ctx, out_object):
        out_xml = self.soap_app.serialize_soap(ctx, self.soap_app.OUT_WRAPPER, out_object)
        out_string = etree.tostring(out_xml, xml_declaration=True,
                    encoding=string_encoding)
        return out_string
    
    def on_out_string(self, out_string):
        return out_string

    def rootPage(self,*args, **kwargs):
        """Handle an incoming SOAP request or a non-SOAP WSDL query."""
        self.response.content_type = 'text/xml'
        if not self.request._request.body:
            return self.service_description()
        try:
            ctx = MethodContext()
            in_string = collapse_swa(self.request.content_type, self.request._request.body)
            in_obj = self.get_in_object(ctx, in_string, self.request._request.charset)
            out_obj = self.get_out_object(ctx, in_obj)
            out_string = self.get_out_string(ctx, out_obj)
            return self.on_out_string(out_string)
        except Exception, e:
            if getattr(self, 'debug_soap',False):
                raise
            self.response.status='500 Internal Server Error'
            fault = Fault(faultstring=str(e))
            resp = etree.tostring(fault, encoding=string_encoding)
            return resp
    def service_description(self):

        wsdl = self.soap_app.get_wsdl(self.request._request.host_url+self.request._request.path)
        return wsdl
        
    def _onBegin(self):
        DefinitionBase.__init__(self)
        self.soap_app = GnrSoapApplication([self],getattr(self,'app_tns','xs'), name=getattr(self,'app_name',None))
        self.soap_app.transport = 'http://schemas.xmlsoap.org/soap/http'
