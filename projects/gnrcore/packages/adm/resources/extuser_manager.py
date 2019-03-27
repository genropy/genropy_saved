# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method

class ExternalUsers(BaseComponent):

    @struct_method
    def ue_externalUsers(self,parent,default_email=None,default_group_code=None,**kwargs):
        parent.contentPane(**kwargs).remote(self.ue_remoteExternalUsers,default_email=default_email,default_group_code=default_group_code)
    
    @public_method
    def ue_remoteExternalUsers(self,pane,title=None,default_email=None,default_group_code=None,**kwargs):
        th = pane.dialogTableHandler(relation='@external_users',dialog_height='400px',
                                dialog_width='650px',
                                formInIframe='/adm/user_page',
                                default_email=default_email,
                                default_group_code=default_group_code,
                                view_store__onBuilt=True)
 