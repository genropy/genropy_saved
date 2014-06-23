#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.web.gnrwsgisite_proxy.gnrresourceloader import GnrMixinError
from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    """USER PREFERENCE BUILDER"""
    maintable = 'adm.preference'
    py_requires = """public:Public,preference:UserPref"""

    def windowTitle(self):
        return '!!Preference panel'

    def mainLeftContent(self, parentBC, **kwargs):
        return

    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='pbl_dialog_center', **kwargs)

    def main(self, rootBC, **kwargs):
        self.controllers(rootBC)
        self.bottom(rootBC.contentPane(region='bottom', _class='dialog_bottom'))
       #rootBC.dataController("""genro.bp();
       #                        //genro.publish({iframe:'*',topic:'changed_user_preference'},{preference:_node.label,});""",preference="^preference")
        tc = rootBC.tabContainer(region='center', datapath='preference', formId='preference')
        for pkg in self.db.packages.values():
            panecb = getattr(self, 'prefpane_%s' % pkg.name, None)
            if panecb:
                panecb(tc, title=pkg.name_full, datapath='.%s' % pkg.name, nodeId=pkg.name)

    def bottom(self, bottom):
        bottom.button('!!Save', baseClass='bottom_btn', float='right', margin='1px',
                        margin_right='20px',
                      action='genro.formById("preference").save(true)')
        bottom.button('!!Cancel', baseClass='bottom_btn', float='right', margin='1px',
                      action='window.parent.genro.wdgById("userpreference").hide();')

    def controllers(self, pane):
        pane.dataController("""parent.genro.fireEvent("#userpreference.close");""", _fired="^frame.close")
        pane.dataController("genro.formById('preference').load()", _onStart=True)
        pane.dataRpc('dummy', 'savePreference', data='=preference', nodeId='preference_saver',
                     _onResult='genro.formById("preference").saved();FIRE frame.setOnParent;window.parent.genro.wdgById("userpreference").hide();')
        pane.dataRpc('preference', 'loadPreference', nodeId='preference_loader',
                     _onResult='genro.formById("preference").loaded();')

    def rpc_loadPreference(self):
        return self.getUserPreference('*')

    def rpc_savePreference(self, data):
        self.db.table('adm.user').setPreference(username=self.user, data=data)
        self.setInClientData('gnr.serverEvent.refreshNode', value='gnr.user_preference', filters='user:%s' % self.user,
                             fired=True, public=True)

        return
 