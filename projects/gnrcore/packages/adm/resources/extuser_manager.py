# -*- coding: utf-8 -*-
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method

class ExternalUsers(BaseComponent):
    @struct_method
    def ue_externalUsers(self,parent,default_email=None,
                        default_group_code=None,default_tags=None,**kwargs):
        parent.contentPane(datapath='#FORM',**kwargs).remote(self.ue_remoteExternalUsers,
                                            default_email=default_email,
                                            default_group_code=default_group_code,
                                            default_tags=default_tags)

    @public_method
    def ue_remoteExternalUsers(self,pane,title=None,default_email=None,
                                default_group_code=None,default_tags=None,**kwargs):
        pane.dialogTableHandler(relation='@external_users',margin='2px',pbl_classes=True,
                                default_email=default_email,
                                default_status='conf',
                                formResource='ExtUserForm',
                                viewResource='ExtUserView',
                                default_group_code=default_group_code,
                                default_tags=default_tags,
                                configurable=False,
                                view_store__onBuilt=True)
 