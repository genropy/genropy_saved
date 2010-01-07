#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" cambio_password.py """
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='public:Public'
    
    def windowTitle(self):
         return '!!Change Password'
    def pageAuthTags(self, method=None, **kwargs):
        """
        authorizated people have tag user
        """
        return 'user'


    def main(self, root, **kwargs):
        """
        this is the main of the page
        """
        sc, top, bottom = self.pbl_rootStackContainer(root, '!!Change password',selected='^_pbl.selectedPage')
        changeusername=(self.db.table('adm.user').query(where='$id=:username',username=self.user).count()>0)
        self.formPage(sc,bottom,changeusername)
        self.okPage(sc,bottom,changeusername)

    def formPage(self, sc,bottom,changeusername):
        client = sc.contentPane()
        
        #-------------------data logic definition--------------------
        client.dataScript('_aux.isvalid',"return true", 
                          _if='genro.dataValidate(data)',
                          _else='genro.focusOnError(data); return false;',
                          data='=passchange',
                          buttonsave='^confirmbtn'
                          )
        client.dataRpc('_aux.chpwd', 'doChangePassword', data='=passchange', 
                       isvalid='^_aux.isvalid', _if='isvalid',
                       _onResult="SET _pbl.selectedPage=1;")
                       
        #-------------------widget definition--------------------
        fbp= client.formbuilder(cols=1, datapath='passchange', border_spacing='5px', margin='1em',onEnter='FIRE confirmbtn=true')
        
        if changeusername:
            fbp.data('user_regex','^\w{3,}$')
            fbp.field('adm.user.username', width='12em', lbl='Utente', validate_len='3:32' ,
                validate_regex='=user_regex',validate_nodup=True, autofocus=True,
                promptMessage=u'!!Choose a valid username',
                invalidMessage=u'!!Invalid username',required=True)
        
                    
        fbp.textbox(lbl='!!Old password', width='12em', type='password', value='^.oldpass', required=True,
                    autofocus=(not changeusername),invalidMessage=u'Wrong password',validate_remote="checkOldPwd")

        fbp.textbox(lbl='!!New password',width='12em',type='password', value='^.newpass', 
                    validate_len='4:',invalidMessage='At least 4 characters',required=True)

        fbp.textbox(lbl='!!Confirm password',type='password',width='12em', value='^.newpass2',
                    invalidMessage=u'!!Password mismatches',
                    validate_call="var v=GET .newpass; return ((v==value) || (!value && !v))")


        bottom['right'].div('Confirm',connect_onclick="FIRE confirmbtn=true", _class='bottom_btn', float='right')
        bottom['right'].div('Cancel',connect_onclick='genro.pageBack()', _class='bottom_btn', float='right')
        
    def okPage(self, sc,bottom,changeusername):
        client = sc.contentPane(datapath='form')
        if changeusername:
            client.div(u'!!Username has been changed', _class='pbl_mediummessage',
                                margin_top='1em',margin_right='3em',margin_left='3em')
        client.div(u'!!Password has been changed', _class='pbl_mediummessage',
                                margin_top='1em',margin_right='3em',margin_left='3em')
        bottom['left'].div(u'!!Back to login',connect_onclick="genro.logout()", _class='bottom_btn', float='left')
        

    def rpc_checkOldPwd(self, value):
        return self.application.validatePassword(value, self.avatar.pwd)
    
    def rpc_doChangePassword(self, data, **kwargs):
        newpass = self.application.changePassword(None, None, data['newpass'])
        if data['username']:
            self.db.table('adm.user').update({'id':self.avatar.userid, 'md5pwd':newpass, 'username':data['username']})
        else:
            self.db.table('adm.user').update({'id':self.avatar.userid, 'md5pwd':newpass})
        
        self.db.commit()

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
