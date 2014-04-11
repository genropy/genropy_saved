# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from datetime import date
from gnr.core.gnrbag import Bag

#foundation/menu:MenuIframes,
class FrameIndex(BaseComponent):
    py_requires="""frameplugin_menu/frameplugin_menu:MenuIframes,
                   gnrcomponents/batch_handler/batch_handler:TableScriptRunner,
                   gnrcomponents/batch_handler/batch_handler:BatchMonitor,
                   gnrcomponents/chat_component/chat_component,
                   gnrcomponents/datamover:MoverPlugin,
                   gnrcomponents/maintenance:MaintenancePlugin
                   """
    js_requires='frameindex'
    css_requires='frameindex,public'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin,datamover,maintenance'
    custom_plugin_list = None
    index_page = False
    index_url = 'html_pages/splashscreen.html'
    indexTab = False
    hideLeftPlugins = False
    auth_preference = 'admin'
    auth_workdate = 'admin'
    auth_page='user'
    login_error_msg = '!!Invalid login'
    login_title = '!!Login'
    new_window_title = '!!New Window'
    
    def mainLeftContent(self,*args,**kwargs):
        pass 

    @property
    def defaultAuthTags(self):
        return ''
    
    def main(self,root,new_window=None,gnrtoken=None,custom_index=None,**kwargs):
        if gnrtoken and not self.db.table('sys.external_token').check_token(gnrtoken):
            root.dataController("""genro.dlg.alert(msg,'Error',null,null,{confirmCb:function(){
                    var href = window.location.href;
                    href = href.replace(window.location.search,'');
                    window.history.replaceState({},document.title,href);
                    genro.pageReload()}})""",msg='!!Invalid Access',_onStart=True)
            return 
        root.attributes['overflow'] = 'hidden'
        if self.root_page_id:
            if custom_index:
                getattr(self,'index_%s' %custom_index)(root)
            else:
                self.index_dashboard(root)
        else:         
            sc = root.stackContainer(selectedPage='^indexStack',
                subscribe_openApplicationPage="this.widget.switchPage('dashboard')",
                subscribe_openFrontPage="this.widget.switchPage('frontpage')")
            sc.loginPage(new_window=new_window,gnrtoken=gnrtoken)
            sc.contentPane(pageName='dashboard',overflow='hidden').remote(self.remoteFrameRoot,custom_index='=gnr.rootenv.custom_index',**kwargs)
            root.screenLockDialog()
        
    @struct_method
    def frm_screenLockDialog(self,pane):
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
        fb.dataRpc('.result',self.frm_checkPwd,password='=.password',user='=gnr.avatar.user',_fired='^.checkPwd')
        fb.dataController("""if(!authResult){
                                genro.publish('failed_screenout',{'message':error_msg});
                            }else{
                                dlg.hide();
                            }
                            btn.setAttribute('disabled',false);
                            
                            """,authResult='^.result',btn=btn,dlg=dlg.js_widget,error_msg='!!Wrong password')

    @public_method  
    def frm_checkPwd(self,user=None,password=None):
        validpwd = self.application.getAvatar(user, password=password,authenticate=True)
        if not validpwd:
            return False
        return True

    @public_method  
    def remoteFrameRoot(self,pane,custom_index=None,**kwargs):
        pageAuth = self.application.checkResourcePermission(self.pageAuthTags(method='page'),self.avatar.user_tags) 
        if pageAuth:
            pane.dataController("FIRE gnr.onStart;",_onBuilt=True,_delay=1)
            if self.avatar.user != self.avatar.user_id:
                usernotification_tbl = self.db.table('adm.user_notification')
                usernotification_tbl.updateGenericNotification(self.avatar.user_id,user_tags=self.avatar.user_tags)
                notification_id = usernotification_tbl.nextUserNotification(user_id=self.avatar.user_id) if self.avatar.user_id else None
                self.pageSource().dataController('loginManager.notificationManager(notification_id);',notification_id=notification_id or False,_onStart=1,_if='notification_id')
            if custom_index and custom_index!='*':
                getattr(self,'index_%s' %custom_index)(pane,**kwargs)
            else:
                pane.frameIndexRoot(**kwargs)
        else:
            pane.div('Not allowed')
    
    @struct_method
    def frm_frameIndexRoot(self,pane,onCreatingTablist=None,**kwargs):
        pane.dataController("""var d = data.deepCopy();
                            if(deltaDays(new Date(),d.getItem('workdate'))==0){
                                d.setItem('workdate','');
                            }
                            var str = dataTemplate(tpl,d);
                            
                            SET gnr.windowTitle = str;
                            """,
                            data='=gnr.rootenv',
                            tpl=self.windowTitleTemplate(),
                            _onStart=True)
        frame = pane.framePane('standard_index',_class='hideSplitter frameindexroot',
                                #border='1px solid gray',#rounded_top=8,
                                margin='0px',overflow='hidden',
                                persist=True,
                                selfsubscribe_toggleLeft="""this.getWidget().setRegionVisible("left",'toggle');""",
                                selfsubscribe_hideLeft="""this.getWidget().setRegionVisible("left",false);""",
                                subscribe_setIndexLeftStatus="""var delay = $1===true?0: 500;
                                                                var set = $1;                           
                                                                if(typeof($1)=='number'){
                                                                    set = false;
                                                                    delay = $1;
                                                                }
                                                                var wdg = this.getWidget();
                                                                setTimeout(function(){
                                                                        wdg.setRegionVisible("left",set);
                                                                },delay);""",
                                selfsubscribe_showLeft="""this.getWidget().setRegionVisible("left",true);""")
        self.prepareLeft(frame.left)
        self.prepareTop(frame.top,onCreatingTablist=onCreatingTablist)
        self.prepareBottom(frame.bottom)
        self.prepareCenter(frame.center)
        return frame
        
    def prepareTop(self,pane,onCreatingTablist=None):
        pane.attributes.update(dict(height='30px',overflow='hidden',gradient_from='gray',gradient_to='silver',gradient_deg=90))
        bc = pane.borderContainer(margin_top='4px') 
        leftbar = bc.contentPane(region='left',overflow='hidden').div(display='inline-block', margin_left='10px')  
        for btn in ['menuToggle']+self.plugin_list.split(','):
            getattr(self,'btn_%s' %btn)(leftbar)
            
        if self.custom_plugin_list:
            for btn in self.custom_plugin_list.split(','):
                getattr(self,'btn_%s' %btn)(leftbar)
                
        rightbar = bc.contentPane(region='right',overflow='hidden').div(display='inline-block', margin_right='10px')
        for btn in ['refresh','delete','newWindow']:
            getattr(self,'btn_%s' %btn)(rightbar)
        
        self.prepareTablist(bc.contentPane(region='center'),onCreatingTablist=onCreatingTablist)
        
    def prepareTablist(self,pane,onCreatingTablist=False):

        menu = pane.div().menu(modifiers='Shift',_class='smallMenu',id='_menu_tab_opt_',
                                action="genro.framedIndexManager.menuAction($1,$2,$3);")
        menu.menuline('!!Add to favorites',code='fav')
        menu.menuline('!!Set as start page',code='start')
        menu.menuline('!!Detach',code='detach') 
        menu.menuline('!!Remove from favorites',code='remove')
        menu.menuline('!!Clear favorites',code='clearfav')
        box = pane.div(zoomToFit='x',overflow='hidden')
        tabroot = box.div(connect_onclick="""
                                            if(genro.dom.getEventModifiers($1)=='Shift'){
                                                return;
                                            }
                                            if($1.target==this.domNode){
                                                return;
                                            }
                                            var targetSource = $1.target.sourceNode;
                                            var pageName = targetSource.inheritedAttribute("pageName");
                                            this.setRelativeData("selectedFrame",pageName);

                                            """,margin_left='20px',
                                            nodeId='frameindex_tab_button_root',white_space='nowrap')
        pane.dataController("""if(!data){
                                    if(indexTab){
                                        genro.callAfter(function(){
                                            var data = new gnr.GnrBag();
                                            data.setItem('indexpage',null,{'fullname':indexTab,pageName:'indexpage',fullpath:'indexpage'});
                                            this.setRelativeData("iframes",data);
                                        },1,this);
                                    }
                                }else{
                                    genro.framedIndexManager.createTablist(tabroot,data,onCreatingTablist);
                                }
                                """,
                            data="^iframes",tabroot=tabroot,indexTab=self.indexTab,
                            onCreatingTablist=onCreatingTablist or False,_onStart=True)
        pane.dataController("genro.framedIndexManager.loadFavorites();",_onStart=100)
        pane.dataController("""  var iframetab = tabroot.getValue().getNode(page);
                                    if(iframetab){
                                        genro.dom.setClass(iframetab,'iframetab_selected',selected);                                        
                                        var node = genro._data.getNode('iframes.'+page);
                                        var treeItem = genro.getDataNode(node.attr.fullpath);
                                        if(!treeItem){
                                            return;
                                        }
                                        var labelClass = treeItem.attr.labelClass;
                                        labelClass = selected? labelClass+ ' menu_current_page': labelClass.replace('menu_current_page','')
                                        treeItem.setAttribute('labelClass',labelClass);
                                    }
                                    """,subscribe_iframe_stack_selected=True,tabroot=tabroot,_if='page')

    def prepareBottom(self,pane):
        pane.attributes.update(dict(overflow='hidden',background='silver'))
        sb = pane.slotToolbar('3,applogo,genrologo,5,devlink,5,count_errors,5,appInfo,*,debugping,5,preferences,screenlock,logout,3',_class='slotbar_toolbar framefooter',height='20px',
                        gradient_from='gray',gradient_to='silver',gradient_deg=90)
        sb.appInfo.div('^gnr.appInfo')
        applogo = sb.applogo.div()
        if hasattr(self,'application_logo'):
            applogo.img(src=self.application_logo,height='20px')
        sb.genrologo.img(src='/_rsrc/common/images/made_with_genropy.png',height='20px')
        sb.dataController("""SET gnr.appInfo = dataTemplate(tpl,{msg:msg,dbremote:dbremote}); """,
            msg="!!Connected to:",dbremote=(self.site.remote_db or False),_if='dbremote',
                        tpl="<div class='remote_db_msg'>$msg $dbremote</div>",_onStart=True)


        box = sb.preferences.div(_class='iframeroot_pref')
        appPref = box.div(innerHTML='==_owner_name || "Preferences";',_owner_name='^gnr.app_preference.adm.instance_data.owner_name',_class='iframeroot_appname',
                                connect_onclick='PUBLISH app_preference')
        userPref = box.div(self.user if not self.isGuest else 'guest', _class='iframeroot_username',tip='!!%s preference' % (self.user if not self.isGuest else 'guest'),
                               connect_onclick='PUBLISH user_preference')
        sb.logout.div(connect_onclick="genro.logout()",_class='iconbox icnBaseUserLogout',tip='!!Logout')
        sb.screenlock.div(connect_onclick="genro.publish('screenlock')",_class='iconbox icnBaseUserPause',tip='!!Lock screen')

        formula = '==(_iframes && _iframes.len()>0)?_iframes.getNode(_selectedFrame).attr.url:"";'
        
        sb.count_errors.div('^gnr.errors?counter',hidden='==!_error_count',_error_count='^gnr.errors?counter',
                            _msg='!!Errors:',_class='countBoxErrors',connect_onclick='genro.dev.errorPalette();')
        sb.devlink.a(href=formula,_iframes='=iframes',_selectedFrame='^selectedFrame').div(_class="iconbox flash",tip='!!Open the page outside frame',_tags='_DEV_')
        
        appPref.dataController("""genro.dlg.iframePalette({top:'10px',left:'10px',url:url,
                                                        title:preftitle,height:'450px', width:'800px',
                                                        palette_nodeId:'mainpreference'});""",
                            subscribe_app_preference=True,url='adm/app_preference',
                            _tags=self.pageAuthTags(method='preference'),pane=appPref,preftitle='!!Application preference')
       # dlg = self.frm_envDataDialog()
        userPref.dataController("""genro.dlg.iframePalette({top:'10px',right:'10px',title:preftitle,url:url,
                                                        height:'300px', width:'400px',palette_transition:null,
                                                        palette_nodeId:'userpreference'});""",url='adm/user_preference',
                            subscribe_user_preference=True,pane=userPref,preftitle='!!User preference')


        sb.debugping.div(_class='ping_semaphore')
                            
    def prepareCenter(self,pane):
        sc = pane.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack',
                                #border_left='1px solid silver',
                                onCreated='genro.framedIndexManager = new gnr.FramedIndexManager(this);',_class='frameindexcenter')
        sc.dataController("""setTimeout(function(){
                                genro.framedIndexManager.selectIframePage(selectIframePage[0])
                            },1);""",subscribe_selectIframePage=True)

        scattr = sc.attributes
        scattr['subscribe_reloadFrame'] = """var currentPage = GET selectedFrame
                                            if(currentPage=='indexpage'){
                                                genro.pageReload();
                                                return;
                                            }
                                            genro.framedIndexManager.reloadSelectedIframe(currentPage,$1);
                                            """
        scattr['subscribe_closeFrame'] = "genro.framedIndexManager.deleteFramePage(GET selectedFrame);"        
        scattr['subscribe_destroyFrames'] = """
                        var sc = this.widget;
                        for (var k in $1){
                            var node = genro._data.popNode('iframes.'+k);
                            this.getValue().popNode(k);
                        }
                        """
        scattr['subscribe_changeFrameLabel']='genro.framedIndexManager.changeFrameLabel($1);'
        page = self.pageSource()   
        if getattr(self,'index_dashboard',None):
            self.index_dashboard(sc.contentPane(pageName='indexpage'))
        else:
            indexpane = sc.contentPane(pageName='indexpage',title='Index',overflow='hidden')
            if self.index_url:
                indexpane.iframe(height='100%', width='100%', src=self.getResourceUri(self.index_url), border='0px')         
        page.dataController("""genro.publish('selectIframePage',_menutree__selected[0]);""",
                               subscribe__menutree__selected=True)
                       
    def prepareLeft(self,pane):
        pane.attributes.update(dict(splitter=True,width='210px',datapath='left',
                                    margin_right='-4px',overflow='hidden',hidden=self.hideLeftPlugins,border_right='1px solid #ddd'))
        bc = pane.borderContainer()
        
        #self.rootSummaryBox(bc.contentPane(region='bottom',_class='login_summarybox'))
        
        
        sc = bc.stackContainer(selectedPage='^.selected',nodeId='gnr_main_left_center',
                                subscribe_open_plugin="""SET .selected=$1;
                                                         genro.getFrameNode('standard_index').publish('showLeft');""",
                                overflow='hidden',region='center')
        sc.dataController("""if(!page){return;}
                             genro.publish(page+'_'+(selected?'on':'off'));
                             genro.dom.setClass(genro.nodeById('plugin_block_'+page).getParentNode(),'iframetab_selected',selected);
                             """,subscribe_gnr_main_left_center_selected=True)
        sc.dataController("""var command= main_left_status[0]?'open':'close';
                             genro.publish(page+'_'+(command=='open'?'on':'off'));
                             """,subscribe_main_left_status=True,page='=.selected') 
        for plugin in self.plugin_list.split(','):
            cb = getattr(self, 'mainLeft_%s' % plugin,None)
            if not cb:
                return
            assert cb, 'Plugin %s not found' % plugin
            cb(sc.contentPane(pageName=plugin,overflow='hidden'))
            sc.dataController("""PUBLISH main_left_set_status = true;
                                 SET .selected=plugin;
                                 """, **{'subscribe_%s_open' % plugin: True, 'plugin': plugin})


    def btn_menuToggle(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='application_menu',tip='!!Show/Hide the left pane',
                                                      connect_onclick="""genro.getFrameNode('standard_index').publish('toggleLeft');""")

    def btn_refresh(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameRefresh',tip='!!Refresh the current page',
                                                      connect_onclick="PUBLISH reloadFrame=genro.dom.getEventModifiers($1);")               

    def btn_delete(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameDelete',tip='!!Close the current page',
                                                      connect_onclick='PUBLISH closeFrame;')
    
    def btn_newWindow(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='plus',tip='!!New Window',connect_onclick='genro.openBrowserTab(genro.addParamsToUrl(window.location.href,{new_window:true}));')

    def windowTitle(self):
        return self.package.attributes.get('name_long')
        
    def windowTitleTemplate(self):
        return "%s $workdate" %self.package.attributes.get('name_long')
        
