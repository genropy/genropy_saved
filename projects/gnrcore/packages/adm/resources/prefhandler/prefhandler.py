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
Component for preference handling:
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method




class AppPrefHandler(BaseComponent):
    py_requires='preference:AppPref,foundation/tools'

    @struct_method
    def ph_appPreferencesTabs(self,parent,packages='*',datapath=None,context_dbstore=None,**kwargs):
        if isinstance(packages,basestring):
            packages = self.application.packages.keys() if packages == '*' else packages.split(',')
        tc = parent.tabContainer(datapath=datapath,context_dbstore=context_dbstore,**kwargs)
        for pkgId in packages:
            pkg = self.application.packages[pkgId]
            if pkg.disabled:
                continue
            permmissioncb = getattr(self, 'permission_%s' % pkg.id, None)
            auth = True
            if permmissioncb:
                auth = self.application.checkResourcePermission(permmissioncb(), self.userTags)
            panecb = getattr(self, 'prefpane_%s' % pkg.id, None)
            if panecb and auth:
                panecb(tc, title=pkg.attributes.get('name_full'), datapath='.%s' % pkg.id, nodeId=pkg.id,
                        pkgId=pkg.id,_anchor=True,sqlContextRoot='%s.%s' % (datapath,pkg.id))
        if context_dbstore:
            tc.dataRpc(None,self.ph_updatePrefCache,formsubscribe_onSaved=True,prefdbstore=context_dbstore)
    
    @public_method
    def ph_updatePrefCache(self,prefdbstore=None,**kwargs):
        self.db.application.cache.updatedItem( '_storepref_%s' %prefdbstore)
    
        