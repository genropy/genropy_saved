# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
class Mixin(BaseComponent):
    py_requires="""foundation/menu:MenuIframes,gnrcomponents/batch_handler/batch_handler,
                   gnrcomponents/chat_component/chat_component"""
    js_requires='frameindex'
    css_requires='frameindex,public'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
    index_url = None
    showTabs = True
    
    def rootWidget(self,root,**kwargs):
        return root.framePane('standard_index',_class='hideSplitter',
                                border='1px solid gray',rounded_top=8,
                                margin='2px',
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
        pane.attributes.update(dict(height='50px',overflow='hidden'))
        bc = pane.borderContainer(rounded_top=10,gradient_from='gray',gradient_to='silver',gradient_deg=90) 
        top = bc.contentPane(region='top').slotBar('*,owner,*',height='20px')
        top.owner.div('^gnr.app_preference.adm.instance_data.owner_name',font_size='13px',
                            connect_onclick='PUBLISH preference_open="app";')
        
        center = bc.borderContainer(region='center',margin_top='1px')
        
        leftbar = center.contentPane(region='left',overflow='hidden').div(display='inline-block', margin_left='10px')  
        for btn in ['menuToggle']+self.plugin_list.split(','):
            getattr(self,'btn_%s' %btn)(leftbar)
                
        rightbar = center.contentPane(region='right',overflow='hidden').div(display='inline-block', margin_right='10px')
        for btn in ['refresh','delete']:
            getattr(self,'btn_%s' %btn)(rightbar)
        
        self.prepareTablist(center.contentPane(region='center'))
        
    def prepareTablist(self,pane):     
        tabroot = pane.div(connect_onclick="""
                                            var targetSource = $1.target.sourceNode;
                                            var pageName = targetSource.inheritedAttribute("pageName");
                                            this.setRelativeData("selectedFrame",pageName);
                                            """,margin_left='20px',display='inline-block')
        tabroot.div()
        pane.dataController("frameIndex.createTablist(tabroot,data);",data="^iframes",tabroot=tabroot)
        pane.dataController("""  var iframetab = tabroot.getValue().getNode(page);
                                    if(iframetab){
                                        genro.dom.setClass(iframetab,'iframetab_selected',selected);                                        
                                        var node = genro._data.getNode('iframes.'+page);
                                        var treeItem = genro.getDataNode(node.attr.fullpath);
                                        var labelClass = treeItem.attr.labelClass;
                                        labelClass = selected? labelClass+ ' menu_current_page': labelClass.replace('menu_current_page','')
                                        treeItem.setAttribute('labelClass',labelClass);
                                    }
                                    """,subscribe_iframe_stack_selected=True,tabroot=tabroot,_if='page')


    def prepareBottom(self,pane):
        pane.attributes.update(dict(height='20px',overflow='hidden'))
        bc = pane.borderContainer(gradient_from='gray',gradient_to='silver',gradient_deg=-90)
        left = bc.contentPane(region='left')
        right = bc.contentPane(region='right')
        center= bc.contentPane(region='center')

    def prepareCenter(self,pane):
        sc = pane.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack')
        scattr = sc.attributes
        scattr['subscribe_reloadFrame'] = """var frame = dojo.byId("iframe_"+$1);
                                                    var src = frame.src;
                                                    frame.src = '';
                                                    setTimeout(function(){
                                                        frame.src = src;
                                                    },1)"""
        scattr['subscribe_closeFrame'] = """
                                            var sc = this.widget;
                                            var selected = sc.getSelectedIndex();
                                            var node = genro._data.popNode('iframes.'+$1);
                                            var treeItem = genro.getDataNode(node.attr.fullpath);
                                            treeItem.setAttribute('labelClass',treeItem.attr.labelClass.replace('menu_existing_page',''));
                                            this.getValue().popNode($1);
                                            selected = selected>=sc.getChildren().length? selected-1:selected;
                                            PUT selectedFrame = null;
                                            sc.setSelected(selected);
                                        """        
        page = self.pageSource()
        if self.index_url:
            sc.contentPane(pageName='index',title='Index',overflow='hidden').iframe(height='100%', width='100%', src=self.index_url, border='0px')
        page.dataController("""
            setTimeout(function(){frameIndex.selectIframePage(sc,name,label,file,table,formResource,viewResource,fullpath)},1);
        """,subscribe__menutree__selected=True,sc=sc)
        
    def prepareLeft(self,pane):
        pane.attributes.update(dict(splitter=True,width='200px',datapath='left',margin_right='-1px',overflow='hidden'))
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
                 connect_onclick="""SET left.selected='batch_monitor';genro.getFrameNode('standard_index').publish('showLeft');""",
                  nodeId='plugin_block_batch_monitor')
                  
    def btn_chat_plugin(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='chat_plugin_icon',
                 connect_onclick="""SET left.selected='chat_plugin';genro.getFrameNode('standard_index').publish('showLeft');""",
                  nodeId='plugin_block_chat_plugin')
                  

    def btn_menuToggle(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='application_menu',
                    connect_onclick="""genro.getFrameNode('standard_index').publish('toggleLeft');""")

    def btn_refresh(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameRefresh',
                                                      connect_onclick="PUBLISH reloadFrame=this.inheritedAttribute('selectedFrame');",
                                                      selectedFrame='=selectedFrame')               

    def btn_delete(self,pane,**kwargs):
        pane.div(_class='button_block iframetab').div(_class='icnFrameDelete',
                                                        connect_onclick='PUBLISH closeFrame=this.inheritedAttribute("selectedFrame");',
                                                        selectedFrame='=selectedFrame')
        
                    
    @struct_method
    def login_slotbar_user(self,pane,**kwargs): 
        if not self.isGuest:
            pane.div(self.user,connect_onclick='PUBLISH preference_open="user";')
        else:
            pane.div('guest')
            
    @struct_method
    def login_slotbar_logout(self,pane,**kwargs):
        if not self.isGuest:
            pane.div(connect_onclick="genro.logout()",
                      _class='iframetab button_block application_logout',**kwargs)
        else:
            pane.div()
            
