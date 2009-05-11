#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='develop.staff'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Staff management'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'staff'
        
    def tableWriteTags(self):
        return 'staff'
        
    def tableDeleteTags(self):
        return 'staff'
        
    def barTitle(self):
        return '!!Staff'
        
    def columnsBase(self,):
        return """fullname,username,email,phone,role"""
                  
    def orderBase(self):
        return 'username'

    def queryBase(self):
        return dict(column='fullname',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(_class='pbl_roundedGroup',margin='5px',**kwargs)
        fb = pane.formbuilder(cols=2, border_spacing='6px',disabled=disabled)
        fb.field('develop.staff.@user_id',auxColumns='@user_id.firstname,@user_id.lastname',
                 validate_onAccept=""" var tags = GET .@user_id.auth_tags;
                                       tags = tags.split(',');
                                       if (!arrayContains(tags,'staff')){
                                            tags.push('staff');
                                            SET .@user_id.auth_tags = tags.join(',');
                                       }""")
        fb.div(innerHTML='==dataTemplate(tpl, dbag);',
                tpl='$firstname $lastname <br/> $email',
                dbag='^.@user_id',_class='infoBox')
        fb.field('develop.staff.role')
        fb.field('develop.staff.phone')

############################## RPC_METHODS ###################################       

# --------------------------- GnrWebPage Standard footer ---------------------------
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
        