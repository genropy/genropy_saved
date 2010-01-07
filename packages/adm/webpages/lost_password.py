#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """
import random
import os

from gnr.core.gnrstring import templateReplace

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):

    py_requires='public:Public,utils:SendMail'
    
    def windowTitle(self):
         return '!!Lost Password'

    def main(self, root, userid=None, **kwargs):
        sc, top,bottom = self.pbl_rootStackContainer(root, '!!Lost Password', height='120px',  width='35em', centered=True)
        if userid:
            self._doNewPassword(userid)
            self.pageConfirmed(sc,bottom['left'], userid)
        else:
            self.pageForm(sc,bottom['right'])
            self.pageSaving(sc)
            self.pageSaved(sc,bottom['left'])

    def pageSaving(self, sc):
        center = sc.contentPane(datapath='form')
        center.div('!!Sending new password...', _class='pbl_mediummessage',
                                margin_top='2em',margin='auto')
        
    def pageSaved(self, sc,bottom):
        center = sc.contentPane(datapath='form')
        center.div(u"!!A confirmation mail has been sent at this address:",_class='pbl_mediummessage',
                                margin_top='2em',margin='auto')
        center.div(u"^newpass.mail_to",_class='pbl_mediummessage',
                                margin='auto')
        center.div(u"!!Read the email containing your account informations", _class='pbl_mediummessage',
                                margin='auto')
        bottom.div(u'!!Back to menu',connect_onclick="genro.gotoHome()", _class='bottom_btn',float='left')
    
    def pageConfirmed(self,sc,bottom,userid):
        center= sc.contentPane(datapath='form')
        recordBag = self.db.table('adm.user').record(userid).output('bag')
        
        center.div(u"!!A confirmation mail has been sent at this address:",_class='pbl_mediummessage',
                                margin_top='2em',margin='auto')
        center.div(recordBag['email'],_class='pbl_mediummessage',
                                marginright='auto')
        bottom.div(u'!!Back to menu',connect_onclick="genro.gotoHome()", _class='bottom_btn', float='left')
        
    def pageForm(self, sc,bottom):
        center = sc.contentPane(datapath='form')
        center.dataScript('_aux.isvalid',"return true", 
                          _if='genro.dataValidate(data)',
                          _else='genro.focusOnError(data); return false;',
                          data='=newpass',
                          buttonsave='^confirmbtn'
                          )
        center.dataScript('_aux.changepage','SET _pbl.selectedPage=1;', isvalid='^_aux.isvalid', _if='isvalid')
        center.dataRpc('_aux.donewpass', 'confirmNewPassword', data='=newpass', 
                       isvalid='^_aux.isvalid', _if='isvalid',
                       _onResult="SET _pbl.selectedPage=2;")
        fb= center.formbuilder(cols=1, datapath='newpass', border_spacing='5px',margin='auto',margin_top='2em',onEnter='FIRE confirmbtn=true')

        fb.textbox(lbl='Email', value='^.mail_to', width='30em', 
                   validate_remote="checkUserEmail", required=True,autofocus=True,
                   invalidMessage='!!No user has this email')

        bottom.div('!!Confirm',connect_onclick="FIRE confirmbtn=true", _class='bottom_btn', float='right')
        bottom.div('!!Cancel',connect_onclick='genro.pageBack()', _class='bottom_btn', float='right')

    def rpc_checkUserEmail(self, value):
        result = self.db.table('adm.user').query(columns='$username', where='$email = :value', value=value).fetch()
        return bool(result)
    
    def _doNewPassword(self, userid, **kwargs):
        newpass = str(random.random()*100000).replace('.','')[0:4]
        newpassmd5 = self.application.changePassword(None, None, newpass)
        self.db.table('adm.user').update({'id':userid, 'md5pwd':newpassmd5, 'status':'conf'})
        self.db.commit()
        
        recordBag = self.db.table('adm.user').record(userid).output('bag')
        recordBag['newpassword'] = newpass
        recordBag['link'] = self.externalUrl('adm/change_password', _user_login='%s:%s' % (recordBag['username'], recordBag['newpassword']))
        
        return self.sendMailTemplate('new_pwd.xml', recordBag['email'], recordBag)
        

    def rpc_confirmNewPassword(self, data, **kwargs):
        value = data['mail_to']
        users = self.db.table('adm.user').query(columns='$id', where='$email = :value', value=value).fetch()
        
        for u in users:
            userid = u['id']
            recordBag = self.db.table('adm.user').record(userid).output('bag')
            recordBag['link'] = self.externalUrl('adm/lost_password', userid=recordBag['id'])
            self.sendMailTemplate('confirm_new_pwd.xml', recordBag['email'], recordBag)


