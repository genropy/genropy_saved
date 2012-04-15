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
from rpclib.service import ServiceBase
from rpclib._base import MethodContext
from rpclib.protocol.soap.mime import collapse_swa
from rpclib.protocol.soap.soap11 import Soap11
from rpclib.interface.wsdl.wsdl11 import Wsdl11
from rpclib.model.fault import Fault
from rpclib.model.primitive import string_encoding
from rpclib.application import Application
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



class GnrSoapPage(GnrWebPage, ServiceBase):
    __name__ = 'GnrSoapApplication'

    def __init__(self, *args, **kwargs):
        GnrWebPage.__init__(self, *args, **kwargs)
        
        
        
    def get_in_object(self, ctx, in_string, in_string_charset=None):
        in_object = None
        root, xmlids = self.soap_app.parse_xml_string(in_string, in_string_charset)

        if True:
            in_object = self.soap_app.deserialize_soap(ctx, self.soap_app.IN_WRAPPER,
                                                                   root, xmlids)
        else:

        #except Fault,e:
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
    
    def rootPage(self,*args, **kwargs):
        """Handle an incoming SOAP request or a non-SOAP WSDL query."""
        self.response.content_type = 'text/xml'
        if not self.request._request.body:
            return self.service_description()
        if True:
            ctx = MethodContext()
            in_string = collapse_swa(self.request.content_type, self.request._request.body)
            in_obj = self.get_in_object(ctx, in_string, self.request._request.charset)
            out_obj = self.get_out_object(ctx, in_obj)
            out_string = self.get_out_string(ctx, out_obj)
            return out_string
        else:
        #except Exception, e:
            if getattr(self, 'debug_soap',False):
                raise
            self.response.status='500 Internal Server Error'
            fault = Fault(faultstring=str(e))
            resp = etree.tostring(fault, encoding=string_encoding)
            return resp
    def service_description(self):

        #wsdl = self.soap_app.get_wsdl(self.request._request.host_url+self.request._request.path)
        self.soap_app.interface.build_interface_document(self.request._request.host_url+self.request._request.path)
        wsdl = self.soap_app.interface.get_interface_document()
        return wsdl
        
    def _onBegin(self):
        ServiceBase.__init__(self)
        for k in dir(self):
            v = getattr(self,k)
            if hasattr(v, '_is_rpc'):
                # these three lines are needed for staticmethod wrapping to work
                descriptor = v(_default_function_name=k)
                setattr(self, k, staticmethod(descriptor.function))
                descriptor.reset_function(getattr(self, k))
                self.public_methods[k] = descriptor
                #self.public_methods[k] = v
        self.soap_app = GnrSoapApplication([self],getattr(self,'app_tns','gnr.soap.application'),Soap11(),Soap11(), name=getattr(self,'app_name',None))
        self.soap_app.transport = 'http://schemas.xmlsoap.org/soap/http'
