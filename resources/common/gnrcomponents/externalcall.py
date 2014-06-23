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

from gnr.web.gnrbaseclasses import BaseComponent

class BaseRpc(BaseComponent):

    skip_connection = True

    def rootPage(self, *args, **kwargs):
        if 'pagetemplate' in kwargs:
            kwargs.pop('pagetemplate')
        if args:
            method = self.getPublicMethod('rpc',args[0])
            if not method:
                return self.rpc_error(*args, **kwargs)
            args = list(args)
            args.pop(0)
        else:
            method = self.rpc_index
        return method(*args, **kwargs)

    def validIpList(self):
        return None

    def rpc_index(self, *args, **kwargs):
        return 'Dummy rpc'

    def rpc_error(self, method, *args, **kwargs):
        return 'Not existing method %s' % method
