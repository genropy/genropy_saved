#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" login.py """

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    
    def windowTitle(self):
        return '!!Assopy login'

    def main(self, root,fromPage='index.py', **kwargs):
        root.data('fromPage',fromPage)
        top,client,bottom = self.publicPane(root, '!!Accesso area riservata', height='230px')
        fb = client.formbuilder(cols=1,margin='auto',margin_top='4em',onEnter='FIRE loginbtn=true')
        fb.textbox(lbl='!!Utente', value='^form.user',autofocus=True,width='20em')
        fb.textbox(lbl='!!Password', type='password', value='^form.password',width='10em')
        client.div("!!Inserire il nome utente, non l'indirizzo email",text_align='left',margin_left='1em',_class='pbl_largemessage',font_size='.95em')
        
        client.dataRpc('_aux.login', 'doLogin', login='=form', btn='^loginbtn')
        root.dataRecord('_pbl.user_record','assopy.utente', username='^form.user')
        if not fromPage:
            root.dataFormula('fromPage',"'index.py'", _if='userid!=username',_else="'cambio_password.py'",userid='^_pbl.user_record.id',username='=_pbl.user_record.username')
        client.dataScript('_aux.dologin',"genro.gotoURL(fromPage)" , fromPage='=fromPage' , message='^_aux.login.message',
                            _if="message==''", _else="SET _aux.error_message = msg;", msg='!!Utente o password errati')

        fb.div('^_aux.error_message', text_align='center', height='1em')
        bottom.div('!!Registrati', connect_onclick="genro.gotoURL('nuovo_utente.py')",_class='pbl_button',float='left',width='7em')
        bottom.div('!!Password dimenticata ?', connect_onclick="genro.gotoURL('password_dimenticata.py')",_class='pbl_button',float='left',width='14em')
        bottom.div('!!Entra',connect_onclick="FIRE loginbtn=true",_class='pbl_button pbl_confirm',float='right',width='9em')
        bottom.div('!!Annulla',connect_onclick='genro.pageBack()',_class='pbl_button pbl_cancel',float='right',width='9em')
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
