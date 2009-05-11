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

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):

    py_requires='basecomponent:Public,utils:SendMail'
    
    def windowTitle(self):
         return '!!Assopy Password Dimenticata'

    def main(self, root, userid=None, **kwargs):
        top, pages = self.publicPagedPane(root, '!!Password Dimenticata', height='230px')
        if userid:
            self._doNewPassword(userid)
            self.pageConfirmed(pages, userid)
        else:
            self.pageForm(pages)
            self.pageSaving(pages)
            self.pageSaved(pages)

    def pageSaving(self, pages):
        client, bottom=self.publicPage(pages,datapath='form')
        client.div('!!Invio nuova password in corso...', _class='pbl_largemessage',
                                margin_top='2em',margin='auto')
        
    def pageSaved(self, pages):
        client, bottom=self.publicPage(pages,datapath='form')
        client.div(u"!!Ti è stata spedita una mail di conferma all'indirizzo:",_class='pbl_largemessage',_class='pbl_largemessage',
                                margin_top='2em',margin='auto')
        client.div(u"^newpass.mail_to",_class='pbl_largemessage',_class='pbl_largemessage',
                                margin='auto')
        client.div(u"!!Segui le istruzioni nella mail per ricevere i tuoi dati di accesso", _class='pbl_largemessage',_class='pbl_largemessage',
                                margin='auto')
        bottom.div(u'!!Torna al menù',connect_onclick="genro.gotoURL('index.py')", _class='pbl_button', float='right')
    
    def pageConfirmed(self,pages, userid):
        client, bottom=self.publicPage(pages,datapath='form')
        recordBag = self.db.table('assopy.utente').record(userid).output('bag')
        
        client.div(u"!!Ti è stata spedita una mail con la nuova password all'indirizzo:",_class='pbl_largemessage',_class='pbl_largemessage',
                                margin_top='2em',margin='auto')
        client.div(recordBag['email'],_class='pbl_largemessage',_class='pbl_largemessage',
                                marginright='auto')
        bottom.div(u'!!Torna al menù',connect_onclick="genro.gotoURL('index.py')", _class='pbl_button', float='right')
        
    def pageForm(self, pages):
        client, bottom=self.publicPage(pages,datapath='form')

        client.dataScript('_aux.isvalid',"return true", 
                          _if='genro.dataValidate(data)',
                          _else='genro.focusOnError(data); return false;',
                          data='=newpass',
                          buttonsave='^confirmbtn'
                          )
        client.dataScript('_aux.changepage','SET _pbl.selectedPage=1;', isvalid='^_aux.isvalid', _if='isvalid')
        client.dataRpc('_aux.donewpass', 'confirmNewPassword', data='=newpass', 
                       isvalid='^_aux.isvalid', _if='isvalid',
                       _onResult="SET _pbl.selectedPage=2;")

        fb= client.formbuilder(cols=1, datapath='newpass', border_spacing='5px',margin='auto',margin_top='4em',onEnter='FIRE confirmbtn=true')

        fb.textbox(lbl='Email', value='^.mail_to', width='30em', 
                   validate_remote="checkUserEmail", required=True,autofocus=True,
                   invalidMessage='!!Nessun utente registrato con questa email')

        bottom.div('!!Conferma',connect_onclick="FIRE confirmbtn=true", _class='pbl_button pbl_confirm', float='right')
        bottom.div('!!Annulla',connect_onclick='genro.pageBack()', _class='pbl_button pbl_cancel', float='right')

    def rpc_checkUserEmail(self, value):
        result = self.db.table('assopy.utente').query(columns='$username', where='$email = :value', value=value).fetch()
        return bool(result)
    
    def _doNewPassword(self, userid, **kwargs):
        newpass = str(random.random()*100000).replace('.','')[0:4]
        newpassmd5 = self.application.changePassword(None, None, newpass)
        self.db.table('assopy.utente').update({'id':userid, 'pwd':newpassmd5, 'stato':'confermato'})
        self.db.commit()
        
        recordBag = self.db.table('assopy.utente').record(userid).output('bag')
        recordBag['newpassword'] = newpass
        recordBag['link'] = self.externalUrl('assopy/cambio_password.py', _user_login='%s:%s' % (recordBag['username'], recordBag['newpassword']))
        
        return self.sendMailTemplate('new_pwd.xml', recordBag['email'], recordBag)
        

    def rpc_confirmNewPassword(self, data, **kwargs):
        value = data['mail_to']
        users = self.db.table('assopy.utente').query(columns='$id', where='$email = :value', value=value).fetch()
        
        for u in users:
            userid = u['id']
            recordBag = self.db.table('assopy.utente').record(userid).output('bag')
            recordBag['link'] = self.externalUrl('assopy/password_dimenticata.py', userid=recordBag['id'])
            self.sendMailTemplate('confirm_new_pwd.xml', recordBag['email'], recordBag)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
