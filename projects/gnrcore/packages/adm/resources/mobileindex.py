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

    def prepareTop(self,bc,onCreatingTablist=None):
        pass
        #pane = bc.contentPane(region='bottom',height='20px',overflow='hidden',
        #                    _class='framedindex_tablist',style="""display:flex;flex-direction: row;justify-content:center;""")
    #
        #for btn in ['menuToggle']+self.plugin_list.split(','):
        #    getattr(self,'btn_%s' %btn)(pane)


    def mainLeft_iframemenu_plugin(self, tc):
        frame = tc.framePane(title="Menu", pageName='menu_plugin')
        frame.bottom.slotToolbar('2,searchOn,*',searchOn=True,_class='mobilebar')
        if not self.isMobile:
            frame.bottom.slotToolbar('5,newWindow,*')
        bc = frame.center.borderContainer()
        #tbl = bc.contentPane(region='bottom').div(height='40px',margin='5px',_class='clientlogo')
        self.menu_iframemenuPane(bc.contentPane(region='center').div(position='absolute', top='2px', left='0', right='2px', bottom='2px', overflow='auto'))

        
        
        
        
    def prepareLeft(self,bc):
        bc = bc.borderContainer(region='left',width='100%',datapath='left')
        top = bc.contentPane(region='top',height='35px',_class='mobilebar',
                                style='display:flex;flex-direction: row;justify-content:center;')
        for btn in self.plugin_list.split(','):
            getattr(self,'btn_%s' %btn)(top.div())
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

    def prepareBottom(self,bc):
        pane = bc.contentPane(region='bottom',overflow='hidden')
        sb = pane.slotToolbar('3,menuToggle,5,devlink,3,applogo,*,genrologo,3,logout,3,debugping,3',
                        _class='slotbar_toolbar framefooter',height='22px',
                        background='#EEEEEE',border_top='1px solid silver')
        self.btn_menuToggle(sb.menuToggle.div())
        applogo = sb.applogo.div()
        if hasattr(self,'application_logo'):
            applogo.div(_class='application_logo_container').img(src=self.application_logo,height='100%')
        sb.genrologo.div(_class='application_logo_container').img(src='/_rsrc/common/images/made_with_genropy_small.png',height='100%')
        sb.logout.div(connect_onclick="genro.logout()",_class='iconbox icnBaseUserLogout switch_off',tip='!!Logout')
        formula = '==(_iframes && _iframes.len()>0)?_iframes.getAttr(_selectedFrame,"url"):"";'
        
        
        sb.devlink.a(href=formula,_iframes='=iframes',_selectedFrame='^selectedFrame').div(_class="iconbox flash",tip='!!Open the page outside frame',_tags='_DEV_')

        sb.debugping.div(_class='ping_semaphore')
    