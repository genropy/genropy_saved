# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag

class FrameIndex(BaseComponent):
    py_requires="""foundation/menu:MenuIframes,
                   gnrcomponents/batch_handler/batch_handler:TableScriptRunner,
                   gnrcomponents/batch_handler/batch_handler:BatchMonitor,
                   gnrcomponents/chat_component/chat_component,
                   gnrcomponents/datamover:MoverPlugin
                   """
    js_requires='frameindex'
    css_requires='frameindex,public'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin,datamover'
    custom_plugin_list = None
    index_url = None
    indexTab = False
    hideLeftPlugins = False
    preferenceTags = 'admin'
    authTags=''
    
    login_error_msg = '!!Invalid login'
    
    def windowTitle(self):
        return ''
    
    def pageAuthTags(self, method=None, **kwargs):
        print method,kwargs
    
    def mainLeftContent(self,*args,**kwargs):
        pass
    
    def main(self,root,**kwargs):
        if self.root_page_id:
            self.index_dashboard(root)
        else:
            sc = root.stackContainer()
            sc.loginPage()
            sc.contentPane().remote(self.remoteFrameRoot,**kwargs)
            
    @public_method  
    def remoteFrameRoot(self,pane,**kwargs):
        pane.frameIndexRoot(**kwargs)
    
    @struct_method
    def frm_frameIndexRoot(self,pane,onCreatingTablist=None,**kwargs):
        frame = pane.framePane('standard_index',_class='hideSplitter frameindexroot',
                                #border='1px solid gray',#rounded_top=8,
                                margin='0px',
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
        tabroot = pane.div(connect_onclick="""
                                            var targetSource = $1.target.sourceNode;
                                            var pageName = targetSource.inheritedAttribute("pageName");
                                            this.setRelativeData("selectedFrame",pageName);
                                            """,margin_left='20px',display='inline-block',nodeId='frameindex_tab_button_root')
        tabroot.div()
        pane.dataController("""
                                if(!data){
                                    if(indexTab){
                                        data = new gnr.GnrBag();
                                        data.setItem('indexpage',null,{'fullname':indexTab,pageName:'indexpage',fullpath:'indexpage'});
                                        SET iframes = data;
                                    }
                                }else{
                                    genro.framedIndexManager.createTablist(tabroot,data,onCreatingTablist);
                                }
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
        sb = pane.slotToolbar('5,appName,*,messageBox,*,devlink,user,logout,5',_class='slotbar_toolbar framefooter',
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
                            _tags=self.preferenceTags,pane=appPref,preftitle='!!Application preference')
       # dlg = self.frm_envDataDialog()
        userPref.dataController("""genro.dlg.zoomPaletteFromSourceNode(pane,null,{top:'10px',right:'10px',title:preftitle,
                                                        height:'300px', width:'400px',palette_transition:null,
                                                        palette_nodeId:'userpreference'});""",
                            subscribe_user_preference=True,pane=userPref,preftitle='!!User preference')
                            
    def prepareCenter(self,pane):
        sc = pane.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack',
                                border_left='1px solid silver',margin_left='-4px',
                                onCreated='genro.framedIndexManager = new gnr.FramedIndexManager(this);',_class='frameindexcenter')
        sc.dataController("setTimeout(function(){genro.framedIndexManager.selectIframePage(selectIframePage[0])},1);",subscribe_selectIframePage=True)

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
                                    margin_right='-1px',overflow='hidden',hidden=self.hideLeftPlugins))
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
        pane.div(_class='button_block iframetab').div(_class='plus',tip='!!New Window',connect_onclick='genro.openWindow(window.location.href);')


class FramedIndexLogin(BaseComponent):
    """docstring for FramedIndexLogin"""
    def loginboxPars(self):
        return dict(width='320px',_class='index_loginbox',shadow='5px 5px 20px #555',rounded=10)

    def rootSummaryBox(self,pane):
        pane.div(innerHTML='==rootWindowData.getFormattedValue();',rootWindowData='^rootWindowData',
                    height='80px',margin='3px',border='1px solid silver')
        
    def windowTitle(self):
        return self.package.attributes.get('name_long')
        
    def windowTitleTemplate(self):
        return "%s $workdate" %self.package.attributes.get('name_long')

    @struct_method
    def login_loginPage(self,sc):
        pane = sc.contentPane(overflow='hidden')   
        if self.index_url:
            pane.iframe(height='100%', width='100%', src=self.getResourceUri(self.index_url), border='0px')             
        dlg = pane.dialog(_class='lightboxDialog')
        sc.dataController("""loginDialog.show();""",_onStart=True,
                            curravatar='=gnr.avatar',authTags=self.authTags,_if='authTags',
                            loginDialog = dlg.js_widget,sc=sc.js_widget)        
        box = dlg.div(**self.loginboxPars())
        doLogin = self.avatar is None
        topbar = box.div().slotBar('*,wtitle,*',_class='index_logintitle',height='30px') 
        wtitle = '!!Login' if doLogin else '!!New Window'  
        topbar.wtitle.div(wtitle)  
        fb = box.div(margin='10px',margin_right='20px',padding='10px').formbuilder(cols=1, border_spacing='4px',onEnter='FIRE do_login;',
                                datapath='rootWindowData',width='100%',fld_width='100%',row_height='3ex',keeplabel=True)
        rpcmethod = self.login_newWindow
        if doLogin:
            fb.textbox(value='^loginData.user',lbl='!!Username')
            fb.textbox(value='^loginData.password',lbl='!!Password',type='password',validate_remote=self.login_onPassword,validate_user='=loginData.user')
            rpcmethod = self.login_doLogin
            defaultRootWindowData = Bag(dict(workdate=self.workdate))
        else:
            defaultRootWindowData = self.connectionStore().getItem('defaultRootWindowData')
            
        fb.data('rootWindowData',defaultRootWindowData)
            
        fb.dateTextBox(value='^.workdate',lbl='!!Workdate')
        if hasattr(self,'rootWindowDataForm'):
            self.rootWindowDataForm(fb)
        
        btn = fb.div(width='100%',position='relative').button('!!Enter',action='FIRE do_login',position='absolute',right='-5px',top='8px')

        footer = box.div().slotBar('*,messageBox,*',messageBox_subscribeTo='failed_login_msg',height='18px',width='100%',tdl_width='6em')
        footer.dataController("""
        btn.widget.setDisabled(true);
        genro.serverCall(rpcmethod,{'login':loginData,rootWindowData:rootWindowData},function(result){
            if (!result){
                genro.publish('failed_login_msg',{'message':error_msg});
                btn.widget.setDisabled(false);
            }else{
                dlg.hide();
                sc.switchPage(1);
                genro.publish('logged');
            }
        })
        """,loginData='=loginData',rootWindowData='=rootWindowData',_fired='^do_login',rpcmethod=rpcmethod,
            error_msg=self.login_error_msg,dlg=dlg.js_widget,sc=sc.js_widget,btn=btn)  
        
        footer.dataFormula("gnr.windowTitle", "dataTemplate(tpl,data)",data='=rootWindowData',
                            tpl=self.windowTitleTemplate(),subscribe_logged=True)
            
        return dlg

    @public_method
    def login_doLogin(self, login=None,rootWindowData=None,guestName=None, **kwargs): 
        self.doLogin(login=login,guestName=guestName,**kwargs)
        if self.avatar:
            with self.connectionStore() as store:
                store.setItem('defaultRootWindowData',rootWindowData)
            return self.login_newWindow(rootWindowData=rootWindowData)
    
    @public_method
    def login_onPassword(self,value=None,user=None,**kwargs):
        avatar = self.application.getAvatar(user, password=value,authenticate=True)
        if not avatar:
            return False
        data=self.onUserSelected(avatar)
        if data:
            return Bag(dict(data=data))
        return True
        
    def onUserSelected(self,avatar):
        return
    
    @public_method
    def login_newWindow(self, rootWindowData=None, **kwargs): 
        self.workdate = rootWindowData.pop('workdate')
        with self.pageStore() as store:
            store.update(rootWindowData)
        return True
                    

                                                      