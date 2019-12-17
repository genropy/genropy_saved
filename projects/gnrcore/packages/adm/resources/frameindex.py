# -*- coding: utf-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class FrameIndex(BaseComponent):
    py_requires="""frameplugin_menu/frameplugin_menu:MenuIframes,
                   login:LoginComponent,
                   th/th:TableHandler,
                   gnrcomponents/batch_handler/batch_handler:TableScriptRunner,
                   gnrcomponents/batch_handler/batch_handler:BatchMonitor,
                   gnrcomponents/chat_component/chat_component,
                   gnrcomponents/maintenance:MaintenancePlugin
                   """
    #gnrcomponents/datamover:MoverPlugin, removed
    js_requires='frameindex'
    css_requires='frameindex,public'
    
    custom_plugin_list = None
    index_page = False
    index_url = 'html_pages/splashscreen.html'
    indexTab = False
    hideLeftPlugins = False
    auth_preference = 'admin'
    auth_page = 'user'
    auth_main = 'user'

    @property
    def plugin_list(self):
        frameplugins = ['iframemenu_plugin','batch_monitor','chat_plugin']
        for pkgId,pkgobj in self.packages.items():
            if hasattr(pkgobj,'sidebarPlugins'):
                plugins = pkgobj.sidebarPlugins()
                if not plugins:
                    continue
                package_plugins,requires = plugins
                frameplugins.extend(package_plugins.split(','))
                if requires:
                    for p in requires.split(','):
                        self.mixinComponent(p)
        frameplugins.append('maintenance')
        return ','.join(frameplugins)

    def main(self,root,new_window=None,gnrtoken=None,custom_index=None,**kwargs):
        if gnrtoken and not self.db.table('sys.external_token').check_token(gnrtoken):
            root.dataController("""genro.dlg.alert(msg,'Error',null,null,{confirmCb:function(){
                    var href = window.location.href;
                    href = href.replace(window.location.search,'');
                    window.history.replaceState({},document.title,href);
                    genro.pageReload()}})""",msg='!!Invalid Access',_onStart=True)
            return 
        root.attributes['overflow'] = 'hidden'
        if self.root_page_id and (custom_index or hasattr(self,'index_dashboard')):
            if custom_index:
                getattr(self,'index_%s' %custom_index)(root)
            else:
                self.index_dashboard(root)
        else:         
            custom_index = self.rootenv['custom_index']
            pageAuth = self.application.checkResourcePermission(self.pageAuthTags(method='page'),self.userTags) 
            if pageAuth:
                if self.avatar and self.avatar.user != self.avatar.user_id:
                    usernotification_tbl = self.db.table('adm.user_notification')
                    usernotification_tbl.updateGenericNotification(self.avatar.user_id,user_tags=self.avatar.user_tags)
                    notification_id = usernotification_tbl.nextUserNotification(user_id=self.avatar.user_id) if self.avatar.user_id else None
                    self.pageSource().dataController('loginManager.notificationManager(notification_id);',notification_id=notification_id or False,_onStart=1,_if='notification_id')
                if custom_index and custom_index!='*':
                    getattr(self,'index_%s' %custom_index)(root,**kwargs)
                else:
                    root.frameIndexRoot(new_window=new_window,**kwargs)
            else:
                root.div('Not allowed')

    @struct_method
    def frm_frameIndexRoot(self,pane,new_window=None,onCreatingTablist=None,**kwargs):
        pane.dataController("""var d = data.deepCopy();
                            if(deltaDays(new Date(),d.getItem('workdate'))==0){
                                d.setItem('workdate','');
                            }
                            var str = dataTemplate(tpl,d);
                            SET gnr.windowTitle = str;
                            """,
                            data='^gnr.rootenv',
                            tpl=self.windowTitleTemplate(),
                            _onStart=True)
        bc = pane.borderContainer(nodeId='standard_index',_class='frameindexroot',
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
                                selfsubscribe_showLeft="""this.getWidget().setRegionVisible("left",true);""",
                                regions='^frameindex.regions')
        pane.dataController("""
                genro.setInStorage('local','frameindex_left_'+pluginSelected+'_width',currentWidth);
                """,currentWidth='^frameindex.regions.left',
                    pluginSelected='=left.selected')
        self.prepareLeft(bc)
        self.prepareTop(bc,onCreatingTablist=onCreatingTablist)
        self.prepareBottom(bc)
        self.prepareCenter(bc)
        if new_window:
            self.loginDialog(pane)
        else:
            self.login_newPassword(pane)
        return bc
        
    def prepareTop(self,bc,onCreatingTablist=None):
        bc = bc.borderContainer(region='top',height='30px',overflow='hidden',_class='framedindex_tablist')
        leftbar = bc.contentPane(region='left',overflow='hidden').div(display='inline-block', margin_left='10px',margin_top='4px')  
        for btn in ['menuToggle']+self.plugin_list.split(','):
            getattr(self,'btn_%s' %btn)(leftbar)
            
        if self.custom_plugin_list:
            for btn in self.custom_plugin_list.split(','):
                getattr(self,'btn_%s' %btn)(leftbar)
        
        self.prepareTablist(bc.contentPane(region='center',margin_top='4px'),onCreatingTablist=onCreatingTablist)
        
    def prepareTablist(self,pane,onCreatingTablist=False):

        menu = pane.div().menu(_class='smallMenu',id='_menu_tab_opt_',
                                action="genro.framedIndexManager.menuAction($1,$2,$3);")
        pane.div().menu(modifiers='*',_class='_menu_open_windows_',id='_menu_open_windows_',
                                action="genro.framedIndexManager.selectWindow($1,$2,$3);",
                                storepath='externalWindows')

        menu.menuline('!!Add to favorites',code='fav')
        menu.menuline('!!Set as start page',code='start')
        menu.menuline('!!Remove from favorites',code='remove')
        menu.menuline('!!Clear favorites',code='clearfav')
        menu.menuline('-')
        menu.menuline('!!Reload',code='reload')

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
        pane.dataController("""if(!data && !externalWindows){
                                    if(indexTab){
                                        genro.callAfter(function(){
                                            var data = new gnr.GnrBag();
                                            data.setItem('indexpage',null,{'fullname':indexTab,pageName:'indexpage',fullpath:'indexpage'});
                                            this.setRelativeData("iframes",data);
                                        },1,this);
                                    }
                                }else{
                                    genro.callAfter(function(){
                                        genro.framedIndexManager.createTablist(tabroot,data,onCreatingTablist);
                                    },200,this);

                                }
                                """,
                            data="=iframes",externalWindows='=externalWindows',_refreshTablist='^refreshTablist',tabroot=tabroot,indexTab=self.indexTab,
                            onCreatingTablist=onCreatingTablist or False,_onStart=True)
        if not self.isMobile:
            pane.dataController("genro.framedIndexManager.loadFavorites();",_onStart=100)
        pane.dataController(""" var cb = function(){
                                                var iframetab = tabroot.getValue().getNode(page);
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
                                            }
                                if(selected){
                                    setTimeout(cb,1);
                                }else{
                                    cb();
                                }
                                    
        """,subscribe_iframe_stack_selected=True,tabroot=tabroot,_if='page')

    def prepareBottom(self,bc):
        pane = bc.contentPane(region='bottom',overflow='hidden')
        sb = pane.slotToolbar('3,applogo,genrologo,5,devlink,5,manageDocumentation,5,openGnrIDE,5,appdownload,count_errors,5,appInfo,*,debugping,5,preferences,logout,3',_class='slotbar_toolbar framefooter',height='22px',
                        background='#EEEEEE',border_top='1px solid silver')
        sb.appInfo.div('^gnr.appInfo')
        applogo = sb.applogo.div()
        if hasattr(self,'application_logo'):
            applogo.div(_class='application_logo_container').img(src=self.application_logo,height='100%')
        sb.genrologo.div(_class='application_logo_container').img(src='/_rsrc/common/images/made_with_genropy_small.png',height='100%')
        sb.dataController("""SET gnr.appInfo = dataTemplate(tpl,{msg:msg,dbremote:dbremote}); """,
            msg="!!Connected to:",dbremote=(self.site.remote_db or False),_if='dbremote',
                        tpl="<div class='remote_db_msg'>$msg $dbremote</div>",_onStart=True)
        box = sb.preferences.div(_class='iframeroot_pref')
        if not self.dbstore:
            appPref = box.div(innerHTML='==_owner_name?dataTemplate(_owner_name,envbag):"Preferences";',
                                    _owner_name='^gnr.app_preference.adm.instance_data.owner_name',
                                    _class='iframeroot_appname',
                                    connect_onclick='PUBLISH app_preference',envbag='=gnr.rootenv')
            userPref = box.div(self.user if not self.isGuest else 'guest', _class='iframeroot_username',tip='!!%s preference' % (self.user if not self.isGuest else 'guest'),
                                connect_onclick='PUBLISH user_preference')
            appPref.dataController("""genro.dlg.iframePalette({top:'10px',left:'10px',url:url,
                                                        title:preftitle,height:'450px', width:'800px',
                                                        palette_nodeId:'mainpreference'});""",
                            subscribe_app_preference=True,url='adm/app_preference',
                            _tags=self.pageAuthTags(method='preference'),pane=appPref,preftitle='!!Application preference')
            userPref.dataController("""genro.dlg.iframePalette({top:'10px',right:'10px',title:preftitle,url:url,
                                                        height:'300px', width:'400px',palette_transition:null,
                                                        palette_nodeId:'userpreference'});""",url='adm/user_preference',
                            subscribe_user_preference=True,pane=userPref,preftitle='!!User preference')
        
        sb.logout.div(connect_onclick="genro.logout()",_class='iconbox icnBaseUserLogout switch_off',tip='!!Logout')

        formula = '==(_iframes && _iframes.len()>0)?_iframes.getAttr(_selectedFrame,"url"):"";'
        
        sb.count_errors.div('^gnr.errors?counter',hidden='==!_error_count',_error_count='^gnr.errors?counter',
                            _msg='!!Errors:',_class='countBoxErrors',connect_onclick='genro.dev.errorPalette();')
        sb.devlink.a(href=formula,_iframes='=iframes',_selectedFrame='^selectedFrame').div(_class="iconbox flash",tip='!!Open the page outside frame',_tags='_DEV_')
        sb.manageDocumentation.slotButton("!!Help",iconClass='iconbox help',
                            action='genro.framedIndexManager.openHelpForCurrentIframe();')
        if not self.isMobile :
            self.electronAppDownload(sb)
        sb.openGnrIDE.div().slotButton("!!Open Genro IDE",iconClass='iconbox laptop',
                            action='genro.framedIndexManager.openGnrIDE();',_tags='_DEV_')
        sb.debugping.div(_class='ping_semaphore')
    
    def electronAppDownload(self,bar):
        electron_pars = self.site.config.getAttr('electron') or {}
        name = electron_pars.get('name') or self.site.site_name
        platform = {'windows':('windows',''),'linux':('linux',''),'mac':('osx','.app')}.get(self.connection.user_device.split(':')[0])
        bar.appdownload.slotButton('!!Download desktop app',iconClass="iconbox inbox",
                                action='genro.download(appurl,{_lazydoc:"service:download_app"})',
                                appurl=self.site.getStaticUrl('site:application',
                                                             platform[0],'%s%s.zip' %(name,platform[1])))
                            
    def prepareCenter(self,bc):
        sc = bc.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack',region='center',
                                #border_left='1px solid silver',
                                margin_left='-1px',
                                onCreated='genro.framedIndexManager = new gnr.FramedIndexManager(this);',_class='frameindexcenter')
        sc.dataController("""setTimeout(function(){
                                genro.framedIndexManager.selectIframePage(selectIframePage[0])
                            },1);""",subscribe_selectIframePage=True)
        sc.dataController("genro.framedIndexManager.onSelectedFrame(selectedPage);",selectedPage='^selectedFrame')

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
                src = self.getResourceUri(self.index_url,add_mtime=self.isDeveloper())
                indexpane.htmliframe(height='100%', width='100%', src=src, border='0px',shield=True)         
        page.dataController("""genro.publish('selectIframePage',_menutree__selected[0]);""",
                               subscribe__menutree__selected=True)
        page.dataController("""genro.framedIndexManager.newBrowserWindowPage(newBrowserWindowPage[0]);""",
                               subscribe_newBrowserWindowPage=True)
                       
    def prepareLeft(self,bc):
        pane = bc.contentPane(region='left',splitter=True,width='210px',datapath='left',_lazyBuild=True,
                                    margin_right='-4px',overflow='hidden',hidden=self.hideLeftPlugins,border_right='5px solid #eee')
        sc = pane.stackContainer(selectedPage='^.selected',nodeId='gnr_main_left_center',
                                subscribe_open_plugin="""var plugin_name = $1.plugin;
                                                         SET left.selected = plugin_name;
                                                         var width = $1.forcedWidth || genro.getFromStorage('local','frameindex_left_'+plugin_name+'_width') || $1.defaultWidth;
                                                         if(width){
                                                              SET frameindex.regions.left = width;
                                                         }
                                                         genro.nodeById('standard_index').publish('showLeft');""",
                                overflow='hidden')
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
                                                      connect_onclick="""genro.nodeById('standard_index').publish('toggleLeft');""")

    def btn_refresh(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameRefresh',tip='!!Refresh the current page',
                                                      connect_onclick="PUBLISH reloadFrame=genro.dom.getEventModifiers($1);")               

    def btn_delete(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameDelete',tip='!!Close the current page',
                                                      connect_onclick='PUBLISH closeFrame;')
    
    @struct_method
    def fi_slotbar_newWindow(self,pane,**kwargs):
        pane.div(_class='windowaddIcon iconbox',tip='!!New Window',connect_onclick='genro.openBrowserTab(genro.addParamsToUrl(window.location.href,{new_window:true}));')

    @struct_method
    def fi_pluginButton(self,pane,name,caption=None,iconClass=None,defaultWidth=None,**kwargs):
        pane.div(_class='button_block iframetab').lightButton(_class=iconClass,tip=caption,
                 action="""genro.publish('open_plugin',{plugin:plugin_name,defaultWidth:defaultWidth});""",
                 plugin_name=name,defaultWidth=defaultWidth or '210px',
                 nodeId='plugin_block_%s' %name)


    def windowTitle(self):
        return self.getPreference('instance_data.owner_name',pkg='adm') or self.site.site_name
        
    def windowTitleTemplate(self):
        return "%s $workdate" %self.windowTitle()
                                                   