# -*- coding: utf-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class FrameIndex(BaseComponent):
    py_requires="""frameindex"""
    css_requires = 'mobileindex'

   #def prepareCenter(self,bc):
   #    pass

    def prepareBottom(self,bc,onCreatingTablist=None):
        pass
        #pane = bc.contentPane(region='bottom',height='20px',overflow='hidden',
        #                    _class='framedindex_tablist',style="""display:flex;flex-direction: row;justify-content:center;""")
    #
        #for btn in ['menuToggle']+self.plugin_list.split(','):
        #    getattr(self,'btn_%s' %btn)(pane)


    def mainLeft_iframemenu_plugin(self, tc):
        frame = tc.framePane(title="Menu", pageName='menu_plugin')
        bc = frame.center.borderContainer()
        #tbl = bc.contentPane(region='bottom').div(height='40px',margin='5px',_class='clientlogo')
        self.menu_iframemenuPane(bc.contentPane(region='center').div(position='absolute', top='2px', left='0', right='2px', bottom='2px', overflow='auto'))

        
        
        
        
    def prepareLeft(self,bc):
        bc = bc.borderContainer(region='left',width='100%',datapath='left',background='white')
        bottom = bc.contentPane(region='bottom',height='30px',_class='mobilebar')
        bar = bottom.slotBar('3,tools,*,logout,3')
        tools = bar.tools.div(style='display:flex;flex-direction: row;justify-content:center;')
        for btn in self.plugin_list.split(','):
            getattr(self,'btn_%s' %btn)(tools.div())
        bar.logout.div(connect_onclick="genro.logout()",_class='button_block iframetab icnBaseUserLogout switch_off',tip='!!Logout')
        sc = bc.stackContainer(selectedPage='^.selected',nodeId='gnr_main_left_center',region='center',
                                subscribe_open_plugin="""var plugin_name = $1.plugin;
                                                         SET left.selected = plugin_name;                                                        
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

    def prepareTop(self,bc,onCreatingTablist=None):
        pane = bc.contentPane(region='top',overflow='hidden')
        sb = pane.slotBar('3,menuToggle,*,debugping,3',
                        _class='mobilebar',height='30px')
        self.btn_menuToggle(sb.menuToggle.div())
        sb.debugping.div(_class='ping_semaphore')
    
    def btn_menuToggle(self,pane,**kwargs):
        pane.div(_class='menu_toggle',tip='!!Show/Hide the left pane',
                                                      connect_onclick="""genro.nodeById('standard_index').publish('toggleLeft');""")
