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
        titlebar = bc.contentPane(region='top').slotBar('*,owner,*',height='20px')
        titlebar.owner.div('^gnr.app_preference.adm.instance_data.owner_name',font_size='13px',
                            connect_onclick='PUBLISH preference_open="app";')
        center = bc.borderContainer(region='center',margin_top='1px')
        leftbar = center.contentPane(region='left',overflow='hidden')        
        leftbar.slotBar(slots='menuToggle,%s' %self.plugin_list,_class='pluginSlotbar',orientation='horizontal',margin_left='10px')
                        
        rightbar = center.contentPane(region='right')        
        #rightbar.slotBar('user,logout',border='1px solid #666',
        #                              rounded=6,_class='pluginSlotbar',
        #                              orientation='horizontal',margin_left='10px')
        buttons = center.contentPane(region='center')
        tabroot = buttons.div(connect_onclick="""
                                            var targetSource = $1.target.sourceNode;
                                            var pageName = targetSource.inheritedAttribute("pageName");
                                            this.setRelativeData("selectedFrame",pageName);
                                            """,margin_left='20px',display='inline-block')
        tabroot.div()
        buttons.dataController("frameIndex.createTablist(tabroot,data);",data="^iframes",tabroot=tabroot)
        buttons.dataController("""  var iframetab = tabroot.getValue().getNode(page);
                                    if(iframetab){
                                        console.log(iframetab);
                                        genro.dom.setClass(iframetab,'iframetab_selected',selected);
                                    }
                                    """,subscribe_iframe_stack_selected=True,tabroot=tabroot,_if='page')


    def prepareBottom(self,pane):
        pane.attributes.update(dict(height='20px'))
        bc = pane.borderContainer(gradient_from='gray',gradient_to='silver',gradient_deg=-90)
        left = bc.contentPane(region='left')
        right = bc.contentPane(region='right')
        center= bc.contentPane(region='center')

    def prepareCenter(self,pane):
        sc = pane.stackContainer(selectedPage='^selectedFrame',nodeId='iframe_stack')
        page = self.pageSource()
        if self.index_url:
            sc.contentPane(pageName='index',title='Index',overflow='hidden').iframe(height='100%', width='100%', src=self.index_url, border='0px')
        page.dataController("""
            frameIndex.selectIframePage(sc,name,label,file,table,formResource,viewResource)
        """,subscribe__menutree__selected=True,sc=sc)
        


        
    def prepareLeft(self,pane):
        pane.attributes.update(dict(splitter=True,width='200px',datapath='left',margin_right='-1px'))
        sc = pane.stackContainer(selectedPage='^.selected',nodeId='gnr_main_left_center')
        sc.dataController("""
                            if(!page){return;}
                             genro.publish(page+'_'+(selected?'on':'off'));
                             genro.dom.setClass(genro.nodeById('plugin_block_'+page).getParentNode(),'selected_plugin',selected);
                            """,
                          subscribe_gnr_main_left_center_selected=True)
        sc.dataController(""" 
                              var command= main_left_status[0]?'open':'close';
                              genro.publish(page+'_'+(command=='open'?'on':'off'));
                            """,subscribe_main_left_status=True,page='=.selected') 
        for plugin in self.plugin_list.split(','):
            cb = getattr(self, 'mainLeft_%s' % plugin)
            assert cb, 'Plugin %s not found' % plugin
            cb(sc.contentPane(pageName=plugin))
            sc.dataController("""
                            PUBLISH main_left_set_status = true;
                            SET .selected=plugin;
                          """, **{'subscribe_%s_open' % plugin: True, 'plugin': plugin})
    
    @struct_method
    def plugin_slotbar_iframemenu_plugin(self,pane,**kwargs):
        pane.div(_class='newplugin_block iframemenu_plugin_icon',
                 connect_onclick="""SET left.selected='iframemenu_plugin';genro.getFrameNode('standard_index').publish('showLeft');""",
                  nodeId='plugin_block_iframemenu_plugin')
                                            
    @struct_method
    def plugin_slotbar_batch_monitor(self,pane,**kwargs):
        pane.div(_class='newplugin_block batch_monitor_icon',
                 connect_onclick="""SET left.selected='batch_monitor';genro.getFrameNode('standard_index').publish('showLeft');""",
                  nodeId='plugin_block_batch_monitor')
                  
    @struct_method
    def plugin_slotbar_chat_plugin(self,pane,**kwargs):
        pane.div(_class='newplugin_block chat_plugin_icon',
                 connect_onclick="""SET left.selected='chat_plugin';genro.getFrameNode('standard_index').publish('showLeft');""",
                  nodeId='plugin_block_chat_plugin')
                  

    @struct_method
    def plugin_slotbar_menuToggle(self,pane,**kwargs):
        pane.div(_class='newplugin_block application_menu',
                    connect_onclick="""genro.getFrameNode('standard_index').publish('toggleLeft');""")
                  

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
                      _class='newplugin_block application_logout',**kwargs)
        else:
            pane.div()
            
