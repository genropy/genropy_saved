#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """
import datetime
import os
import haslib

from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='basecomponent:Public,utils:SendMail'
    
    def windowTitle(self):
         return '!!Assopy Nuovo Utente'
        
    def main(self, root, userid=None,**kwargs):
        #get header and stack container. This container behaves like a multiple pages site inside the page itself
        top,pages=self.publicPagedPane(root,'!!Registrazione nuovo utente',height='250px')
        
        # so after the subscription, the userid is passed to the page through the confirm link 
        if userid:
            try:
                #get the record from the db
                user = self.db.table('assopy.utente').record(id=userid).output('bag')
                #change the state of the user
                self.db.table('assopy.utente').update({'id':user['id'], 'stato':'confermato'})
                self.db.commit()
                #go to the confirmation page
                self.pageConfirmed(pages,username=user['nome_cognome'])
            except:
                self.pageExpired(pages)
        else:
            #create the pages into the stack. The upper page is the one defined into pageForm
            self.pageForm(pages)
            self.pageSaving(pages)
            self.pageSaved(pages)

    def pageForm(self,pages):
        # get a new client pane and footer pane
        client,bottom=self.publicPage(pages, valign='middle',datapath='form')
       
        client.data('user_regex','^\w{3,}$') #not working work around, fix it!
        
        #-------------data logic definition----------------------------------
        client.dataScript('.isValid',"return true", data='=.data.user',_if='genro.dataValidate(data)',
                                _else='genro.focusOnError(data);return false;', dummy='^form.doSave')
                                
        client.dataScript('dummy', 'SET _pbl.selectedPage=1;', isValid='^.isValid', _if='isValid')
        client.dataRpc('.response.save', 'saveUser', recordBag='=.data.user',
                             _POST=True, isValid='^.isValid' ,_if='isValid',
                             _onResult='SET _pbl.selectedPage=2;')
        client.dataScript('dummy', 'alert("server response"+responseSave)',responseSave='.^response.save',
                           _if='responseSave!="ok"')
        
        #-------------widget definition---------------------------------
        fb = client.formbuilder(cols=1, margin='1em', datapath='.data.user',onEnter='FIRE form.doSave=true')
        
        fb.field('assopy.utente.nome_cognome', width='18em', validate_len='3:32',validate_case='c',autofocus=True,
                  validate_regex='\w* \w*',
                  invalidMessage='!! almeno 3 caratteri',required=True)
        fb.field('assopy.utente.username', width='12em', lbl='!!Utente', validate_len='3:32' ,validate_regex='=user_regex',
                 validate_nodup=True, invalidMessage='!!Nome utente non valido',required=True)
        fb.textbox('password',lbl='Password', type='password', width='12em', validate_len='4:', value='^.password',
                   invalidMessage='!!almeno 4 caratteri',required=True)
        fb.field('email', width='18em', validate_email=True,invalidMessage='!!indirizzo non valido', required=True)
        
        bottom.div('!!Registra', connect_onclick='FIRE form.doSave=true',_class='pbl_button pbl_confirm',float='right')
        bottom.div('!!Annulla',connect_onclick=self.cancel_url(), _class='pbl_button pbl_cancel',float='right')

    def pageSaving(self,pages):
        # get a new client pane and footer pane
        client,bottom=self.publicPage(pages)
        
        #append a message using template
        client.div(template=u"!!Grazie per la registrazione ^.nome_cognome", datasource='^form.data.user',_class='pbl_largemessage',
                               margin_top='1em',margin_right='3em',margin_left='3em')

    def pageSaved(self,pages):
        # get a new client pane and footer pane
        client,bottom=self.publicPage(pages)
        #append a message using template
        client.div(template=u"!!Grazie per la registrazione ^.nome_cognome", datasource='^form.data.user',_class='pbl_largemessage',
                                margin_top='1em',margin_right='3em',margin_left='3em')
        client.div(u"!!Ti è stata spedita una mail di conferma",_class='pbl_largemessage',_class='pbl_largemessage',
                                margin_right='3em',margin_left='3em')
        client.div(u"!!Controlla nella posta (anche nello spam) e non appena avrai completato la registrazione potrai accedere al sito.",
                                margin_right='3em',margin_left='3em',
                                _class='pbl_largemessage')
        bottom.div('Ok',connect_onclick=self.cancel_url() ,_class='pbl_button',float='right')
        
    def pageConfirmed(self,pages,username):
        client,bottom=self.publicPage(pages)
        client.data('user.username',username)
        client.div(template = u"!!Benvenuto ^.username, la tua registrazione è completata.", datasource='^user', _class='pbl_largemessage',
                                margin_top='1em',margin_right='3em',margin_left='3em')
        
        client.div(u"!!Ora puoi accedere al sito e, se lo desideri, puoi completare il tuo profilo.",_class='pbl_largemessage',
                                margin_right='3em',margin_left='3em')                        
        bottom.div('!!Accedi al sito',connect_onclick="genro.gotoURL('login.py')",float='right',_class='pbl_button')

    def pageExpired(self,pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!La tua registrazione è scaduta, per favore registrati nuovamente.",_class='pbl_largemessage',
                                    margin_top='1em',margin_right='3em',margin_left='3em')
        bottom.div('!!Torna alla registrazione',connect_onclick="genro.pageReload({userid:''})",float='right',_class='pbl_button')


    def rpc_saveUser(self, recordBag, **kwargs):
        try:
            recordBag['data_registrazione'] = datetime.date.today()
            recordBag['stato'] = 'provvisorio'
            recordBag['pwd'] = hashlib.md5(recordBag.pop('password')).hexdigest()
            recordBag['id'] = self.db.table('assopy.utente').newPkeyValue()
            self.db.table('assopy.utente').insert(recordBag)
            self.db.commit()
            try:
                self.sendConfirmationMail(recordBag)
                return 'ok'
            except Exception, err:
                return 'Record saved. Email error %s' %err
        except Exception, err:
            return 'Record not saved. Error %s' %err

        
        
    def sendConfirmationMail(self, recordBag):
        """
        this method is to add into gnrwebpage
        """
        recordBag['link'] = self.externalUrl('assopy/nuovo_utente.py', userid=recordBag['id'])
        return self.sendMailTemplate('new_user.xml', recordBag['email'], recordBag)
        
        
    def rpc_chkDuplicates(self, fldname, value):
        return self.db.query('assopy.utente', where='$%s = :val' % fldname, val=value).count()
        
    
