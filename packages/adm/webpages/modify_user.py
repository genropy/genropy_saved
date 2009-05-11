#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Francesco Cavazzana on 2008-02-12.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" modify_user """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'


    def main(self, root, **kwargs):
        sc ,top, bottom= self.pbl_rootStackContainer(root, '!!Modify user', centered=True)
        self.pageForm(sc,bottom)
        self.pageSaving(sc,bottom)
        self.pageSaved(sc,bottom)
    
    def pageForm(self,sc,bottom):
        client = sc.contentPane(datapath='form')
        client.dataRecord('.data.user', 'adm.user', username=self.user, _init=True)
        client.dataScript('.isValid',"return true", data='=.data',
                          _if='genro.dataValidate(data)',
                          _else="genro.focusOnError(data); return false;", dummy='^form.doSave')
        client.dataRpc('.response.save','save', data='=.data', _POST=True, isValid='^.isValid' , 
                        _if='isValid',
                        _onResult='SET _pbl.selectedPage=2;')

        client.dataScript('dummy','SET _pbl.selectedPage=1;', isValid='^.isValid', _if='isValid')
        
        
        fb = client.formbuilder(datapath='.data',cols=1, margin_left='1em',
                         cellspacing=7,margin_top='1em',onEnter='FIRE form.doSave=true')
        fb.field('adm.user.firstname',width='12em',value='^.user.firstname')
        fb.field('adm.user.lastname',width='12em',value='^.user.lastname')
        
        fb.field('adm.user.email', width='18em', validate_email=True, value='^.user.email',
                  invalidMessage='!!Invalid email')
        
        fb.textbox(lbl='!!New password',width='12em',type='password', value='^.newpass', 
                    validate_len='4:',invalidMessage='!!Value too short')

        fb.textbox(lbl='!!Confirm password',type='password',width='12em', value='^.newpass2',
                    invalidMessage=u"!!The passwords doesn't match",
                    validate_call="var v=GET .newpass; return ((v==value) || (!value && !v))")
        
        bottom['right'].div('!!Confirm', connect_onclick='FIRE form.doSave=true',_class='bottom_btn',float='right' )
        bottom['right'].div('!!Cancel',connect_onclick='genro.gotoHome()', _class='bottom_btn',float='right')

    def pageSaving(self,sc,bottom):
        client = sc.contentPane(datapath='form')
        client.div(u"!!Saving...", _class='pbl_mediummessage', margin_top='1em')

    def pageSaved(self,sc,bottom):
        client = sc.contentPane(datapath='form')
        client.div(u"!!User profile saved",_class='pbl_mediummessage',margin_top='1em')
                
    def rpc_save(self,data=None,**kwargs):
        user = data['user']
        if data['newpass']:
            user['md5pwd'] = self.application.changePassword(None, None, data['newpass'])

        self.db.table('adm.user').update(user)

        self.db.commit()
        return 'Record Saved'
           
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