class FramedIndexLogin(BaseComponent):
    """docstring for FramedIndexLogin"""

    def loginboxPars(self):
        return dict(width='320px',_class='index_loginbox',shadow='5px 5px 20px #555',rounded=10)

    def rootSummaryBox(self,pane):
        pane.div(innerHTML='==rootenv.getFormattedValue();',rootenv='^gnr.rootenv',
                    height='80px',margin='3px',border='1px solid silver')


    def loginSubititlePane(self,pane):
        pass
        
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
                            color='silver',font_size='12px',height='15px')
        footer.dataController("dlg_lp.hide();dlg_login.show();",_fired='^back_login',
                        dlg_login=dlg_login.js_widget,dlg_lp=dlg.js_widget)
            
        return dlg

    def login_newPassword(self,pane,gnrtoken=None,dlg_login=None):
        dlg = pane.dialog(_class='lightboxDialog')
        box = dlg.div(**self.loginboxPars())
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        topbar.wtitle.div('!!New Password')  
        fb = box.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='4px',onEnter='FIRE set_new_password;',
                                datapath='new_password',width='100%',
                                fld_width='100%',row_height='3ex')
        fb.data('.gnrtoken',gnrtoken)
        fb.textbox(value='^.password',lbl='!!New Password',type='password')
        fb.textbox(value='^.password_confirm',lbl='!!Confirm New Password',type='password',
                    validate_call='return value==GET .password;',validate_call_message='!!Passwords must be equal')
        fb.div(width='100%',position='relative',row_hidden=False).button('!!Send',action='FIRE set_new_password',position='absolute',right='-5px',top='8px')
        fb.dataRpc('dummy',self.login_changePassword,_fired='^set_new_password',
                    password='=.password',password_confirm='=.password_confirm',
                    _if='password==password_confirm',
                    _else="genro.dlg.floatingMessage(sn,{message:'Passwords must be equal',messageType:'error',yRatio:.95})",
                    gnrtoken=gnrtoken,_onResult='genro.pageReload()')
        return dlg


    def login_confirmUserDialog(self,pane,gnrtoken=None,dlg_login=None):
        dlg = pane.dialog(_class='lightboxDialog')
        sc = dlg.stackContainer(**self.loginboxPars())
        box = sc.contentPane()
        sc.contentPane().div(self.loginPreference['check_email'],_class='index_logintitle',text_align='center',margin_top='50px')
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        topbar.wtitle.div(self.loginPreference['confirm_user_title'] or '!!Confirm User')  
        box.div(self.loginPreference['confirm_user_message'],padding='10px',color='#777',font_style='italic',font_size='.9em',text_align='center')
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
        
        
    def login_newUser(self,pane):
        dlg = pane.dialog(_class='lightboxDialog',
                            subscribe_openNewUser='this.widget.show(); genro.formById("newUser_form").newrecord();',
                            subscribe_closeNewUser='this.widget.hide();')
        kw = self.loginboxPars()
        kw['width'] = '400px'
        kw['height'] = '250px'
        form = dlg.frameForm(frameCode='newUser',datapath='new_user',store='memory',**kw)
        form.dataController("PUT creating_new_user = false;",_fired='^#FORM.controller.loaded')
        topbar = form.top.slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        topbar.wtitle.div('!!New User')  
        fb = form.record.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='6px',onEnter='SET creating_new_user = true;',
                                width='100%',tdl_width='6em',fld_width='100%',row_height='3ex')
        fb.textbox(value='^.firstname',lbl='!!First name',validate_notnull=True,validate_case='c',validate_len='2:')
        fb.textbox(value='^.lastname',lbl='!!Last name',validate_notnull=True,validate_case='c',validate_len='2:')
        fb.textbox(value='^.email',lbl='!!Email',validate_notnull=True)
        fb.textbox(value='^.username',lbl='!!Username',validate_notnull=True,validate_nodup='adm.user.username',validate_len='4:')

        fb.div(width='100%',position='relative',row_hidden=False).button('!!Send',action='SET creating_new_user = true;',position='absolute',right='-5px',top='8px')
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
        footer = form.bottom.slotBar('12,loginbtn,*',height='18px',width='100%',tdl_width='6em')
        footer.loginbtn.div('!!Login',cursor='pointer',connect_onclick="genro.publish('closeNewUser');genro.publish('openLogin');",
                            color='silver',font_size='12px',height='15px')
        return dlg

    @public_method
    def login_createNewUser(self,data=None,**kwargs):
        try:
            data['status'] = 'new'
            self.db.table('adm.user').insert(data)
            data['link'] = self.externalUrlToken(self.site.homepage, userid=data['id'],max_usages=1)
            data['greetings'] = data['firstname'] or data['lastname']
            email = data['email']
            body = self.loginPreference['confirm_user_tpl'] or 'Dear $greetings to confirm click $link'
            self.getService('mail').sendmail_template(data,to_address=email,
                                body=body, subject=self.loginPreference['subject'] or 'Confirm user',
                                async=False,html=True)
            self.db.commit()
        except Exception,e:
            return dict(error=str(e))
        return dict(ok=self.loginPreference['new_user_ok_message'] or 'Check your email to confirm')

    @property
    def loginPreference(self):
        if not hasattr(self,'_loginPreference'):
            self._loginPreference = self.getPreference('general',pkg='adm') or Bag()
        return self._loginPreference


    @struct_method
    def login_loginPage(self,sc,new_window=None,gnrtoken=None):
        pane = sc.contentPane(overflow='hidden',pageName='frontpage') 
        homePageHandler = getattr(self,'homePagePane',None)
        loginOnBuilt= homePageHandler is None

        if homePageHandler:
            homePageHandler(pane)

        elif self.index_url:
            pane.iframe(height='100%', width='100%', src=self.getResourceUri(self.index_url), border='0px')   
        dlg = pane.dialog(_class='lightboxDialog',subscribe_openLogin="this.widget.show()",subscribe_closeLogin="this.widget.hide()")
       
        box = dlg.div(**self.loginboxPars())
        if not loginOnBuilt:
            dlg.div(_class='dlg_closebtn',connect_onclick='PUBLISH closeLogin;')
        doLogin = self.avatar is None and self.auth_page
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        wtitle = (self.loginPreference['login_title'] or self.login_title) if doLogin else (self.loginPreference['new_window_title'] or self.new_window_title) 
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
                                    if (!avatar){
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
        if hasattr(self,'rootenvForm'):
            self.rootenvForm(fb)
        for fbnode in fb.getNodes()[start:]:
            if fbnode.attr['tag']=='tr':
                fbnode.attr['hidden'] = '==!_avatar || _hide'
                fbnode.attr['_avatar'] = '^gnr.avatar.user'
                fbnode.attr['_hide'] = '%s?hidden' %fbnode.value['#1.#0?value']
                
        pane.dataController("""
                            var href = window.location.href;
                            if(window.location.search){
                                href = href.replace(window.location.search,'');
                                window.history.replaceState({},document.title,href);
                            }
                            if(startPage=='frontpage'){
                                if(new_password){
                                    newPasswordDialog.show();
                                }else if(loginOnBuilt){
                                    PUBLISH openLogin;
                                }
                            }else if(loginOnBuilt){
                                PUBLISH openApplicationPage;
                            }
                            """,_onBuilt=True,
                            loginOnBuilt= loginOnBuilt,
                            new_password=gnrtoken or False,
                            loginDialog = dlg.js_widget,
                            newPasswordDialog = self.login_newPassword(pane,gnrtoken=gnrtoken,dlg_login=dlg).js_widget,
                            sc=sc.js_widget,fb=fb,
                            _if='indexStack=="frontpage"',indexStack='^indexStack',
                            startPage=self._getStartPage(new_window))


        btn = fb.div(width='100%',position='relative',row_hidden=False).button('!!Enter',action='FIRE do_login',position='absolute',right='-5px',top='8px')
        dlg.dataController("genro.dlg.floatingMessage(sn,{message:message,messageType:'error',yRatio:.95})",subscribe_failed_login_msg=True,sn=dlg)

        footer = box.div().slotBar('12,lost_password,*,new_user,12',height='18px',width='100%',tdl_width='6em')
        lostpass = footer.lost_password.div()
        new_user = footer.new_user.div()
        if self.loginPreference['forgot_password']:
            lostpass.div('!!Lost password',cursor='pointer',connect_onclick='FIRE lost_password_dlg;',
                            color='silver',font_size='12px',height='15px')
            lostpass.dataController("dlg_login.hide();dlg_lp.show();",_fired='^lost_password_dlg',dlg_login=dlg.js_widget,dlg_lp=self.login_lostPassword(pane,dlg).js_widget)
        if self.loginPreference['new_user']:
            self.login_newUser(pane)
            new_user.div('!!New User',cursor='pointer',connect_onclick='genro.publish("closeLogin");genro.publish("openNewUser");',
                            color='silver',font_size='12px',height='15px')

        pane.dataController("dlg_login.hide();dlg_cu.show();",dlg_login=dlg.js_widget,
                    dlg_cu=self.login_confirmUserDialog(pane,dlg).js_widget,subscribe_confirmUserDialog=True)


        footer.dataController("""
        btn.setAttribute('disabled',true);
        var result = genro.serverCall(rpcmethod,{'rootenv':rootenv,login:login},null,null,'POST');
        if (!result){
            genro.publish('failed_login_msg',{'message':error_msg});
            btn.setAttribute('disabled',false);
        }else if(result.error){
            genro.publish('failed_login_msg',{'message':result.error});
            btn.setAttribute('disabled',false);
        }else{
            dlg.hide();
            rootpage = rootpage || result['rootpage'];
            if(rootpage){
                genro.gotoURL(rootpage);
            }
            if(loginOnBuilt){
                PUBLISH openApplicationPage;
            }
            
            genro.publish('logged');
        }
        """,rootenv='=gnr.rootenv',_fired='^do_login',rpcmethod=rpcmethod,login='=_login',_if='avatar',
            avatar='=gnr.avatar',_else="genro.publish('failed_login_msg',{'message':error_msg});",
            rootpage='=gnr.rootenv.rootpage',loginOnBuilt=loginOnBuilt,
            error_msg=self.login_error_msg,dlg=dlg.js_widget,btn=btn.js_widget,_delay=1)  
        return dlg

    @public_method
    def login_doLogin(self, rootenv=None,login=None,guestName=None, **kwargs): 
        self.doLogin(login=login,guestName=guestName,rootenv=rootenv,**kwargs)
        if self.avatar:
            rootenv['user'] = self.avatar.user
            rootenv['user_id'] = self.avatar.user_id
            rootenv['workdate'] = rootenv['workdate'] or self.workdate
            rootenv['language'] = rootenv['language'] or self.language
            self.connectionStore().setItem('defaultRootenv',rootenv) #no need to be locked because it's just one set
            return self.login_newWindow(rootenv=rootenv)
        return dict(error=login['error']) if login['error'] else False

    @public_method
    def login_checkAvatar(self,password=None,user=None,serverTimeDelta=None,**kwargs):
        result = Bag()
        avatar = self.application.getAvatar(user, password=password,authenticate=True)
        if not avatar:
            return result
        status = getattr(avatar,'status',None)
        if not status:
            avatar.extra_kwargs['status'] = 'conf'
        result['avatar'] = Bag(avatar.as_dict())
        if avatar.status != 'conf':
            return result
        data = Bag()
        data['serverTimeDelta'] = serverTimeDelta
        self.onUserSelected(avatar,data)
        canBeChanged = self.application.checkResourcePermission(self.pageAuthTags(method='workdate'),avatar.user_tags)
        data.setItem('workdate',self.workdate, hidden= not canBeChanged)
        result['rootenv'] = data
        return result

    def onUserSelected(self,avatar,data=None):
        return
    
    def automaticLogin(self,rootenv=None):
        return False
        
    def _getStartPage(self,new_window):
        startPage = 'dashboard'        
        if not self.avatar and self.auth_page:
            newrootenv = Bag()
            autologin = self.automaticLogin(newrootenv)
            if autologin:
                authenticate = autologin.pop('_authenticate',True)
                self.doLogin(autologin,authenticate=authenticate)
                canBeChanged = self.application.checkResourcePermission(self.pageAuthTags(method='workdate'),self.avatar.user_tags)
                newrootenv.setItem('workdate',self.workdate, hidden= not canBeChanged,editable=True)
                self.pageStore().setItem('rootenv',newrootenv)
                self.connectionStore().setItem('defaultRootenv',Bag(newrootenv))
            else:
                return 'frontpage'
        elif new_window:
            for n in self.rootenv:
                if n.attr.get('editable') and not n.attr.get('hidden'):
                    startPage = 'frontpage'
                    break               
        return startPage

    @public_method
    def login_newWindow(self, rootenv=None, **kwargs): 
        td = date.today()
        rootenv['workdate'] = rootenv['workdate'] or td
        if rootenv['workdate'] != td:
            rootenv['custom_workdate'] = True
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
        body = self.loginPreference['confirm_user_tpl'] or 'Dear $greetings to confirm click $link'
        self.getService('mail').sendmail_template(recordBag,to_address=email,
                                body=body, subject=self.loginPreference['subject'] or 'Password recovery',
                                async=False,html=True)
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
        for u in users:
            userid = u['id']
            recordBag = usertbl.record(userid).output('bag')
            recordBag['link'] = self.externalUrlToken(self.site.homepage, userid=recordBag['id'],max_usages=1)
            self.db.commit()
            recordBag['greetings'] = recordBag['firstname'] or recordBag['lastname']
            body = self.loginPreference['confirm_password_tpl'] or 'Dear $greetings set your password $link'

            self.getService('mail').sendmail_template(recordBag,to_address=email,
                                    body=body, subject=self.loginPreference['confirm_password_subject'] or 'Password recovery',
                                    async=False,html=True)
        return 'ok'
            #self.sendMailTemplate('confirm_new_pwd.xml', recordBag['email'], recordBag)

    @public_method
    def login_changePassword(self,password=None,gnrtoken=None,**kwargs):
        if not gnrtoken:
            return
        method,args,kwargs,user_id = self.db.table('sys.external_token').use_token(gnrtoken)
        if kwargs.get('userid'):
            self.db.table('adm.user').batchUpdate(dict(status='conf',md5pwd=password),_pkeys=kwargs['userid'])
        self.db.commit()

                                                      