#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" cambio_password.py """
import md5

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    
    def windowTitle(self):
         return '!!Assopy Cambio Password'
    def pageAuthTags(self, method=None, **kwargs):
        """
        authorizated people have tag user
        """
        return 'users'


    def main(self, root, **kwargs):
        """
        this is the main of the page
        """
        top, pages = self.publicPagedPane(root, '!!Cambia Password',height='230px') # see the component method
        changeusername=(self.userRecord('id')==self.userRecord('username'))
        self.formPage(pages,changeusername)
        self.okPage(pages,changeusername)

    def formPage(self, pages,changeusername):
        client, bottom=self.publicPage(pages,datapath='form') # see the component method
        
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
        fbp= client.formbuilder(cols=1, datapath='passchange', border_spacing='5px',margin='auto', margin_top='3em',onEnter='FIRE confirmbtn=true')
        
        if changeusername:
            fbp.data('user_regex','^\w{3,}$')
            fbp.field('assopy.utente.username', width='12em', lbl='Utente', validate_len='3:32' ,
                validate_regex='=user_regex',validate_nodup=True, autofocus=True,
                promptMessage=u'!!Scegli un nome utente (non potrai più cambiarlo)',
                invalidMessage=u'!!Nome utente non valido',required=True)
        
                    
        fbp.textbox(lbl='!!Password precedente', width='12em', type='password', value='^.oldpass', required=True,
                    autofocus=(not changeusername),invalidMessage=u'La password digitata è errata',validate_remote="checkOldPwd")

        fbp.textbox(lbl='!!Nuova password',width='12em',type='password', value='^.newpass', 
                    validate_len='4:',invalidMessage='almeno 4 caratteri',required=True)

        fbp.textbox(lbl='!!Conferma password',type='password',width='12em', value='^.newpass2',
                    invalidMessage=u'!!La password di conferma digitata è differente dalla nuova.',
                    validate_call="var v=GET .newpass; return ((v==value) || (!value && !v))")


        bottom.div('!!Conferma',connect_onclick="FIRE confirmbtn=true", _class='pbl_button pbl_confirm', float='right')
        bottom.div('!!Annulla',connect_onclick='genro.pageBack()', _class='pbl_button pbl_cancel', float='right')
        
    def okPage(self, pages,changeusername):
        client, bottom = self.publicPage(pages,datapath='form', valign='middle') # see component method
        if changeusername:
            client.div(u'!!Ti è stato assegnato il nome utente prescelto.', _class='pbl_largemessage',
                                margin_top='1em',margin_right='3em',margin_left='3em')
        client.div(u'!!La tua password è stata modificata', _class='pbl_largemessage',
                                margin_top='1em',margin_right='3em',margin_left='3em')
        bottom.div(u'!!Torna al login',connect_onclick="genro.logout()", _class='pbl_button', float='right')
        

    def rpc_checkOldPwd(self, value):
        return self.application.validatePassword(value, self.avatar.pwd)
    
    def rpc_doChangePassword(self, data, **kwargs):
        newpass = self.application.changePassword(None, None, data['newpass'])
        if data['username']:
            self.db.table('assopy.utente').update({'id':self.avatar.userid, 'pwd':newpass, 'username':data['username']})
        else:
            self.db.table('assopy.utente').update({'id':self.avatar.userid, 'pwd':newpass})
        
        self.db.commit()

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
