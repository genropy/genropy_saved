#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#



from gnr.web.gnrbaseclasses import BaseComponent

class PreferenceHandler(BaseComponent):
    py_requires='public:Public'
    maintable='adm.preference'
    
    def main(self,root,**kwargs):
        root.dataRpc('preferences','loadPreferences',_onStart=True)
        root.dataRpc('dummy','savePreferences',data='=preferences',_fired='^save',
                     _onResult='FIRE pbl.bottomMsg="Preferences Saved"')
        
        mainbc, top, bottom = self.pbl_rootBorderContainer(root, '!!Preference',datapath='preferences',
                                                        _class='pbl_roundedGroup',margin='5px')    
        header = mainbc.contentPane(region='top',_class='pbl_roundedGroupLabel')
        header.div('!!Preferences')
        footer = mainbc.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
        footer.button('!!Save',float='right',fire='save')
        self.preference_form(mainbc.borderContainer(region='center',margin='5px',
                             datapath='.data'))
        
    def rpc_loadPreferences(self):
        return self.package.getPreferences(autocreate=True)
    
    def rpc_savePreferences(self,data):
        self.package.setPreferences(data)
        self.db.commit()