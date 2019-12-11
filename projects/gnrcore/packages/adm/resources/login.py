# -*- coding: utf-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from builtins import str
from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from datetime import date
from gnr.core.gnrbag import Bag
from gnr.app.gnrapp import GnrRestrictedAccessException
        
class LoginComponent(BaseComponent):
    login_error_msg = '!!Invalid login'
    login_title = '!!Login'
    new_window_title = '!!New Window'
    auth_workdate = 'admin'
    auth_page = 'user'
    index_url = 'html_pages/splashscreen.html'
    closable_login = False
    loginBox_kwargs = dict()

    def loginDialog(self,pane,gnrtoken=None,**kwargs):
        doLogin = self.avatar is None and self.auth_page
        if doLogin and not self.closable_login and self.index_url:
            pane.css('.dijitDialogUnderlay.lightboxDialog_underlay',"opacity:0;")
            pane.iframe(height='100%', width='100%', src=self.getResourceUri(self.index_url), border='0px')  
        loginKwargs = dict(_class='lightboxDialog') 
        loginKwargs.update(self.loginBox_kwargs)
        dlg = pane.dialog(subscribe_openLogin="this.widget.show()",
                          subscribe_closeLogin="this.widget.hide()",**loginKwargs)
       
        box = dlg.div(**self.loginboxPars())
        if self.closable_login:
            dlg.div(_class='dlg_closebtn',connect_onclick='PUBLISH closeLogin;')
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        wtitle = (self.loginPreference('login_title') or self.login_title) if doLogin else (self.loginPreference('new_window_title') or '!!New Window') 
        topbar.wtitle.div(wtitle)  
        if hasattr(self,'loginSubititlePane'):
            self.loginSubititlePane(box.div())
        fb = box.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='4px',onEnter='FIRE do_login;',
                                datapath='gnr.rootenv',width='100%',
                                fld_width='100%',row_height='3ex',keeplabel=True
                                ,fld_attr_editable=True)
        rpcmethod = self.login_newWindow
        start = 0
        if doLogin:
            start = 2
            fb.textbox(value='^_login.user',lbl='!!Username',row_hidden=False)
            fb.textbox(value='^_login.password',lbl='!!Password',type='password',row_hidden=False)
            pane.dataRpc('dummy',self.login_checkAvatar,user='^_login.user',password='^_login.password',
                        _onCalling='kwargs.serverTimeDelta = genro.serverTimeDelta;',
                        _if='user&&password&&!_avatar_user',_else='SET gnr.avatar = null;',
                        _avatar_user='=gnr.avatar.user',
                        _onResult="""var avatar = result.getItem('avatar');
                                     var error_message = result.getItem('login_error_msg');
                                    if(error_message){
                                        genro.publish('failed_login_msg',{'message':error_message});
                                        SET gnr.avatar.error = error_message;
                                        return;
                                    }
                                    if (!avatar){
                                        SET gnr.avatar = null;
                                        return;
                                    }
                                    if(avatar.getItem('status')!='conf'){
                                        SET gnr.avatar = avatar;
                                        genro.publish('confirmUserDialog');
                                        return;
                                    }
                                    var newenv = result.getItem('rootenv');
                                    var rootenv = GET gnr.rootenv;
                                    currenv = rootenv.deepCopy();
                                    currenv.update(newenv);
                                    SET gnr.rootenv = currenv;
                                    SET gnr.avatar = avatar;
                                """,sync=True,_POST=True)
            rpcmethod = self.login_doLogin    
        
        fb.dateTextBox(value='^.workdate',lbl='!!Workdate')
        valid_token = False
        if gnrtoken:
            valid_token = self.db.table('sys.external_token').check_token(gnrtoken)
        self.callPackageHooks('rootenvForm',fb)
        for fbnode in fb.getNodes()[start:]:
            if fbnode.attr['tag']=='tr':
                fbnode.attr['hidden'] = '==!_avatar || _hide '
                fbnode.attr['_avatar'] = '^gnr.avatar.user'
                fbnode.attr['_hide'] = '%s?hidden' %fbnode.value['#1.#0?value']
                
        if gnrtoken or not self.closable_login:
            pane.dataController("""
                            var href = window.location.href;
                            if(window.location.search){
                                var urlParsed = parseURL(window.location.href);
                                objectExtract(urlParsed.params,'gnrtoken,new_window,custom_index');        
                                window.history.replaceState({},document.title,serializeURL(urlParsed));

                            }
                            if(new_password){
                                if(valid_token){
                                    newPasswordDialog.show();
                                }else{

                                    PUBLISH openLogin;
                                    setTimeout(function(){
                                            genro.publish('failed_login_msg',{message:invalid_token_message});
                                        },1000);
                                }
                                
                            }else{
                                PUBLISH openLogin;
                            }
                            
                            """,_onBuilt=True,
                            new_password=gnrtoken or False,loginDialog = dlg.js_widget,
                            valid_token = valid_token,invalid_token_message='!!Change password link expired',
                            newPasswordDialog = self.login_newPassword(pane,gnrtoken=gnrtoken,dlg_login=dlg).js_widget,
                            fb=fb)


        fb.div(width='100%',position='relative',row_hidden=False).button('!!Enter',action='FIRE do_login',position='absolute',right='-5px',top='8px')
        dlg.dataController("genro.dlg.floatingMessage(sn,{message:message,messageType:'error',yRatio:1.85})",subscribe_failed_login_msg=True,sn=dlg)

        footer = box.div().slotBar('12,lost_password,*,new_user,12',height='18px',width='100%',tdl_width='6em')
        lostpass = footer.lost_password.div()
        new_user = footer.new_user.div()
        if self.loginPreference('forgot_password'):
            lostpass.div('!!Lost password',cursor='pointer',connect_onclick='FIRE lost_password_dlg;',
                            color='gray',font_size='12px',height='15px')
            lostpass.dataController("dlg_login.hide();dlg_lp.show();",_fired='^lost_password_dlg',dlg_login=dlg.js_widget,dlg_lp=self.login_lostPassword(pane,dlg).js_widget)
        if self.loginPreference('new_user'):
            self.login_newUser(pane)
            new_user.div('!!New User',cursor='pointer',connect_onclick='genro.publish("closeLogin");genro.publish("openNewUser");',
                            color='gray',font_size='12px',height='15px')

        pane.dataController("dlg_login.hide();dlg_cu.show();",dlg_login=dlg.js_widget,
                    dlg_cu=self.login_confirmUserDialog(pane,dlg).js_widget,subscribe_confirmUserDialog=True)


        footer.dataController("""
        if(!avatar || !avatar.getItem('user') || avatar.getItem('error')){
            var error = avatar? (avatar.getItem('error') || error_msg):error_msg
            genro.publish('failed_login_msg',{'message':error});
            return;
        }
        dlg.hide();
        genro.lockScreen(true,'login');
        genro.serverCall(rpcmethod,{'rootenv':rootenv,login:login},function(result){
            genro.lockScreen(false,'login');
            if (!result || result.error){
                dlg.show();
                genro.publish('failed_login_msg',{'message':result?result.error:error_msg});
            }else{
                genro.setData('gnr.avatar',new gnr.GnrBag(result))
                var user_dbstore = genro.getData('gnr.avatar.user_record.dbstore')
                rootpage = rootpage || result['rootpage'];
                if(user_dbstore){
                    if(!window.location.pathname.slice(1).startsWith(user_dbstore)){
                        var redirect_url = window.location.protocol+'//'+window.location.host+'/'+user_dbstore;
                        if(rootpage){
                            redirect_url+=rootpage;
                        }
                        window.location.assign(redirect_url);
                        return;
                    }
                }
                if(rootpage){
                    genro.gotoURL(rootpage);
                }
                if(doLogin){
                    if(!closable_login){
                        var rootpage = avatar.getItem('avatar_rootpage') || avatar.get('singlepage');
                        if(rootpage){
                            genro.gotoURL(rootpage);
                        }else{
                            genro.pageReload();
                        }
                    }
                }
            }
        },null,'POST');
        """,rootenv='=gnr.rootenv',_fired='^do_login',rpcmethod=rpcmethod,login='=_login',
            avatar='=gnr.avatar',
            rootpage='=gnr.rootenv.rootpage',closable_login=self.closable_login,
            error_msg='!!Invalid login',dlg=dlg.js_widget,
            doLogin=doLogin,
            _delay=1)  
        return dlg

    @public_method
    def login_doLogin(self, rootenv=None,login=None,guestName=None, **kwargs):
        self.doLogin(login=login,guestName=guestName,rootenv=rootenv,**kwargs)
        if login['error']:
            return dict(error=login['error'])
        rootenv['user'] = self.avatar.user
        rootenv['user_id'] = self.avatar.user_id
        rootenv['user_group_code'] = getattr(self.avatar,'group_code',None)
        rootenv['workdate'] = rootenv['workdate'] or self.workdate
        rootenv['login_date'] = date.today()
        rootenv['language'] = rootenv['language'] or self.language
        self.connectionStore().setItem('defaultRootenv',rootenv) #no need to be locked because it's just one set
        return self.login_newWindow(rootenv=rootenv)


    @public_method
    def login_checkAvatar(self,password=None,user=None,serverTimeDelta=None,**kwargs):
        result = Bag()
        try:
            avatar = self.application.getAvatar(user, password=password,authenticate=True)
            if not avatar:
                return result
        except GnrRestrictedAccessException as e:
            return Bag(login_error_msg=e.description)
        status = getattr(avatar,'status',None)
        if not status:
            avatar.extra_kwargs['status'] = 'conf'
        result['avatar'] = Bag(avatar.as_dict())
        if avatar.status != 'conf':
            return result
        data = Bag()
        data['serverTimeDelta'] = serverTimeDelta
        self.callPackageHooks('onUserSelected',avatar,data)
        canBeChanged = self.application.checkResourcePermission(self.pageAuthTags(method='workdate'),avatar.user_tags)
        result['rootenv'] = data
        default_workdate = self.clientDatetime(serverTimeDelta=serverTimeDelta).date()
        data.setItem('workdate',default_workdate, hidden= not canBeChanged)
        return result

    def loginboxPars(self):
        return dict(width='320px',_class='index_loginbox')

    def login_lostPassword(self,pane,dlg_login):
        dlg = pane.dialog(_class='lightboxDialog')
        box = dlg.div(**self.loginboxPars())
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        topbar.wtitle.div('!!Lost password')  
        fb = box.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='4px',onEnter='FIRE recover_password;',
                                datapath='lost_password',width='100%',
                                fld_width='100%',row_height='3ex')
        fb.textbox(value='^.email',lbl='!!Email')
        fb.div(width='100%',position='relative',row_hidden=False).button('!!Recover',action='FIRE recover_password',position='absolute',right='-5px',top='8px')
        fb.dataRpc("dummy",self.login_confirmNewPassword, _fired='^recover_password',_if='email',email='=.email',
                _onResult="""if(result=="ok"){
                    FIRE recover_password_ok;
                }else{
                    FIRE recover_password_err;
                }""")
        fb.dataController("""genro.dlg.floatingMessage(sn,{message:msg,messageType:'error',yRatio:.95})""",
                            msg='!!Missing user for this email',_fired='^recover_password_err',sn=dlg)
        fb.dataController("""genro.dlg.floatingMessage(sn,{message:msg,yRatio:.95})""",
                            msg='!!Check your email for instruction',_fired='^recover_password_ok',sn=dlg)
        footer = box.div().slotBar('12,loginbtn,*',height='18px',width='100%',tdl_width='6em')
        footer.loginbtn.div('!!Login',cursor='pointer',connect_onclick='FIRE back_login;',
                            color='gray',font_size='12px',height='15px')
        footer.dataController("dlg_lp.hide();dlg_login.show();",_fired='^back_login',
                        dlg_login=dlg_login.js_widget,dlg_lp=dlg.js_widget)
        return dlg

    def login_newPassword(self,pane,gnrtoken=None,dlg_login=None):
        dlg = pane.dialog(_class='lightboxDialog',subscribe_closeNewPwd='this.widget.hide();',subscribe_openNewPwd='this.widget.show();')
        box = dlg.div(**self.loginboxPars())
        
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        topbar.wtitle.div('!!New Password')  
        fb = box.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='4px',onEnter='FIRE set_new_password;',
                                datapath='new_password',width='100%',
                                fld_width='100%',row_height='3ex')
        if not gnrtoken:
            #change password by a logged user
            dlg.div(_class='dlg_closebtn',connect_onclick="genro.publish('closeNewPwd');")
            fb.textbox(value='^.current_password',lbl='!!Password',type='password')
        else:
            fb.data('.gnrtoken',gnrtoken)
        fb.textbox(value='^.password',lbl='!!New password',type='password')
        fb.textbox(value='^.password_confirm',lbl='!!Confirm password',type='password',
                    validate_call='return value==GET .password;',validate_call_message='!!Passwords must be equal')
        fb.div(width='100%',position='relative',row_hidden=False).button('!!Send',action='FIRE set_new_password',position='absolute',right='-5px',top='8px')
        fb.dataRpc('dummy',self.login_changePassword,_fired='^set_new_password',
                    current_password='=.current_password',
                    password='=.password',password_confirm='=.password_confirm',
                    _if='password==password_confirm',_box=box,
                    _else="genro.dlg.floatingMessage(_box,{message:'Passwords must be equal',messageType:'error',yRatio:.95})",
                    gnrtoken=gnrtoken,_onResult="""if(result){
                        genro.dlg.floatingMessage(kwargs._box,{message:'Wrong password',messageType:'error',yRatio:.95});
                        return;
                    }
                    genro.publish("closeNewPwd");genro.publish("openLogin")""")
        return dlg


    def login_confirmUserDialog(self,pane,gnrtoken=None,dlg_login=None):
        dlg = pane.dialog(_class='lightboxDialog')
        sc = dlg.stackContainer(**self.loginboxPars())
        box = sc.contentPane()
        sc.contentPane().div(self.loginPreference('check_email'),_class='index_logintitle',text_align='center',margin_top='50px')
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        topbar.wtitle.div(self.loginPreference('confirm_user_title') or '!!Confirm User')  
        box.div(self.loginPreference('confirm_user_message'),padding='10px',color='#777',font_style='italic',font_size='.9em',text_align='center')
        fb = box.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='4px',onEnter='FIRE confirm_email;',
                                datapath='new_password',width='100%',
                                fld_width='100%',row_height='3ex')
        fb.textbox(value='^.email',lbl='!!Email')
        fb.dataController("SET .email = avatar_email;",avatar_email='^gnr.avatar.email')
        fb.div(width='100%',position='relative',row_hidden=False).button('!!Send Email',action='FIRE confirm_email',position='absolute',right='-5px',top='8px')
        fb.dataRpc('dummy',self.login_confirmUser,_fired='^confirm_email',email='=.email',user_id='=gnr.avatar.user_id',
                    _if='email',
                    _onCalling='_sc.switchPage(1);',
                    _sc=sc.js_widget,
                    _else="genro.dlg.floatingMessage(_sn,{message:_error_msg,messageType:'error',yRatio:.95})",
                    _error_msg='!!Missing email',_sn=box)
        return dlg
        
        
    def login_newUser(self,pane,closable=False,**kwargs):
        dlg = pane.dialog(_class='lightboxDialog',
                            subscribe_openNewUser='this.widget.show(); genro.formById("newUser_form").newrecord();',
                            subscribe_closeNewUser='this.widget.hide();')

        kw = self.loginboxPars()
        kw['width'] = '400px'
        kw['height'] = '250px'
        kw.update(kwargs)
        form = dlg.frameForm(frameCode='newUser',datapath='new_user',store='memory',**kw)
        if closable:
            dlg.div(_class='dlg_closebtn',connect_onclick="genro.publish('closeNewUser')")
        form.dataController("PUT creating_new_user = false;",_fired='^#FORM.controller.loaded')
        topbar = form.top.slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        topbar.wtitle.div('!!New User')  
        self.login_newUser_form(form)
        form.dataRpc('dummy',self.login_createNewUser,data='=#FORM.record',
                    _do='^creating_new_user',_if='_do && this.form.isValid()',
                    _else='this.form.publish("message",{message:_error_message,messageType:"error"})',
                    _error_message='!!Missing data',
                    _onResult="""if(result.ok){
                        genro.publish('closeNewUser');
                        genro.publish('floating_message',{message:result.ok,duration_out:6})
                    }else{
                        this.form.publish("message",{message:result.error,messageType:"error"});
                        PUT creating_new_user = false;
                    }
                    """,_lockScreen=True)
        if not closable:
            footer = form.bottom.slotBar('12,loginbtn,*',height='18px',width='100%',tdl_width='6em')
            footer.loginbtn.div('!!Login',cursor='pointer',connect_onclick="genro.publish('closeNewUser');genro.publish('openLogin');",
                            color='gray',font_size='12px',height='15px')
        return dlg

    def login_newUser_form(self,form):
        fb = form.record.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='6px',onEnter='SET creating_new_user = true;',
                                width='100%',tdl_width='6em',fld_width='100%',row_height='3ex')
        fb.textbox(value='^.firstname',lbl='!!First name',validate_notnull=True,validate_case='c',validate_len='2:')
        fb.textbox(value='^.lastname',lbl='!!Last name',validate_notnull=True,validate_case='c',validate_len='2:')
        fb.textbox(value='^.email',lbl='!!Email',validate_notnull=True)
        fb.textbox(value='^.username',lbl='!!Username',validate_notnull=True,validate_nodup='adm.user.username',validate_len='4:')
        fb.div(width='100%',position='relative',row_hidden=False).button('!!Send',action='SET creating_new_user = true;',position='absolute',right='-5px',top='8px')

    @public_method
    def login_createNewUser(self,data=None,**kwargs):
        tpl_userconfirm_id = self.loginPreference('tpl_userconfirm_id')
        print(f'tplconferma {tpl_userconfirm_id}')
        mailservice = self.getService('mail')
        try:
            data['status'] = 'new'
            self.db.table('adm.user').insert(data)
            data['link'] = self.externalUrlToken(self.site.homepage, userid=data['id'],max_usages=1)
            data['greetings'] = data['firstname'] or data['lastname']
            email = data['email']
            if tpl_userconfirm_id:
                mailservice.sendUserTemplateMail(record_id=data,template_id=tpl_userconfirm_id)
            else:
                body = self.loginPreference('confirm_user_tpl') or 'Dear $greetings to confirm click $link'
                mailservice.sendmail_template(data,to_address=email,
                                    body=body, subject=self.loginPreference('subject') or 'Confirm user',
                                    async_=False,html=True)
            self.db.commit()
        except Exception as e:
            return dict(error=str(e))
        return dict(ok=self.loginPreference('new_user_ok_message') or 'Check your email to confirm')

    def loginPreference(self,path=None):
        if not hasattr(self,'_loginPreference'):
            self._loginPreference = self.getPreference('general',pkg='adm') or Bag()
        if not path:
            return self._loginPreference
        return self._loginPreference[path]

    
    @public_method
    def login_newWindow(self, rootenv=None, **kwargs): 
        rootenv['workdate'] = rootenv['workdate']
        self.pageStore().setItem('rootenv',rootenv)
        self.db.workdate = rootenv['workdate']
        self.setInClientData('gnr.rootenv', rootenv)
        result = self.avatar.as_dict()
        return result


    @public_method
    def login_confirmUser(self, email=None,user_id=None, **kwargs):
        usertbl = self.db.table('adm.user')
        recordBag = usertbl.record(pkey=user_id,for_update=True).output('bag')
        userid = recordBag['id']
        oldrec = Bag(recordBag)
        recordBag['email'] = email
        recordBag['status'] = 'wait'
        usertbl.update(recordBag,oldrec)
        recordBag['link'] = self.externalUrlToken(self.site.homepage, userid=userid,max_usages=1)
        recordBag['greetings'] = recordBag['firstname'] or recordBag['lastname']
        tpl_userconfirm_id = self.loginPreference('tpl_userconfirm_id')
        mailservice = self.getService('mail')
        if tpl_userconfirm_id:
            mailservice.sendUserTemplateMail(record_id=recordBag,template_id=tpl_userconfirm_id)
        else:
            body = self.loginPreference('confirm_user_tpl') or 'Dear $greetings to confirm click $link'
            mailservice.sendmail_template(recordBag,to_address=email,
                                    body=body, subject=self.loginPreference('subject') or 'Password recovery',
                                    async_=False,html=True)
        self.db.commit()
        return 'ok'
        
    @public_method
    def login_confirmNewPassword(self, email=None,username=None, **kwargs):
        usertbl = self.db.table('adm.user')
        if username:
            users = usertbl.query(columns='$id', where='$username = :u', u=username).fetch()
        else:
            users = usertbl.query(columns='$id', where='$email = :e', e=email).fetch()
        if not users:
            return 'err'
        mailservice = self.getService('mail')
        tpl_new_password_id = self.loginPreference('tpl_new_password_id')
        for u in users:
            userid = u['id']
            recordBag = usertbl.record(userid).output('bag')
            recordBag['link'] = self.externalUrlToken(self.site.homepage, userid=recordBag['id'],max_usages=1)
            recordBag['greetings'] = recordBag['firstname'] or recordBag['lastname']
            body = self.loginPreference('confirm_password_tpl') or 'Dear $greetings set your password $link'
            if tpl_new_password_id:
                mailservice.sendUserTemplateMail(record_id=recordBag,template_id=tpl_new_password_id,)
            else:
                mailservice.sendmail_template(recordBag,to_address=email,
                                        body=body, subject=self.loginPreference('confirm_password_subject') or 'Password recovery',
                                        async_=False,html=True)
            self.db.commit()

        return 'ok'
            #self.sendMailTemplate('confirm_new_pwd.xml', recordBag['email'], recordBag)

    @public_method
    def login_changePassword(self,password=None,gnrtoken=None,current_password=None,**kwargs):
        if gnrtoken:
            method,args,kwargs,user_id = self.db.table('sys.external_token').use_token(gnrtoken)
            if not kwargs:
                return
            userid = kwargs.get('userid')
        else:
            if self.login_checkPwd(self.avatar.user,password=current_password):
                userid = self.avatar.user_id
            else:
                return 'Wrong password'
        if userid:
            self.db.table('adm.user').batchUpdate(dict(status='conf',md5pwd=password),_pkeys=userid)
            self.db.commit()


    @struct_method
    def login_screenLockDialog(self,pane):
        dlg = pane.dialog(_class='lightboxDialog',subscribe_screenlock="this.widget.show();this.setRelativeData('.password',null);",datapath='_screenlock')
        box = dlg.div(**self.loginboxPars())
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        wtitle = '!!Screenlock'
        topbar.wtitle.div(wtitle)  
        box.div('!!Insert password',text_align='center',font_size='.9em',font_style='italic')
        fb = box.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='4px',onEnter='FIRE .checkPwd;',
                                width='100%',
                                fld_width='100%',row_height='3ex')
        fb.textbox(value='^.password',lbl='!!Password',type='password',row_hidden=False)
        btn=fb.div(width='100%',position='relative',row_hidden=False).button('!!Enter',action='FIRE .checkPwd;this.widget.setAttribute("disabled",true);',position='absolute',right='-5px',top='8px')
        box.div().slotBar('*,messageBox,*',messageBox_subscribeTo='failed_screenout',height='18px',width='100%',tdl_width='6em')
        fb.dataRpc('.result',self.login_checkPwd,password='=.password',user='=gnr.avatar.user',_fired='^.checkPwd')
        fb.dataController("""if(!authResult){
                                genro.publish('failed_screenout',{'message':error_msg});
                            }else{
                                dlg.hide();
                            }
                            btn.setAttribute('disabled',false);
                            
                            """,authResult='^.result',btn=btn,dlg=dlg.js_widget,error_msg='!!Wrong password')

    @public_method  
    def login_checkPwd(self,user=None,password=None):
        validpwd = self.application.getAvatar(user, password=password,authenticate=True)
        if not validpwd:
            return False
        return True

