# -*- coding: UTF-8 -*-
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

"""
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent

class RemoteBuilder(BaseComponent):
    def buildRemote(self,pane,method,lazy,**kwargs):    
        handler = getattr(self,'remote_%s' %method,None)
        if handler:
            parentAttr = pane.parentNode.getAttr()
            parentAttr['remote'] = 'remoteBuilder'
            parentAttr['remote_handler'] = method
            for k,v in kwargs.items():
                parentAttr['remote_%s' %k] = v
                kwargs.pop(k)
            if not lazy:
                handler(pane,**kwargs)
            
    def ajaxContent(self,pane,method,**kwargs):
        self.buildRemote(method,pane,False,**kwargs)
        
    def lazyContent(self,pane,method,**kwargs):
        self.buildRemote(pane,method,True,**kwargs)
        
    def rpc_remoteBuilder(self,handler=None,**kwargs):
        handler = getattr(self,'remote_%s' %handler,None)
        if handler:
            pane = self.newSourceRoot()
            handler(pane,**kwargs)
            return pane