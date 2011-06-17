# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
class Mixin(BaseComponent):
    py_requires="""foundation/menu:MenuIframes,gnrcomponents/batch_handler/batch_handler,
                   gnrcomponents/chat_component/chat_component"""
    js_requires='frameindex'
    css_requires='frameindex,public'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
    index_url = None
    showTabs = True
    indexTab = False
    hideLeftPlugins = False
    preferenceTags = 'admin'
    
    def rootWidget(self,root,**kwargs):
        return root.framePane('standard_index',_class='hideSplitter',
                                #border='1px solid gray',#rounded_top=8,
                                margin='0px',
                                gradient_from='#d0d0d0',gradient_to='#ffffff',gradient_deg=-90,
                                selfsubscribe_toggleLeft=""" 
                                                            var bc = this.getWidget();
                                                             genro.dom.toggleClass(bc._left,"hiddenBcPane"); 
                                                             bc._layoutChildren("left");""",
                                selfsubscribe_showLeft=""" 
                                                            var bc = this.getWidget();
                                                             genro.dom.removeClass(bc._left,"hiddenBcPane"); 
                                                             bc._layoutChildren("left");""",
                                **kwargs)

    def mainLeftContent(self,*args,**kwargs):
        pass
    
    
    def main(self,frame,**kwargs):
        self.prepareLeft(frame.left)
        self.prepareTop(frame.top)
        self.prepareBottom(frame.bottom)
        self.prepareCenter(frame.center)

    def prepareTop(self,pane):
        pane.attributes.update(dict(height='30px',overflow='hidden',gradient_from='gray',gradient_to='silver',gradient_deg=90))
        bc = pane.borderContainer(margin_top='4px') 
        leftbar = bc.contentPane(region='left',overflow='hidden').div(display='inline-block', margin_left='10px')  
        for btn in ['menuToggle']+self.plugin_list.split(','):
            getattr(self,'btn_%s' %btn)(leftbar)
                
        rightbar = bc.contentPane(region='right',overflow='hidden').div(display='inline-block', margin_right='10px')
        for btn in ['refresh','delete']:
            getattr(self,'btn_%s' %btn)(rightbar)
        
        self.prepareTablist(bc.contentPane(region='center'))
        
    def prepareTablist(self,pane):     
        tabroot = pane.div(connect_onclick="""
                                            var targetSource = $1.target.sourceNode;
                                            var pageName = targetSource.inheritedAttribute("pageName");
                                            this.setRelativeData("selectedFrame",pageName);
                                            """,margin_left='20px',display='inline-block')
        tabroot.div()
        pane.dataController("""
                                if(!data){
                                    if(indexTab){
                                        data = new gnr.GnrBag();
                                        data.setItem('indexpage',null,{'fullname':indexTab,pageName:'indexpage',fullpath:'indexpage'});
                                        SET iframes = data;
                                    }
                                }else{
                                    genro.framedIndexManager.createTablist(tabroot,data);
                                }
                                """,
                            data="^iframes",tabroot=tabroot,indexTab=self.indexTab,_onStart=True)
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
        sb = pane.slotBar('5,appName,*,frameurl,*,user,logout,5',_class='framefooter',margin_top='1px')
        appPref = sb.appName.div('^gnr.app_preference.adm.instance_data.owner_name',_class='footer_block',
                                connect_onclick='PUBLISH app_preference',zoomUrl='adm/app_preference',pkey='Application preference')
        userPref = sb.user.div(self.user if not self.isGuest else 'guest', _class='footer_block',
                            connect_onclick='PUBLISH user_preference',zoomUrl='adm/user_preference',pkey='User preference')
        sb.logout.div(connect_onclick="genro.logout()",_class='application_logout',height='16px',width='20px')
        formula = '==(_iframes && _iframes.len()>0)?_iframes.getNode(_selectedFrame).attr.url:"";'
        sb.frameurl.div().a(innerHTML=formula,_tags='_DEV_',href=formula,_iframes='=iframes',_selectedFrame='^selectedFrame')
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
        sc = pane.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack',margin_left='-5px',
                                onCreated='genro.framedIndexManager = new gnr.FramedIndexManager(this);')
        sc.dataController("setTimeout(function(){genro.framedIndexManager.selectIframePage(selectIframePage[0])},1);",subscribe_selectIframePage=True)

        scattr = sc.attributes
        scattr['subscribe_reloadFrame'] = """var frame = dojo.byId("iframe_"+$1);
                                                    var src = frame.src;
                                                    frame.src = '';
                                                    setTimeout(function(){
                                                        frame.src = src;
                                                    },1);"""
        scattr['subscribe_closeFrame'] = """
                                            var sc = this.widget;
                                            var selected = sc.getSelectedIndex();
                                            var node = genro._data.popNode('iframes.'+$1);
                                            var treeItem = genro.getDataNode(node.attr.fullpath);
                                            if(treeItem){
                                                var itemclass = treeItem.attr.labelClass.replace('menu_existing_page','');
                                                itemclass = itemclass.replace('menu_current_page','');
                                                treeItem.setAttribute('labelClass',itemclass);
                                            }
                                            this.getValue().popNode($1);
                                            selected = selected>=sc.getChildren().length? selected-1:selected;
                                            PUT selectedFrame = null;
                                            sc.setSelected(selected);
                                        """        
        scattr['subscribe_destroyFrames'] = """
                        var sc = this.widget;
                        for (var k in $1){
                            var node = genro._data.popNode('iframes.'+k);
                            this.getValue().popNode(k);
                        }
                        """
        scattr['subscribe_changeFrameLabel']='genro.framedIndexManager.changeFrameLabel($1);'
        page = self.pageSource()
        if self.index_url:
            sc.contentPane(pageName='indexpage',title='Index',overflow='hidden').iframe(height='100%', width='100%', src=self.getResourceUri(self.index_url), border='0px')            
        elif getattr(self,'index_dashboard'):
            self.index_dashboard(sc.contentPane(pageName='indexpage'))
        page.dataController("""
                            genro.publish('selectIframePage',_menutree__selected[0]);""",
                            subscribe__menutree__selected=True)
                        

    def prepareLeft(self,pane):
        pane.attributes.update(dict(splitter=True,width='200px',datapath='left',
                                    margin_right='-1px',overflow='hidden',_class='hiddenBcPane' if self.hideLeftPlugins else None))
        sc = pane.stackContainer(selectedPage='^.selected',nodeId='gnr_main_left_center',overflow='hidden')
        sc.dataController("""
                            if(!page){return;}
                             genro.publish(page+'_'+(selected?'on':'off'));
                             genro.dom.setClass(genro.nodeById('plugin_block_'+page).getParentNode(),'iframetab_selected',selected);
                            """,
                          subscribe_gnr_main_left_center_selected=True)
        sc.dataController(""" 
                              var command= main_left_status[0]?'open':'close';
                              genro.publish(page+'_'+(command=='open'?'on':'off'));
                            """,subscribe_main_left_status=True,page='=.selected') 
        for plugin in self.plugin_list.split(','):
            cb = getattr(self, 'mainLeft_%s' % plugin)
            assert cb, 'Plugin %s not found' % plugin
            cb(sc.contentPane(pageName=plugin,overflow='hidden'))
            sc.dataController("""
                            PUBLISH main_left_set_status = true;
                            SET .selected=plugin;
                          """, **{'subscribe_%s_open' % plugin: True, 'plugin': plugin})
    
    def btn_iframemenu_plugin(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='iframemenu_plugin_icon',
                 connect_onclick="""SET left.selected='iframemenu_plugin';genro.getFrameNode('standard_index').publish('showLeft');""",
                  nodeId='plugin_block_iframemenu_plugin')
                                            
    def btn_batch_monitor(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='batch_monitor_icon',
                 connect_onclick="""genro.publish('open_batch');""",
                  nodeId='plugin_block_batch_monitor')
        pane.dataController("SET left.selected='batch_monitor';genro.getFrameNode('standard_index').publish('showLeft')",subscribe_open_batch=True)
                  
    def btn_chat_plugin(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='chat_plugin_icon',
                 connect_onclick="""SET left.selected='chat_plugin';genro.getFrameNode('standard_index').publish('showLeft');""",
                  nodeId='plugin_block_chat_plugin')
                  

    def btn_menuToggle(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='application_menu',
                    connect_onclick="""genro.getFrameNode('standard_index').publish('toggleLeft');""")

    def btn_refresh(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameRefresh',
                                                      connect_onclick="PUBLISH reloadFrame=GET selectedFrame;")               

    def btn_delete(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameDelete',
                                                        connect_onclick='PUBLISH closeFrame= GET selectedFrame;')
        

  
            
