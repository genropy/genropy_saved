#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

class GnrCustomWebPage(object):
    maintable = 'adm.preference'
    py_requires = """public:Public,prefhandler/prefhandler:AppPrefHandler"""

    def windowTitle(self):
        return '!!Preference panel'

    def main(self, root, **kwargs):
        """APPLICATION PREFERENCE BUILDER"""
        form = root.frameForm(frameCode='app_preferences',store_startKey='_mainpref_',
                                table=self.maintable,datapath='main',store=True,**kwargs)
        self.controllers(form)
        self.app_preference_bottom_bar(form.bottom)
        form.dataController("""
            var tkw = _triggerpars.kw;
            if(tkw.reason && tkw.reason.attr && tkw.reason.attr.livePreference){
                genro.mainGenroWindow.genro.publish({topic:'externalSetData',
                iframe:'*'},{path:'gnr.app_preference.'+tkw.pathlist.slice(4).join('.'),value:tkw.value});
            }""",preference='^#FORM.record.data')
        form.center.appPreferencesTabs(datapath='#FORM.record.data',margin='2px')

    def app_preference_bottom_bar(self, bottom):
        bar = bottom.slotBar('revertbtn,*,cancel,savebtn',margin_bottom='2px',_class='slotbar_dialog_footer')
        #bottom.a('!!Zoom',float='left',href='/adm/app_preference')
        bar.revertbtn.button('!!Revert',action='this.form.publish("reload")',disabled='^.controller.changed?=!#v')
        bar.savebtn.slotButton('!!Save', action='this.form.publish("save",{destPkey:"*dismiss*",always:true});')
        bar.cancel.slotButton('!!Cancel', action='this.form.abort()')

    def controllers(self, form):
        form.dataController('window.parent.genro.wdgById("mainpreference").close();',
                                formsubscribe_onDismissed=True)

