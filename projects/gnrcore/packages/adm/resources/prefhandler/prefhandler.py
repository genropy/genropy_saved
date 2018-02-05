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

import os
import gzip
from StringIO import StringIO
import pickle

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method




class AppPrefHandler(BaseComponent):
    py_requires='preference:AppPref,foundation/tools'

    @struct_method
    def ph_appPreferencesTabs(self,parent,packages='*',datapath=None,**kwargs):
        if isinstance(packages,basestring):
            packages = self.application.packages.keys() if packages == '*' else packages.split(',')
        tc = parent.tabContainer(datapath=datapath,**kwargs)
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

    @struct_method
    def ph_startupDataPane(self,pane,pkg=None,**kwargs):
        bc = pane.borderContainer(_lazyBuild=True,**kwargs)
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=5,border_spacing='3px')
        fb.button('!!Build Startup Data',action="""genro.mainGenroWindow.genro.publish('open_batch');
                                                    genro.serverCall('_package.%s.createStartupData',null,function(){});
                                                    """ %pkg)
        fb.button('!!Load Startup Data',action="""genro.mainGenroWindow.genro.publish('open_batch');
                                                    genro.serverCall('_package.%s.loadStartupData',{empty_before:empty_before},function(){});
                                                    """ %pkg,empty_before=True,
                                                    ask=dict(title='Delete table contents',fields=[dict(name='empty_before',
                                                                                                            label='Delete tables before import',
                                                                                                            wdg='checkbox')]))
        fb.button('!!Refresh preview',action='PUBLISH %s_startupPreview_reload' %pkg)
        center = bc.borderContainer(region='center',_class='pbl_roundedGroup',margin='2px')
        center.dataRpc('#FORM.startup_tables.%s' %pkg,self.ph_getStartupTables,pkg=pkg,
                    _onBuilt=True,**{'subscribe_%s_startupPreview_reload' %pkg:True})
        center.contentPane(region='top',_class='pbl_roundedGroupLabel').div('Startup tables')
        center.contentPane(region='center',overflow='hidden').quickGrid('^#FORM.startup_tables.%s' %pkg)
        return fb

    @public_method
    def ph_getStartupTables(self,pkg=None):
        bagpath = os.path.join(self.db.application.packages[pkg].packageFolder,'startup_data')
        data = None
        if not os.path.isfile('%s.pik' %bagpath):
            if not os.path.exists('%s.gz' %bagpath):

                return
            with gzip.open('%s.gz' %bagpath,'rb') as gzfile:
                pk = StringIO(gzfile.read())
                data = pickle.load(pk)
        else:
            data = Bag('%s.pik' %bagpath)
        result = Bag()
        for i,t in enumerate(data['tables']):
            row = Bag()
            row['table'] = t
            row['count'] = len(data[t])
            result['r_%s' %i] = row
        return result        
