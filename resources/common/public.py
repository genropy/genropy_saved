#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" public common11 """
from gnr.web.gnrbaseclasses import BaseComponent
import os

class Public(BaseComponent):
    """docstring for Public for common_d11: a complete restyling of Public of common_d10"""
    css_requires = 'public'
    js_requires = 'public'
    py_requires = """foundation/menu:Menu,
                     foundation/dialogs,
                     foundation/macrowidgets,
                     gnrcomponents/chat_component:ChatComponent"""
                     #,
                     #gnrcomponents/batch_monitor/batch_monitor:BatchMonitor"""
    
        
    def userRecord(self,path=None):
        if not hasattr(self,'_userRecord' ):
            user = self.pageArgs.get('_user_')
            if not user or not( 'passpartout' in self.userTags):
                user =  self.user
            self._userRecord=self.db.table('adm.user').record(username=user).output('bag')
        return self._userRecord[path]

    def onMain_pbl(self):
        pass
        
    def mainLeftContent(self,parentBC,**kwargs):
        sc = parentBC.stackContainer(width='20%',selectedPage='^pbl.left_stack',
                                    _class='menupane',overflow='hidden',**kwargs)
        sc.data('pbl.left_stack','menu')
        bc_main = sc.borderContainer(pageName='menu')
        bottom = bc_main.contentPane(region='bottom').toolbar(overflow='hidden',padding=0,padding_left='3px',padding_right='3px',font_size='.9em')
        self.pbl_preference_main(bottom)
        bottom.button('!!Preferences',
                     action='FIRE gnr.openPreference="app";',
                     float='left') #'pbl_brandLogo' should be the client logo
        self.menu_menuPane(bc_main.contentPane(region='center',_class='menutree_container',overflow='auto'))
        
        for pageName, cb in [(c.split('_')[2],getattr(self,c)) for c in dir(self) if c.startswith('pbl_left_')]:
            bc = sc.borderContainer(pageName=pageName)
            top = bc.contentPane(region='top').toolbar(overflow='hidden',padding=0,padding_left='3px',padding_right='3px',min_height='22px',font_size='.9em')
            top.div(float='right',margin='3px',_class='buttonIcon icnTabClose',
                    connect_onclick='SET pbl.left_stack="menu";')            
            cb(bc.contentPane(region='center',overflow='hidden'),footer=bottom,toolbar=top)

    def pbl_preference_main(self,pane):
        #pane.img(_class='buttonIcon %s' %self.pbl_logoclass())
        if self.db.packages['adm']:
            pane.dataController("""var frameId = prefCode=='app'?app+'_frame':user+'_frame';
                                   console.log(frameId);
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
                                    """,prefCode="^gnr.openPreference",app='mainpreference',
                                    user='userpreference')
                                    
            self.iframeDialog(pane,title='!!Application Preference',dlgId='mainpreference',src='/adm/app_preference',
                             cached=False,height='450px',width='800px',centerOn='_pageRoot',datapath='gnr.preference.application')
            self.iframeDialog(pane,title='!!User Preference',dlgId='userpreference',src='/adm/user_preference',
                             cached=False,height='300px',width='400px',centerOn='_pageRoot',datapath='gnr.preference.user')
        
    def pbl_userTable(self):
        return 'adm.user'
        
    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='pbl_root',**kwargs)
        
    def _pbl_dialogs(self,pane):
        self._pbl_dialogs_waiting(pane)
        self._pbl_dialogs_pendingChanges(pane)

    def _pbl_dialogs_waiting(self,pane):
        def cb_bottom(*args,**kwargs):
            pass
            
        def cb_center(parentBc,**kwargs):
            parentBc.contentPane(**kwargs).div(_class='waiting')
            
        self.simpleDialog(pane,title='!!Waiting',dlgId='pbl_waiting',height='200px',width='300px',cb_center=cb_center,
                        datapath='gnr.tools.waitingdialog',cb_bottom=cb_bottom)
        
    def _pbl_dialogs_pendingChanges(self,pane):

        def cb_bottom(bc,confirm_btn=None,**kwargs):
            bottom = bc.contentPane(**kwargs)
            bottom.button('!!Save',float='right',margin='1px',
                        action="FIRE .close; (GET .opener.saveCb)();",
                        disabled='^.opener.invalidData')
            bottom.button('!!Cancel',baseClass='bottom_btn',float='right',margin='1px',
                            action='FIRE .close; (GET .opener.cancelCb)();')
            bottom.button('!!Discard',float='left',margin='1px',
                        action="FIRE .close; (GET .opener.continueCb)();")
            
        def cb_center(parentBc,**kwargs):
            parentBc.contentPane(**kwargs).div("!!Current record has been modified.",text_align='center',margin_top='20px')
            
        self.simpleDialog(pane,title='!!Warning',dlgId='pbl_formPendingChangesAsk',
                         height='80px',width='300px',cb_center=cb_center,
                        datapath='gnr.tools.formPendingChanges',cb_bottom=cb_bottom)
        
            
    def _pbl_root(self, rootbc, title=None, height=None, width=None, centered=None,flagsLocale=False):
        userTable=self.pbl_userTable()
        self._pbl_dialogs(rootbc)
        if self.user and userTable:
            rootbc.dataRecord('gnr.user_record',userTable, username=self.user, _init=True)
            rootbc.data('gnr.user_preference',self.getUserPreference('*'))
        rootbc.data('gnr.workdate', self.workdate)
        if centered:
            margin = 'auto'
        else:
            margin = None
        self.pageSource('_pageRoot').setAttr(height=height, width=width, margin=margin)
        top = self.pbl_topBar(rootbc.borderContainer(region='top', _class='pbl_root_top',overflow='hidden'),title,flagsLocale=flagsLocale)
        bottom = self.pbl_bottomBar(rootbc.stackContainer(region='bottom', _class='pbl_root_bottom',
                                                            overflow='hidden',selectedPage='^pbl.bottom_stack'))
        bc = rootbc.borderContainer(region='center', _class='pbl_root_center')        
        return bc, top, bottom
        
    def pbl_rootContentPane(self, root, title=None, height=None, width=None, centered=False, flagsLocale=False,**kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,flagsLocale=flagsLocale)
        center = bc.contentPane(region='center', **kwargs)
        return center, top, bottom
        
    def pbl_rootStackContainer(self, root, title=None, height=None, width=None, centered=False,flagsLocale=False, **kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,flagsLocale=flagsLocale)
        center = bc.stackContainer(region='center', **kwargs)
        return center, top, bottom

    def pbl_rootTabContainer(self, root, title=None, height=None, width=None, centered=False, flagsLocale=False,**kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,flagsLocale=flagsLocale)
        center = bc.tabContainer(region='center', **kwargs)
        return center, top, bottom

    def pbl_rootBorderContainer(self, root, title=None, height=None, width=None, centered=False, flagsLocale=False,**kwargs):
        bc, top, bottom = self._pbl_root(root, title, height=height, width=width, centered=centered,flagsLocale=flagsLocale)
        center = bc.borderContainer(region='center', **kwargs)
        return center, top, bottom
        
    def pbl_topBarLeft(self,pane):
        self.pbl_workdateManager(pane)
        
    def pbl_canChangeWorkdate(self):
        return

    def pbl_workdateManager(self, pane):
        connect_onclick = None
        if self.application.checkResourcePermission(self.pbl_canChangeWorkdate(), self.userTags):
            connect_onclick='FIRE #changeWorkdate_dlg.open;'
        pane.div('^gnr.workdate', float='left', format='short',
                _class='pbl_workdate buttonIcon',
                 connect_onclick=connect_onclick)
        if connect_onclick:
            def cb_center(parentBC,**kwargs):
                pane = parentBC.contentPane(**kwargs)
                fb = pane.formbuilder(cols=1, border_spacing='5px', margin='25px',margin_top='20px')
                fb.dateTextBox(value='^.current_date',width='8em',lbl='!!Date')
            
            dlg = self.formDialog(pane,title='!!Set workdate',datapath='changeWorkdate',
                                 formId='changeWorkdate', height='100px',width='200px',
                                 cb_center=cb_center, loadsync=True)
            dlg.dataController("SET .data.current_date=date;",date="=gnr.workdate",nodeId='changeWorkdate_loader')
            dlg.dataRpc('gnr.workdate','pbl_changeServerWorkdate', newdate='=.data.current_date', 
                        _if='newdate', nodeId='changeWorkdate_saver',_onResult='FIRE .saved;')
                            
    def rpc_pbl_changeServerWorkdate(self, newdate=None):
        if newdate:
            self.workdate = newdate
        return self.workdate

    def pbl_topBar(self,top,title=None,flagsLocale=False):
        """docstring for publicTitleBar"""
        left = top.contentPane(region='left',width='250px')
        top.data('_clientCtx.mainBC.left?show',self.pageOptions.get('openMenu',True))
        menubtn = left.div(_class='pbl_menu_icon buttonIcon', float='left',
                            connect_onclick=""" var newStatus = !GET _clientCtx.mainBC.left?show
                                                SET _clientCtx.mainBC.left?show = newStatus;
                                                genro.publish('pbl_mainMenuStatus',newStatus);""",
                            subscribe_pbl_mainMenu='SET _clientCtx.mainBC.left?show=$1;')
        self.pbl_topBarLeft(left)
        right = top.contentPane(region='right', width='250px', padding_top='5px', padding_right='8px')
        right.div(connect_onclick='genro.pageBack()', _class='goback',tooltip='!!Torna alla pagina precedente')
        center = top.contentPane(region='center',margin_top='3px',overflow='hidden')
        if title:
            center.div(title,_class='pbl_title_caption')
        #right.div(connect_onclick="genro.pageBack()", title="!!Back",
        #          _class='icnBaseUpYellow buttonIcon', content='&nbsp;', float='right',margin_left='10px')
        if flagsLocale:
            right.dataRpc('aux.locale_ok', 'changeLocale', locale='^aux.locale')
            right.dataController('genro.pageReload()', _fired='^aux.locale_ok')
            right.div(connect_onclick="SET aux.locale = 'EN'", title="!!English",
                    _class='icnIntlEn buttonIcon', content='&nbsp;', float='right',margin_left='5px',margin_top='2px')
            right.div(connect_onclick="SET aux.locale = 'IT'", title="!!Italian",
                    _class='icnIntlIt buttonIcon', content='&nbsp;', float='right',margin_left='5px',margin_top='2px')
        if self.user:
            right.div(connect_onclick="genro.logout()", title="!!Logout",
                  _class='pbl_logout buttonIcon', content='&nbsp;', float='right')
            right.div(content=self.user, float='right', _class='pbl_username buttonIcon',connect_onclick='FIRE gnr.openPreference="user";')

        return center

    def pbl_bottomBar(self,bottom):
        """docstring for publicTitleBar"""
        bottom.data('pbl.bottom_stack','default')
        default_bottom = self.pbl_bottom_default(bottom.borderContainer(pageName='default'))
        self.pbl_bottom_message(bottom.contentPane(pageName='message'))
        return default_bottom

    def pbl_bottom_message(self,pane):
        pane.div('^pbl.bottomMsg', _class='pbl_messageBottom', nodeId='bottomMsg')
        pane.dataController("""
                                SET pbl.bottom_stack='message';
                                var _this = this;
                                var cb = function(){
                                    _this.setRelativeData('pbl.bottom_stack','default');
                                }
                                genro.dom.effect('bottomMsg','fadeout',{duration:1000,delay:2000,onEnd:cb});
                                
                                """, 
                              msg='^pbl.bottomMsg',_if='msg')
        
    def pbl_bottom_default(self,bc):
        left = bc.contentPane(region='left',overflow='hidden',nodeId='pbl_bottomBarLeft')
        right = bc.contentPane(region='right',overflow='hidden',nodeId='pbl_bottomBarRight')
        
        right.dataScript('gnr.localizerClass',"""return 'localizer_'+status""", 
                              status='^gnr.localizerStatus', _init=True, _else="return 'localizer_hidden'")
        if self.isDeveloper():
            right.div(connect_onclick='SET _clientCtx.mainBC.right?show = !GET _clientCtx.mainBC.right?show;', _class='icnBaseEye buttonIcon',float='right',margin_right='5px')
        if self.isLocalizer():
            right.div(connect_onclick='genro.dev.openLocalizer()', _class='^gnr.localizerClass',float='right') 
            
        center = bc.contentPane(region='center',nodeId='pbl_bottomBarCenter')        
        
        return dict(left=left,right=right,center=center)        
    
    def pbl_batch_floating(self,pane):
        
        pane.floatingPane(title='public floating',_class='shadow_4',
                                   top='80px',left='20px',width='200px',height='470px',
                                   visible=False,
                                   closable=True,resizable=True,resizeAxis='xy',maxable=True,
                                   dockable=True,dockTo='pbl_floating_dock',duration=400)
    
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
            return self.site.site_static_url('_resources','images','logo',logo_image)
    
    def custom_logo_path(self):
        logo_image = self.custom_logo_filename()
        if logo_image:
            return self.site.site_static_path('_resources','images','logo',logo_image)
        
    def custom_logo_filename(self):
        logo_folder = self.site.site_static_path('_resources','images','logo')
        logo_url=None
        if os.path.isdir(logo_folder):
            files=os.listdir(logo_folder)
            images=[f for f in files if f.startswith('%s'%'custom_logo')]
            if images:
                return images[0]
                
class ThermoDialog(BaseComponent):
    py_requires='foundation/thermo'

class UserObject(BaseComponent):
    py_requires='foundation/userobject'

class IncludedView(BaseComponent):
    py_requires='foundation/includedview'
        
class RecordHandler(BaseComponent):
    py_requires='foundation/recorddialog'

class Tools(BaseComponent):
    py_requires='foundation/tools'

class SelectionHandler(BaseComponent):
    py_requires='gnrcomponents/selectionhandler'

class RecordLinker(BaseComponent):
    py_requires='gnrcomponents/recordlinker'

class MultiSelect(BaseComponent):
    py_requires='gnrcomponents/multiselect'

class DynamicEditor(BaseComponent):
    py_requires='foundation/macrowidgets:DynamicEditor'
                        
class RecordToHtmlFrame(BaseComponent):
    py_requires='foundation/htmltoframe'
    
