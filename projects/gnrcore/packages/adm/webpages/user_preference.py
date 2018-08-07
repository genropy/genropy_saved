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
    maintable = 'adm.user'
    py_requires = """public:Public,prefhandler/prefhandler:UserPrefHandler"""

    def windowTitle(self):
        return '!!User preference panel'

    def main(self, root, **kwargs):
        """USER PREFERENCE BUILDER"""
        form = root.frameForm(frameCode='user_preferences',store_startKey=self.avatar.user_id,
                                table='adm.user',datapath='main',store=True,**kwargs)
        self.controllers(form)
        self.user_preference_bottom_bar(form.bottom)
        form.dataController("""
            var tkw = _triggerpars.kw;
            if(tkw.reason && tkw.reason.attr && tkw.reason.attr.livePreference){
                genro.mainGenroWindow.genro.publish({topic:'externalSetData',
                iframe:'*'},{path:'gnr.user_preference.'+tkw.pathlist.slice(2).join('.'),value:tkw.value});
            }""",preference='^#FORM.record.preferences')
        form.center.userPreferencesTabs(datapath='#FORM.record.preferences',margin='2px')

    def user_preference_bottom_bar(self, bottom):
        bar = bottom.slotBar('revertbtn,*,cancel,savebtn',margin_bottom='2px',_class='slotbar_dialog_footer')
        #bottom.a('!!Zoom',float='left',href='/adm/app_preference')
        bar.revertbtn.button('!!Revert',action='this.form.publish("reload")',disabled='^.controller.changed?=!#v')
        bar.savebtn.slotButton('!!Save', action='this.form.publish("save",{destPkey:"*dismiss*"});')
        bar.cancel.slotButton('!!Cancel', action='this.form.abort()')

    def controllers(self, form):
        form.dataController('window.parent.genro.wdgById("userpreference").close();',
                                formsubscribe_onDismissed=True)
