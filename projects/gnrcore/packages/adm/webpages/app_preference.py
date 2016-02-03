#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.web.gnrwsgisite_proxy.gnrresourceloader import GnrMixinError
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
import os
import gzip
from StringIO import StringIO
import pickle


class GnrCustomWebPage(object):
    maintable = 'adm.preference'
    py_requires = """public:Public,preference:AppPref,foundation/tools,preference_shortcut_handler:ShortcutGrid"""

    def windowTitle(self):
        return '!!Preference panel'

    def mainLeftContent(self, parentBC, **kwargs):
        return

    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='pbl_dialog_center', **kwargs)

   #def onIniting(self, url_parts, request_kwargs):
   #    for pkgname in self.db.packages.keys():
   #        try:
   #            cl = self.site.loadResource(pkgname, 'preference:AppPref')
   #            self.mixin(cl)
   #        except GnrMixinError:
   #            pass
   #
    def main(self, rootBC, **kwargs):
        """APPLICATION PREFERENCE BUILDER"""
        self.controllers(rootBC)
        self.bottom(rootBC.contentPane(region='bottom', _class='dialog_bottom'))
        tc = rootBC.tabContainer(region='center', datapath='preference', formId='preference',margin='2px')
        for pkg in self.db.packages.values():
            permmissioncb = getattr(self, 'permission_%s' % pkg.name, None)
            auth = True
            if permmissioncb:
                auth = self.application.checkResourcePermission(permmissioncb(), self.userTags)
            panecb = getattr(self, 'prefpane_%s' % pkg.name, None)
            if panecb and auth:
                panecb(tc, title=pkg.name_full, datapath='.%s' % pkg.name, nodeId=pkg.name,
                        pkgId=pkg.name,_anchor=True,
                       sqlContextRoot='preference.%s' % pkg.name)

    def bottom(self, bottom):
        #bottom.a('!!Zoom',float='left',href='/adm/app_preference')
        bottom.button('!!Save', baseClass='bottom_btn', float='right', margin='1px',
                      action='var f=genro.formById("preference").save(true);')
        bottom.button('!!Cancel', baseClass='bottom_btn', float='right', margin='1px',
                      action='window.parent.genro.wdgById("mainpreference").close();')

    def controllers(self, pane):
        pane.data('form.canWrite', True)
        pane.dataController("genro.formById('preference').load()", _onStart=True)
        pane.dataRpc('dummy', 'savePreference', data='=preference', nodeId='preference_saver',
                     _onResult='genro.formById("preference").saved();window.parent.genro.wdgById("mainpreference").close();')
        pane.dataRpc('preference', 'loadPreference', nodeId='preference_loader',
                     _onResult='genro.formById("preference").loaded();')

    @struct_method
    def preferences_startupDataPane(self,pane,pkg=None,**kwargs):
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
        center.dataRpc('startup_tables.%s' %pkg,self.getStartupTables,pkg=pkg,
                    _onBuilt=True,**{'subscribe_%s_startupPreview_reload' %pkg:True})
        center.contentPane(region='top',_class='pbl_roundedGroupLabel').div('Startup tables')
        center.contentPane(region='center',overflow='hidden').quickGrid('^startup_tables.%s' %pkg)
        return fb

    @public_method
    def getStartupTables(self,pkg=None):
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


    def rpc_loadPreference(self, **kwargs):
        record = self.tblobj.loadPreference()
        return record['data']

    def rpc_savePreference(self, data, **kwargs):
        record = self.tblobj.loadPreference(for_update=True)
        record['data'] = data
        self.tblobj.savePreference(record)
        self.setInClientData('gnr.serverEvent.refreshNode', value='gnr.app_preference', filters='*',
                             fired=True, public=True)
