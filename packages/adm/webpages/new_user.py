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
import hashlib

from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public,utils:SendMail'
    
    def main(self, root, userid=None,**kwargs):
        #get header and stack container. This container behaves like a multiple sc site inside the page itself
        sc, top, bottom = self.pbl_rootStackContainer(root, '!!New user',selected='^_pbl.selectedPage', width='450px', height='230px', centered=True)
        
        # so after the subscription, the userid is passed to the page through the confirm link 
        if userid:
            try:
            #get the record from the db
                recorduser = self.db.table('adm.user').record(id=userid,mode='bag')
                recorduser['status'] = 'conf'
                self.db.table('adm.user').update(recorduser)
                self.db.commit()
                self.pageConfirmed(sc, bottom,firstname=recorduser['firstname'],lastname=recorduser['lastname'])
            except:
                self.pageExpired(sc,bottom)
        else:
            #create the sc into the stack. The upper page is the one defined into pageForm
            self.pageForm(sc,bottom)
            self.savingPane(sc,bottom)
            self.savedPane(sc,bottom)
            self.pageError(sc,bottom)
            
    def pageForm(self,sc,bottom):
        # get a new center pane and footer pane
        center = sc.contentPane(datapath='form')
        self.formController(center)
        fb = center.formbuilder(cols=1, margin_top='1em', datapath='.data.user',
                                 onEnter='FIRE form.doSave=true',margin_left='2em')
        fb.field('adm.user.email', width='18em', validate_email=True, invalidMessage='!!Invalid email', required=True)
        
        fb.field('adm.user.username', width='12em', validate_len='3:32' ,
                     validate_nodup=True, invalidMessage='!!Invalid username', required=True)
        
        fb.field('adm.user.firstname', width='18em', validate_len='3:32',validate_case='c',
                  invalidMessage='!!Value too short',required=True)
        fb.field('adm.user.lastname', width='18em', validate_len='3:32',validate_case='c',
                  invalidMessage='!!Value too short',required=True)
                  
        fb.textbox(lbl='!!Password', type='password', width='12em', validate_len='4:', value='^.password',
                        invalidMessage='!!Value too short', required=True)
        fb.textbox(lbl='!!Confirm password', type='password', width='12em', validate_len='4:', value='^aux.password2',
                        invalidMessage='!!Value too short', required=True)
        
        bottom['right'].div('!!Login', connect_onclick='FIRE form.doSave', float='right',  _class='bottom_btn')
        bottom['right'].div('!!Cancel', connect_onclick='genro.pageBack()', float='right', _class='bottom_btn')
        
    def formController(self,pane):
        #center.data('user_regex','^\w{3,}$') #not working work around, fix it!
        pane.dataScript('.checkPwd','return (pwd1==pwd2)',pwd1='^.data.user.password',pwd2='^aux.password2')
        pane.dataScript('.isValid',"return true && checkPwd;",
                          _if='genro.dataValidate(data)',
                          _else='genro.focusOnError(data);return false;',  
                          data='=.data.user', 
                          checkPwd='=.checkPwd',
                          _fired='^form.doSave')
        pane.dataScript('dummy', 'SET _pbl.selectedPage=1;', isValid='^.isValid', _if='isValid')
        pane.dataRpc('.response.save', 'saveUser', recordBag='=.data.user', 
                             _POST=True, isValid='^.isValid' ,_if='isValid')
        pane.dataScript('dummy', 'SET _pbl.selectedPage=3;',responseSave='^.response.save',
                           _if='responseSave!="ok"', _else='SET _pbl.selectedPage=2;')

    def savingPane(self, sc,bottom):
        center = sc.contentPane()
        #append a message using template
        center.div(template=u"!!Thank you for registering ^.firstname ^.lastname", datasource='^form.data.user',margin_top='2em',
                                _class='pbl_mediummessage')

    def savedPane(self,sc,bottom):
        # get a new center pane and footer pane
        center = sc.contentPane()
        #append a message using template
        center.div(template=u"!!Thank you for registering ^.firstname ^.lastname", datasource='^form.data.user',margin_top='2em',
                _class='pbl_mediummessage')
        center.div(u"!!An email was sent to you",_class='pbl_mediummessage')
        center.div(u"!!Please check your email to complete the registration.",_class='pbl_mediummessage')
        bottom['right'].div('!!Ok',connect_onclick='genro.pageBack()' ,_class='bottom_btn',float='right')
        
    def pageError(self,sc,bottom):
        # get a new center pane and footer pane
        center = sc.contentPane(region='center')
        #append a message using template
        center.div(template=u"!!Error: ^.save", datasource='^form.response',_class='pbl_mediummessage')

        
        
    def pageConfirmed(self, sc,bottom, firstname, lastname):
        center = sc.contentPane()
        center.div(u"!!Your registration is complete, thank you!", _class='pbl_mediummessage',margin_top='2em')
        bottom['right'].div('!!Login',connect_onclick="genro.gotoURL('login.py')",float='right',_class='bottom_btn')

    def pageExpired(self,sc,bottom):
        center = sc.contentPane()
        center.div(u"!!Your registration expired, please register again.",_class='pbl_mediummessage',margin_top='2em')
        bottom['right'].div('!!Registration page',connect_onclick="genro.pageReload({userid:''})",float='right',_class='bottom_btn')


    def rpc_saveUser(self, recordBag, **kwargs):
        try:
            recordBag['registration_date'] = datetime.date.today()
            recordBag['status'] = 'wait'
            recordBag['id'] = self.db.table('adm.user').newPkeyValue()
            plainpwd = recordBag.pop('password')
            userid = recordBag['id']
            md5_userid = hashlib.md5(str(userid)).hexdigest()
            new_pass = hashlib.md5(plainpwd+md5_userid).hexdigest()+':'+md5_userid
            recordBag['md5pwd'] = new_pass
            self.db.table('adm.user').insert(recordBag)
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
        recordBag['link'] = self.externalUrl('adm/new_user.py', userid=recordBag['id'])
        return self.sendMailTemplate('new_user.xml', recordBag['email'], recordBag)

        
    
