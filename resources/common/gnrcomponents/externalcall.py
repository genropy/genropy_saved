# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
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

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebpage import GnrUserNotAllowed,GnrBasicAuthenticationError

from gnr.core.gnrbag import Bag
from dateutil import parser as dtparser
import datetime
from decimal import Decimal
from gnr.core.gnrdecorator import public_method
from xmlrpclib import dumps as xmlrpcdumps,loads as xmlrpcloads, Marshaller, Fault
from gnr.core.gnrbag import TraceBackResolver

def dump_decimal(self,value, write):
    write("<value><double>")
    write(str(value))
    write("</double></value>\n")

def dump_date(self,value, write):
    write("<value><dateTime.iso8601>")
    write(value.isoformat())
    write("</dateTime.iso8601></value>\n")

Marshaller.dispatch[Decimal] = dump_decimal
Marshaller.dispatch[datetime.date] = dump_date

class BaseRpc(BaseComponent):

    skip_connection = True

 #def rootPageNew(self,*args, **kwargs):
 #    self.response.content_type = 'application/xml'
 #    request_method = self.request.method
 #    if args:
 #        method_name = '%s_%s'%(request_method.upper(),args[0])
 #        method = getattr(self,method_name,self._default)
 #        args = args[1:]
 #    else:
 #        method = self._default
 #    result = method(*args, **kwargs)
 #    if isinstance(result, Bag):
 #        result = result.toXml()
 #    return result

    def rootPage(self, *args, **kwargs):
        #request_method = self.request.method
        if 'pagetemplate' in kwargs:
            kwargs.pop('pagetemplate')
        if args:
            try:
                method = self.getPublicMethod('rpc',args[0])
            except (GnrUserNotAllowed, GnrBasicAuthenticationError) as err:
                return Bag(dict(error=str(err))).toXml()
            if not method:
                return self.rpc_error(*args, **kwargs)
            args = list(args)
            args.pop(0)
        else:
            method = self.rpc_index
        result = method(*args, **kwargs)
        return self.catalog.asTypedText(result)

    def validIpList(self):
        return None

    def rpc_index(self, *args, **kwargs):
        return 'Dummy rpc'

    def rpc_error(self, method, *args, **kwargs):
        return 'Not existing method %s' % method

class NetBagRpc(BaseComponent):

    skip_connection = True

    def rootPage(self, *args, **kwargs):
        self.response.content_type = 'application/xml'
        if 'pagetemplate' in kwargs:
            kwargs.pop('pagetemplate')
        if args:
            try:
                method = self.getPublicMethod('rpc','netbag_%s' %args[0])
            except (GnrUserNotAllowed, GnrBasicAuthenticationError) as err:
                return Bag(dict(error=str(err))).toXml()
            if not method:
                return self.rpc_error(*args, **kwargs)
            args = list(args)
            args.pop(0)
        else:
            method = self.rpc_index
        try:
            result = method(*args, **kwargs)
        except Exception,e:
            #import traceback
            #result = Bag(dict(error=traceback.format_exc().encode('utf8')))
            result = Bag(dict(error=TraceBackResolver()))
        if not isinstance(result,Bag):
            result = Bag(dict(result=result))
        return result.toXml(unresolved=True)

    def validIpList(self):
        return None

    def rpc_index(self, *args, **kwargs):
        return 'Dummy rpc'

    def rpc_error(self, method, *args, **kwargs):
        return 'Not existing method %s' % method

    def selectionToNetBag(self,selection=None,mode=None,_removeNullAttributes=False):
        mode = mode or 'a'
        result = Bag()
        for i,r in enumerate(selection.output('dictlist')):
            label = 'r_%s' %i
            r = dict(r)
            if mode=='v':
                result.setItem(label,Bag(r))
            elif mode=='a':
                result.setItem(label,None,_attributes=r,_removeNullAttributes=_removeNullAttributes)
            elif mode=='r':
                pass
        return result


class XmlRpc(BaseComponent):
    skip_connection = True
    def rootPage(self, *args, **kwargs):
        args,method = xmlrpcloads(self.request.body,use_datetime=True)
        if not method:
            return self.returnFault(-1,'Missing methodName')
        method=method.replace('.','_')
        try:
            handler = self.getPublicMethod('rpc',method)
        except GnrBasicAuthenticationError, e:
            return self.returnFault(-2,str(e))
        except GnrUserNotAllowed,e:
            return self.returnFault(-2,'User not allowed for method %s' %method)
        except Exception,e:
            return self.returnFault(-2,str(e))
        if not handler:
            return self.returnFault(-2,'Not existing method:%s' % method)
        try:
            kwargs = dict()
            args = list(args)
            if args and isinstance(args[-1],dict):
                kwargs = args.pop()
            result = handler(*args, **kwargs)
            xmlRpcResult = xmlrpcdumps((result,),encoding='UTF-8',methodresponse=True,allow_none=True)
            return xmlRpcResult
        except Exception,e:
            import sys,os
            tb = sys.exc_info()[2]
            while tb is not None :
                f = tb.tb_frame
                lineno = tb.tb_lineno
                tb = tb.tb_next
            co = f.f_code
            filename = co.co_filename
            module=os.path.basename(os.path.splitext(filename)[0])
            funcname = co.co_name
            faultString="""Error in module '%s' calling method '%s' at line %i : %s""" %(module,funcname,lineno,str(e))
            return self.returnFault(1,faultString)

    def returnFault(self,faultCode=0,faultString=''):
        return xmlrpcdumps(Fault(faultCode,faultString),encoding='UTF-8',methodresponse=True,allow_none=True)

    def isPublicMethod(self,name):
        h=getattr(self,name,None)
        if not h:
            return
        f=getattr(h,'im_func',None)
        return (f and f.__module__==self.__module__)
        
    @public_method
    def system_listMethods(self):
        result=[]
        for name in dir(self):
            if self.isPublicMethod(name):
                result.append(name)
        return result
        
    @public_method
    def system_methodSignature(self,methodName):
        try :
            from funcsigs import signature
        except:
            return self.returnFault(-10,'You have to install funcsigs to get method signature')
        if not self.isPublicMethod(methodName):
            return self.returnFault(-5,'Not Existing Method: %s' % methodName)
        h=getattr(self,methodName)
        sig = signature(h).parameters
        return sig
        
    @public_method
    def system_methodHelp(self,methodName):
        if not self.isPublicMethod(methodName):
            return self.returnFault(-5,'Not Existing Method: %s' % methodName)
        h=getattr(self,methodName)
        return h.__doc__

