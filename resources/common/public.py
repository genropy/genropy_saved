#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" public common11 """
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrlang import extract_kwargs

import os

class Public(BaseComponent):
    """docstring for Public for common_d11: a complete restyling of Public of common_d10"""
    css_requires = 'public'
    plugin_list = 'menu_plugin,batch_monitor,chat_plugin'
    js_requires = 'public'
    py_requires = """foundation/menu:Menu,
                     foundation/dialogs,
                     foundation/macrowidgets,
                     gnrcomponents/batch_handler/batch_handler:BatchMonitor,
                     gnrcomponents/chat_component/chat_component:ChatComponent,
                     gnrcomponents/grid_configurator/grid_configurator:GridConfigurator"""


    def userRecord(self, path=None):
        if not hasattr(self, '_userRecord'):
            user = self.pageArgs.get('_user_')
            if not user or not( 'passpartout' in self.userTags):
                user = self.user
            self._userRecord = self.db.table('adm.user').record(username=user).output('bag')
        return self._userRecord[path]

    def onMain_pbl(self):
        pane = self.pageSource()
        userTable = self.pbl_userTable()
        if not self.isGuest and userTable:
            pane.dataRecord('gnr.user_record', userTable, username=self.user, _init=True)
        pane.data('gnr.workdate', self.workdate)
        self._pbl_dialogs(pane)
        #pane.img(_class='buttonIcon %s' %self.pbl_logoclass())
        if self.db.packages['adm']:
            pane.dataController("""var prefCode = preference_open[0];
                                   var frameId = prefCode=='app'?app+'_frame':user+'_frame';
                                   var frameWindow = genro.domById(frameId).contentWindow;
                                   if('genro' in frameWindow){
                                        frameWindow.genro.formById('preference').load();
                                    }
                                    if (prefCode=='app'){
                                        FIRE #mainpreference.open;
                                    }
                                    else if (prefCode=='user'){
                                        FIRE #userpreference.open;
                                    }
                                    """,
                                app='mainpreference',
                                user='userpreference',
                                subscribe_preference_open=True)

            self.iframeDialog(pane, title='!!Application Preference', dlgId='mainpreference', src='/adm/app_preference',
                              cached=False, height='450px', width='800px', centerOn='_pageRoot',
                              datapath='gnr.preference.application')
            self.iframeDialog(pane, title='!!User Preference', dlgId='userpreference', src='/adm/user_preference',
                              cached=False, height='300px', width='400px', centerOn='_pageRoot',
                              datapath='gnr.preference.user')


    def pbl_userTable(self):
        return 'adm.user'

    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='pbl_root', **kwargs)

    def _pbl_dialogs(self, pane):
        self._pbl_dialogs_waiting(pane)

    def _pbl_dialogs_waiting(self, pane):
        def cb_bottom(*args, **kwargs):
            pass

        def cb_center(parentBc, **kwargs):
            parentBc.contentPane(**kwargs).div(_class='waiting')

        self.simpleDialog(pane, title='!!Waiting', dlgId='pbl_waiting', height='200px', width='300px',
                          cb_center=cb_center,
                          datapath='gnr.tools.waitingdialog', cb_bottom=cb_bottom)
        
    @extract_kwargs(top=True,bottom=True)
    def _pbl_frameroot(self, rootbc, title=None, height=None, width=None, flagsLocale=False,
                     top_kwargs=None,bottom_kwargs=None,**kwargs):
        frame = rootbc.framePane(frameCode='public_root',region='center', _class='pbl_root_center',
                                namespace='public',**kwargs)
        self.public_frameTopBar(frame.top,title=title,**top_kwargs)
        self.public_frameBottomBar(frame.bottom,**bottom_kwargs)
        return frame
    
    def public_frameTopBar(self,pane,slots=None,title=None,**kwargs):
        pane.parent.data('_clientCtx.mainBC.left?show', self.pageOptions.get('openMenu', True))            
        slots = slots or 'menuBtn,workdate,*,caption,*,user,logout,5'
        if 'caption' in slots:
            kwargs['caption_title'] = title
        
        return pane.slotBar(slots=slots,
                            _class='pbl_root_top',
                            **kwargs)
    
    def public_frameBottomBar(self,pane,slots=None,**kwargs):
        slots = slots or '5,dock,*,messageBox,*,devBtn,locBtn,5'
        if 'messageBox' in slots:
            pane.parent.dataController("genro.publish('pbl_bottomMsg',{message:msg});",msg="^pbl.bottomMsg") #legacy
            kwargs['messageBox_subscribeTo']=kwargs.get('messageBox_subscribeTo') or 'pbl_bottomMsg'
        return pane.slotBar(slots=slots,
                            _class='pbl_root_bottom',
                            **kwargs)
        
    @struct_method
    def pbl_slotbar_public_menuBtn(self,pane,**kwargs):
        pane.div(_class='pbl_menu_icon buttonIcon', connect_onclick="PUBLISH main_left_set_status= 'toggle';")
        
    @struct_method
    def pbl_slotbar_public_workdate(self,pane,**kwargs):
        connect_onclick = None
        if self.application.checkResourcePermission(self.pbl_canChangeWorkdate(), self.userTags):
            connect_onclick = 'FIRE #changeWorkdate_dlg.open;'
        pane.div('^gnr.workdate', format='short',
                 _class='pbl_slotbar_label buttonIcon',
                 connect_onclick=connect_onclick)
        if connect_onclick:
            self.pbl_workdate_dialog()
        
    
    @struct_method
    def pbl_slotbar_public_caption(self,pane,title='',**kwargs):   
        pane.div(title, _class='pbl_title_caption',subscribe_public_caption='this.domNode.innerHTML=$1;',**kwargs)
        
    @struct_method
    def pbl_slotbar_public_pageback(self,pane,**kwargs): 
        pane.div(connect_onclick="genro.pageBack()", title="!!Back",
                 _class='icnBaseUpYellow buttonIcon', content='&nbsp;',**kwargs)
                 
    @struct_method
    def pbl_slotbar_public_flagsLocale(self,pane,**kwargs): 
            pane.dataRpc('aux.locale_ok', 'changeLocale', locale='^aux.locale')
            pane.dataController('genro.pageReload()', _fired='^aux.locale_ok')
            pane.button(action="SET aux.locale = 'EN'", title="!!English",
                      _class='icnIntlEn buttonIcon')
            pane.button(action="SET aux.locale = 'IT'", title="!!Italian",
                      _class='icnIntlIt buttonIcon')
    
    @struct_method
    def pbl_slotbar_public_user(self,pane,**kwargs): 
        if not self.isGuest:
            pane.div(content=self.user, float='right', _class='pbl_slotbar_label buttonIcon',
                      connect_onclick='PUBLISH preference_open="user";',**kwargs)
    
    @struct_method
    def pbl_slotbar_public_logout(self,pane,**kwargs):
        if not self.isGuest:
            pane.div(connect_onclick="genro.logout()", title="!!Logout",
                      _class='pbl_logout buttonIcon', content='&nbsp;',**kwargs)
        
    @struct_method
    def pbl_slotbar_public_dock(self,pane,**kwargs):
        pane.dock(id='default_dock', background='none', border=0)
        
    @struct_method
    def pbl_slotbar_public_locBtn(self,pane,**kwargs):
        if self.isLocalizer():
            pane.div(connect_onclick='genro.dev.openLocalizer()', _class='^gnr.localizerClass', float='right')
            pane.dataFormula('gnr.localizerClass', """ 'localizer_'+status;""",
                            status='^gnr.localizerStatus', _init=True, 
                            _else="return 'localizer_hidden'")
                   
    @struct_method
    def pbl_slotbar_public_devBtn(self,pane,**kwargs):         
        if self.isDeveloper():
            pane.div(connect_onclick='genro.dev.showDebugger();',
                      _class='icnBaseEye buttonIcon', float='right', margin_right='5px')
        
    
    @struct_method
    def public_rootStackContainer(self, root, title=None, height=None, width=None,**kwargs):
        frame = self._pbl_frameroot(root, title, height=height, width=width,center_widget='StackContainer',**kwargs) 
        return frame
    
    @struct_method
    def public_rootBorderContainer(self, root, title=None, height=None, width=None, **kwargs):
        frame = self._pbl_frameroot(root, title, height=height, width=width,center_widget='BorderContainer',**kwargs) 
        return frame

    @struct_method
    def public_rootTabContainer(self, root, title=None, height=None, width=None, **kwargs):
        frame = self._pbl_frameroot(root, title, height=height, width=width, center_widget='TabContainer',**kwargs) 
        return frame
        
    @struct_method
    def public_rootContentPane(self, root, title=None, height=None, width=None,**kwargs):
        frame = self._pbl_frameroot(root, title, height=height, width=width, **kwargs) 
        return frame
        
    def _pbl_root(self, rootbc, title=None, height=None, width=None, centered=None, flagsLocale=False):
        if centered:
            margin = 'auto'
        else:
            margin = None
        self.pageSource('_pageRoot').setAttr(height=height, width=width, margin=margin)
        top = self.pbl_topBar(rootbc.borderContainer(region='top', _class='pbl_root_top', overflow='hidden'), title,
                              flagsLocale=flagsLocale)
        bottom = self.pbl_bottomBar(rootbc.contentPane(region='bottom', _class='pbl_root_bottom', overflow='hidden'))
        bc = rootbc.borderContainer(region='center', _class='pbl_root_center')
        return bc, top, bottom

    def pbl_rootContentPane(self, root, title=None, height=None, width=None, centered=False, flagsLocale=False,
                            **kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,
                                         flagsLocale=flagsLocale)
        center = bc.contentPane(region='center', **kwargs)
        return center, top, bottom
           
    def pbl_rootStackContainer(self, root, title=None, height=None, width=None, centered=False, flagsLocale=False,
                               **kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,
                                         flagsLocale=flagsLocale)
        center = bc.stackContainer(region='center', **kwargs)
        return center, top, bottom

    def pbl_rootTabContainer(self, root, title=None, height=None, width=None, centered=False, flagsLocale=False,
                             **kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,
                                         flagsLocale=flagsLocale)
        center = bc.tabContainer(region='center', **kwargs)
        return center, top, bottom

    def pbl_rootBorderContainer(self, root, title=None, height=None, width=None, centered=False, flagsLocale=False,
                                **kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,
                                         flagsLocale=flagsLocale)
        center = bc.borderContainer(region='center', **kwargs)
        return center, top, bottom

    def pbl_topBarLeft(self, pane):
        self.pbl_workdateManager(pane)

    def pbl_canChangeWorkdate(self):
        return

    def pbl_workdateManager(self, pane):
        connect_onclick = None
        if self.application.checkResourcePermission(self.pbl_canChangeWorkdate(), self.userTags):
            connect_onclick = 'FIRE #changeWorkdate_dlg.open;'
        pane.div('^gnr.workdate', float='left', format='short',
                 _class='pbl_workdate buttonIcon',
                 connect_onclick=connect_onclick)
        if connect_onclick:
            self.pbl_workdate_dialog()
    
    
    def pbl_workdate_dialog(self):
        def cb_center(parentBC, **kwargs):
            pane = parentBC.contentPane(**kwargs)
            fb = pane.formbuilder(cols=1, border_spacing='5px', margin='25px', margin_top='20px')
            fb.dateTextBox(value='^.current_date', width='8em', lbl='!!Date')
        dlg = self.formDialog(self.pageSource(), title='!!Set workdate', datapath='changeWorkdate',
                              formId='changeWorkdate', height='100px', width='200px',
                              cb_center=cb_center, loadsync=True)
        dlg.dataController("SET .data.current_date=date;", date="=gnr.workdate", nodeId='changeWorkdate_loader')
        dlg.dataRpc('gnr.workdate', 'pbl_changeServerWorkdate', newdate='=.data.current_date',
                    _if='newdate', nodeId='changeWorkdate_saver', _onResult='FIRE .saved;')

    def rpc_pbl_changeServerWorkdate(self, newdate=None):
        if newdate:
            self.workdate = newdate
        return self.workdate

    def mainLeftTop(self, pane):
        if self.application.checkResourcePermission(self.pbl_preferenceAppTags(), self.userTags):
            pane.div(_class='icnBasePref buttonIcon', connect_onclick='PUBLISH preference_open="app";',
                     tip='!!Application Preferences', position='absolute', left='5px', top='5px')
        pane.div('^gnr.app_preference.adm.instance_data.owner_name')

    def pbl_topBar(self, top, title=None, flagsLocale=False):
        """docstring for publicTitleBar"""
        left = top.contentPane(region='left', width='250px')
        top.data('_clientCtx.mainBC.left?show', self.pageOptions.get('openMenu', True))
        menubtn = left.div(_class='pbl_menu_icon buttonIcon', float='left',
                           connect_onclick="PUBLISH main_left_set_status= 'toggle';")
        self.pbl_topBarLeft(left)
        right = top.contentPane(region='right', width='250px', padding_top='5px', padding_right='8px')
        right.div(connect_onclick='genro.pageBack()', _class='goback', tooltip='!!Torna alla pagina precedente')
        center = top.contentPane(region='center', margin_top='3px', overflow='hidden')
        if title:
            center.div(title, _class='pbl_title_caption')
            #right.div(connect_onclick="genro.pageBack()", title="!!Back",
        #          _class='icnBaseUpYellow buttonIcon', content='&nbsp;', float='right',margin_left='10px')
        if flagsLocale:
            right.dataRpc('aux.locale_ok', 'changeLocale', locale='^aux.locale')
            right.dataController('genro.pageReload()', _fired='^aux.locale_ok')
            right.div(connect_onclick="SET aux.locale = 'EN'", title="!!English",
                      _class='icnIntlEn buttonIcon', content='&nbsp;', float='right', margin_left='5px',
                      margin_top='2px')
            right.div(connect_onclick="SET aux.locale = 'IT'", title="!!Italian",
                      _class='icnIntlIt buttonIcon', content='&nbsp;', float='right', margin_left='5px',
                      margin_top='2px')
        if not self.isGuest:
            right.div(connect_onclick="genro.logout()", title="!!Logout",
                      _class='pbl_logout buttonIcon', content='&nbsp;', float='right')
            right.div(content=self.user, float='right', _class='pbl_username buttonIcon',
                      connect_onclick='PUBLISH preference_open="user";')

        return center

    def pbl_bottomBar(self, pane):
        """docstring for publicTitleBar"""
        sc = pane.stackContainer(selectedPage='^pbl.bottom_stack')
        sc.data('pbl.bottom_stack', 'default')

        default_bottom = self.pbl_bottom_default(sc.borderContainer(pageName='default'))
        self.pbl_bottom_message(sc.contentPane(pageName='message'))
        return default_bottom

    def pbl_bottom_message(self, pane):
        pane.div('^pbl.bottomMsg', _class='pbl_messageBottom', nodeId='bottomMsg')
        pane.dataController("""
                                SET pbl.bottom_stack='message';
                                var _this = this;
                                var cb = function(){
                                    _this.setRelativeData('pbl.bottom_stack','default');
                                }
                                genro.dom.effect('bottomMsg','fadeout',{duration:1000,delay:2000,onEnd:cb});
                                
                                """,
                            msg='^pbl.bottomMsg', _if='msg')

    def pbl_preferenceAppTags(self):
        return 'admin'

    def pbl_bottom_default(self, bc):
        left = bc.contentPane(region='left', overflow='hidden', nodeId='pbl_bottomBarLeft')
        right = bc.contentPane(region='right', overflow='hidden', nodeId='pbl_bottomBarRight')

        right.dataScript('gnr.localizerClass', """return 'localizer_'+status""",
                         status='^gnr.localizerStatus', _init=True, _else="return 'localizer_hidden'")
        if self.isDeveloper():
            right.div(connect_onclick='genro.dev.showDebugger();',
                      _class='icnBaseEye buttonIcon', float='right', margin_right='5px')
        if self.isLocalizer():
            right.div(connect_onclick='genro.dev.openLocalizer()', _class='^gnr.localizerClass', float='right')

        center = bc.contentPane(region='center', nodeId='pbl_bottomBarCenter')
        center.dock(id='default_dock', background='none', border=0, float='left', margin_left='4px')
        return dict(left=left, right=right, center=center)

    def pbl_batch_floating(self, pane):
        pane.floatingPane(title='public floating', _class='shadow_4',
                          top='80px', left='20px', width='200px', height='470px',
                          visible=False,
                          closable=True, resizable=True, resizeAxis='xy', maxable=True,
                          dockable=True, dockTo='pbl_floating_dock', duration=400)

    def app_logo_url(self):
        logo_url = self.custom_logo_url()
        if not logo_url:
            logo_url = self.getResourceUri('images/logo/application_logo.png')
        if not logo_url:
            logo_url = self.getResourceUri('images/logo/base_logo.png')
        return logo_url

    def custom_logo_url(self):
        logo_image = self.custom_logo_filename()
        if logo_image:
            return self.site.site_static_url('_resources', 'images', 'logo', logo_image)

    def custom_logo_path(self):
        logo_image = self.custom_logo_filename()
        if logo_image:
            return self.site.site_static_path('_resources', 'images', 'logo', logo_image)

    def custom_logo_filename(self):
        logo_folder = self.site.site_static_path('_resources', 'images', 'logo')
        logo_url = None
        if os.path.isdir(logo_folder):
            files = os.listdir(logo_folder)
            images = [f for f in files if f.startswith('%s' % 'custom_logo')]
            if images:
                return images[0]

class ThermoDialog(BaseComponent):
    py_requires = 'foundation/thermo'

class UserObject(BaseComponent):
    py_requires = 'foundation/userobject'

class IncludedView(BaseComponent):
    py_requires = 'foundation/includedview'

class RecordHandler(BaseComponent):
    py_requires = 'foundation/recorddialog'

class Tools(BaseComponent):
    py_requires = 'foundation/tools'

class SelectionHandler(BaseComponent):
    py_requires = 'gnrcomponents/selectionhandler'

class RecordLinker(BaseComponent):
    py_requires = 'gnrcomponents/recordlinker'

class MultiSelect(BaseComponent):
    py_requires = 'gnrcomponents/multiselect'

class DynamicEditor(BaseComponent):
    py_requires = 'foundation/macrowidgets:DynamicEditor'

class RecordToHtmlFrame(BaseComponent):
    py_requires = 'foundation/htmltoframe'
    
