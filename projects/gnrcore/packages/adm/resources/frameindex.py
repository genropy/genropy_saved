# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.web.gnrwebstruct import struct_method

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
    
    def pageAuthTags(self, method=None, **kwargs):
        print method,kwargs
    
    def mainLeftContent(self,*args,**kwargs):
        pass
        
    def main(self,root,**kwargs):
        root.dataController("""if(!curravatar){genro.loginDialog(loginUrl)}""",_onStart=True,curravatar='=gnr.avatar',loginUrl= self.application.loginUrl())
        if self.root_page_id:
            self.index_dashboard(root)
        else:
            root.frameIndexRoot(**kwargs)
    
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
        for btn in ['refresh','delete']:
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
        pane.attributes.update(dict(overflow='hidden',background='silver',height='18px'))
        sb = pane.slotBar('5,appName,*,messageBox,*,devlink,user,logout,5',_class='framefooter',margin_top='1px',messageBox_subscribeTo='rootmessage')
        appPref = sb.appName.div(innerHTML='==_owner_name || "Preferences";',_owner_name='^gnr.app_preference.adm.instance_data.owner_name',_class='footer_block',
                                connect_onclick='PUBLISH app_preference',zoomUrl='adm/app_preference',pkey='Application preference')
        userPref = sb.user.div(self.user if not self.isGuest else 'guest', _class='footer_block',tip='!!%s preference' % (self.user if not self.isGuest else 'guest'),
                               connect_onclick='PUBLISH user_preference',zoomUrl='adm/user_preference',pkey='User preference')
        sb.logout.div(connect_onclick="genro.logout()",_class='application_logout',height='16px',width='20px',tip='!!Logout')
        formula = '==(_iframes && _iframes.len()>0)?_iframes.getNode(_selectedFrame).attr.url:"";'
        sb.devlink.a(href=formula,_iframes='=iframes',_selectedFrame='^selectedFrame').div(_class="iconbox flash",tip='!!Open the page outside frame',_tags='_DEV_')
        appPref.dataController("""genro.dlg.zoomPalette(pane,null,{top:'10px',left:'10px',
                                                        title:preftitle,height:'450px', width:'800px',
                                                        palette_transition:null,palette_nodeId:'mainpreference'});""",
                            subscribe_app_preference=True,
                            _tags=self.preferenceTags,pane=appPref,preftitle='!!Application preference')
        userPref.dataController("""genro.dlg.zoomPalette(pane,null,{top:'10px',right:'10px',title:preftitle,
                                                        height:'300px', width:'400px',palette_transition:null,
                                                        palette_nodeId:'userpreference'});""",
                            subscribe_user_preference=True,pane=userPref,preftitle='!!User preference')
                            
    def prepareCenter(self,pane):
        sc = pane.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack',
                                border_left='1px solid silver',margin_left='-4px',
                                onCreated='genro.framedIndexManager = new gnr.FramedIndexManager(this);')
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
        scattr['subscribe_closeFrame'] = "genro.framedIndexManager.deleteFramePage($1);"        
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
        sc = pane.stackContainer(selectedPage='^.selected',nodeId='gnr_main_left_center',overflow='hidden')
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
                                                      connect_onclick='PUBLISH closeFrame= GET selectedFrame;')
                                                      