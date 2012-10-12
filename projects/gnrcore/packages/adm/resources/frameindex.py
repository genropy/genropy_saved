# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from datetime import datetime
from gnr.core.gnrbag import Bag

class FrameIndex(BaseComponent):
    py_requires="""foundation/menu:MenuIframes,
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
    index_url = None
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
            
    
    def main(self,root,new_window=None,**kwargs):
        root.attributes['overflow'] = 'hidden'
        if self.root_page_id:
            self.index_dashboard(root)
        else:         
            sc = root.stackContainer(selectedPage='^indexStack')
            sc.loginPage(new_window=new_window)
            sc.contentPane(pageName='dashboard').remote(self.remoteFrameRoot,**kwargs)
        
            
    @public_method  
    def remoteFrameRoot(self,pane,**kwargs):
        pageAuth = self.application.checkResourcePermission(self.pageAuthTags(method='page'),self.avatar.user_tags)
        if pageAuth:
            pane.dataController("FIRE gnr.onStart;",_onBuilt=True,_delay=1)
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
                                subscribe_setIndexLeftStatus="""this.getWidget().setRegionVisible("left",$1);""",
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
        menu.menuline('!!Clear favorites',code='clear')

        tabroot = pane.div(connect_onclick="""
                                            if(genro.dom.getEventModifiers($1)=='Shift'){
                                                return;
                                            }
                                            var targetSource = $1.target.sourceNode;
                                            var pageName = targetSource.inheritedAttribute("pageName");
                                            this.setRelativeData("selectedFrame",pageName);

                                            """,margin_left='20px',display='inline-block',nodeId='frameindex_tab_button_root')
        tabroot.div()
        pane.dataController("""
                                if(!data){
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
                                genro.framedIndexManager.loadFavorites();
                                """,
                            data="^iframes",tabroot=tabroot,indexTab=self.indexTab,
                            onCreatingTablist=onCreatingTablist or False,_onStart=True)
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
        sb = pane.slotToolbar('5,appName,*,messageBox,*,devlink,user,logout,5',_class='slotbar_toolbar framefooter',height='20px',
                        messageBox_subscribeTo='rootmessage',gradient_from='gray',gradient_to='silver',gradient_deg=90)
        appPref = sb.appName.div(innerHTML='==_owner_name || "Preferences";',_owner_name='^gnr.app_preference.adm.instance_data.owner_name',_class='footer_block',
                                connect_onclick='PUBLISH app_preference',zoomUrl='adm/app_preference',pkey='Application preference')
        userPref = sb.user.div(self.user if not self.isGuest else 'guest', _class='footer_block',tip='!!%s preference' % (self.user if not self.isGuest else 'guest'),
                               connect_onclick='PUBLISH user_preference',zoomUrl='adm/user_preference',pkey='User preference')
        sb.logout.div(connect_onclick="genro.logout()",_class='application_logout',height='16px',width='20px',tip='!!Logout')
        formula = '==(_iframes && _iframes.len()>0)?_iframes.getNode(_selectedFrame).attr.url:"";'
        sb.devlink.a(href=formula,_iframes='=iframes',_selectedFrame='^selectedFrame').div(_class="iconbox flash",tip='!!Open the page outside frame',_tags='_DEV_')
        appPref.dataController("""genro.dlg.zoomPaletteFromSourceNode(pane,null,{top:'10px',left:'10px',
                                                        title:preftitle,height:'450px', width:'800px',
                                                        palette_transition:null,palette_nodeId:'mainpreference'});""",
                            subscribe_app_preference=True,
                            _tags=self.pageAuthTags(method='preference'),pane=appPref,preftitle='!!Application preference')
       # dlg = self.frm_envDataDialog()
        userPref.dataController("""genro.dlg.zoomPaletteFromSourceNode(pane,null,{top:'10px',right:'10px',title:preftitle,
                                                        height:'300px', width:'400px',palette_transition:null,
                                                        palette_nodeId:'userpreference'});""",
                            subscribe_user_preference=True,pane=userPref,preftitle='!!User preference')
                            
    def prepareCenter(self,pane):
        sc = pane.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack',
                                border_left='1px solid silver',
                                onCreated='genro.framedIndexManager = new gnr.FramedIndexManager(this);',_class='frameindexcenter')
        sc.dataController("""setTimeout(function(){
                                genro.framedIndexManager.selectIframePage(selectIframePage[0])
                            },1);""",subscribe_selectIframePage=True)

        scattr = sc.attributes
        scattr['subscribe_reloadFrame'] = """
                                            if($1=='indexpage'){
                                                genro.pageReload();
                                                return;
                                            }
                                            var frame = dojo.byId("iframe_"+$1);
                                            frame.sourceNode._genro.pageReload();
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
        pane.attributes.update(dict(splitter=True,width='200px',datapath='left',
                                    margin_right='-4px',overflow='hidden',hidden=self.hideLeftPlugins))
        bc = pane.borderContainer()
        
        #self.rootSummaryBox(bc.contentPane(region='bottom',_class='login_summarybox'))
        
        sc = bc.stackContainer(selectedPage='^.selected',nodeId='gnr_main_left_center',overflow='hidden',region='center')
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
    
    def btn_iframemenu_plugin(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='iframemenu_plugin_icon',tip='!!Menu',
                 connect_onclick="""SET left.selected='iframemenu_plugin';genro.getFrameNode('standard_index').publish('showLeft');""",
                 nodeId='plugin_block_iframemenu_plugin')
                 
    def btn_batch_monitor(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='batch_monitor_icon',tip='!!Batch monitor',
                 connect_onclick="""genro.publish('open_batch');""",
                 nodeId='plugin_block_batch_monitor')
        pane.dataController("SET left.selected='batch_monitor';genro.getFrameNode('standard_index').publish('showLeft')",subscribe_open_batch=True)
        
    def btn_chat_plugin(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='chat_plugin_icon',tip='!!Chat plug-in',
                    connect_onclick="""SET left.selected='chat_plugin';genro.getFrameNode('standard_index').publish('showLeft');""",
                    nodeId='plugin_block_chat_plugin')
    
    def btn_datamover(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='case',tip='!!Mover plug-in',
                    connect_onclick="""SET left.selected='datamover';PUBLISH gnrdatamover_loadCurrent;genro.getFrameNode('standard_index').publish('showLeft');""",
                    nodeId='plugin_block_datamover')

    def btn_maintenance(self,pane,**kwargs):
        if 'admin' in self.userTags:
            pane.div(_class='button_block iframetab').div(_class='gear',tip='!!Maintenance',
                        connect_onclick="""SET left.selected='maintenance';genro.getFrameNode('standard_index').publish('showLeft');""",
                        nodeId='plugin_block_maintenance')
                    
    def btn_menuToggle(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='application_menu',tip='!!Show/Hide the left pane',
                                                      connect_onclick="""genro.getFrameNode('standard_index').publish('toggleLeft');""")

    def btn_refresh(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameRefresh',tip='!!Refresh the current page',
                                                      connect_onclick="PUBLISH reloadFrame=GET selectedFrame;")               

    def btn_delete(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameDelete',tip='!!Close the current page',
                                                      connect_onclick='PUBLISH closeFrame;')
    
    def btn_newWindow(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='plus',tip='!!New Window',connect_onclick='genro.openWindow(genro.addParamsToUrl(window.location.href,{new_window:true}));')

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
        
    @struct_method
    def login_loginPage(self,sc,new_window=None):
        pane = sc.contentPane(overflow='hidden',pageName='login')   
        if self.index_url:
            pane.iframe(height='100%', width='100%', src=self.getResourceUri(self.index_url), border='0px')   
        dlg = pane.dialog(_class='lightboxDialog')
       
        box = dlg.div(**self.loginboxPars())
        doLogin = self.avatar is None and self.auth_page
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        wtitle = self.login_title if doLogin else self.new_window_title  
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
                        _if='user&&password',_else='SET gnr.avatar = null;',
                        _onResult="""var newenv = result.getItem('rootenv');
                                    var rootenv = GET gnr.rootenv;
                                    currenv = rootenv.deepCopy();
                                    currenv.update(newenv);
                                    SET gnr.rootenv = currenv;
                                    SET gnr.avatar = result.getItem('avatar');
                                """,sync=True,_POST=True)
            rpcmethod = self.login_doLogin    
        
        fb.dateTextBox(value='^.workdate',lbl='!!Workdate')
        if hasattr(self,'rootenvForm'):
            self.rootenvForm(fb)
        for fbnode in fb.getNodes()[start:]:
            if fbnode.attr['tag']=='tr':
                fbnode.attr['hidden'] = '==!_avatar || _hide'
                fbnode.attr['_avatar'] = '^gnr.avatar'
                fbnode.attr['_hide'] = '%s?hidden' %fbnode.value['#1.#0?value']
        
        
        pane.dataController("""
                            var href = window.location.href;
                            if(window.location.search){
                                href = href.replace(window.location.search,'');
                                window.history.replaceState({},document.title,href);
                            }
                            if(startPage=='login'){
                                loginDialog.show();
                            }else{
                                SET indexStack = 'dashboard';
                            }
                            """,_onBuilt=True,
                            loginDialog = dlg.js_widget,sc=sc.js_widget,fb=fb,
                            _if='indexStack=="login"',indexStack='^indexStack',
                            startPage=self._getStartPage(new_window))
 
        btn = fb.div(width='100%',position='relative',row_hidden=False).button('!!Enter',action='FIRE do_login',position='absolute',right='-5px',top='8px')

        footer = box.div().slotBar('*,messageBox,*',messageBox_subscribeTo='failed_login_msg',height='18px',width='100%',tdl_width='6em')
        footer.dataController("""
        btn.setAttribute('disabled',true);
        genro.serverCall(rpcmethod,{'rootenv':rootenv,login:login},function(result){
            if (!result){
                genro.publish('failed_login_msg',{'message':error_msg});
                btn.setAttribute('disabled',false);
            }else{
                dlg.hide();
                if(result['rootpage']){
                    genro.gotoURL(result['rootpage']);
                }
                sc.switchPage('dashboard');
                genro.publish('logged');
            }
        },null,'POST');
        """,rootenv='=gnr.rootenv',_fired='^do_login',rpcmethod=rpcmethod,login='=_login',_if='avatar',
            avatar='=gnr.avatar',_else="genro.publish('failed_login_msg',{'message':error_msg});",
            error_msg=self.login_error_msg,dlg=dlg.js_widget,sc=sc.js_widget,btn=btn.js_widget,_delay=1)  
        return dlg

    @public_method
    def login_doLogin(self, rootenv=None,login=None,guestName=None, **kwargs): 
        print 'prima login'
        self.doLogin(login=login,guestName=guestName,**kwargs)
        if self.avatar:
            rootenv['user'] = self.avatar.user
            rootenv['user_id'] = self.avatar.user_id
            with self.connectionStore() as store:
                store.setItem('defaultRootenv',rootenv)
            return self.login_newWindow(rootenv=rootenv)
        return False

    @public_method
    def login_checkAvatar(self,password=None,user=None,**kwargs):
        result = Bag()
        avatar = self.application.getAvatar(user, password=password,authenticate=True)
        if not avatar:
            return result
        result['avatar'] = Bag(avatar.as_dict())
        data = Bag()
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
                with self.pageStore() as pagestore:
                    pagestore.setItem('rootenv',newrootenv)
                with self.connectionStore() as connectionstore:
                    connectionstore.setItem('defaultRootenv',Bag(newrootenv))
            else:
                return 'login'
        elif new_window:
            for n in self.rootenv:
                if n.attr.get('editable') and not n.attr.get('hidden'):
                    startPage = 'login'
                    break               
        return startPage

    @public_method
    def login_newWindow(self, rootenv=None, **kwargs): 
        rootenv['workdate'] = rootenv['workdate'] or datetime.date.today()
        with self.pageStore() as store:
            store.setItem('rootenv',rootenv)
        self.db.workdate = rootenv['workdate']
        self.setInClientData('gnr.rootenv', rootenv)
        return self.avatar.as_dict()
                    

                                                      