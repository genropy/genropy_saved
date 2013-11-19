#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.web.gnrwsgisite_proxy.gnrresourceloader import GnrMixinError

class GnrCustomWebPage(object):
    maintable = 'adm.preference'
    py_requires = """public:Public,preference:AppPref,foundation/includedview,foundation/dialogs,
                   foundation/tools,foundation/macrowidgets:RichTextEditor"""

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

    def rpc_loadPreference(self, **kwargs):
        record = self.tblobj.loadPreference()
        return record['data']

    def rpc_savePreference(self, data, **kwargs):
        record = self.tblobj.loadPreference(for_update=True)
        record['data'] = data
        self.tblobj.savePreference(record)
        self.setInClientData('gnr.serverEvent.refreshNode', value='gnr.app_preference', filters='*',
                             fired=True, public=True)
