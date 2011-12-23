#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  public.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" public common11 """

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrstring import boolean
import os

class PublicBase(BaseComponent):
    #css_requires = 'public'
    py_requires = """public:PublicSlots"""
                     
    def userRecord(self, path=None):
        if not hasattr(self, '_userRecord'):
            user = self.pageArgs.get('_user_')
            if not user or not( 'passpartout' in self.userTags):
                user = self.user
            self._userRecord = self.db.table('adm.user').record(username=user).output('bag')
        return self._userRecord[path]
        
    def onMain_pbl(self):
        self._init_pbl()
        
    def _init_pbl(self):
        pane = self.pageSource()
        userTable = self.pbl_userTable()
        if not self.isGuest and userTable:
            pane.dataRecord('gnr.user_record', userTable, username=self.user, _init=True)
        pane.data('gnr.workdate', self.workdate)
        if self.root_page_id:
            return
            
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
                     top_kwargs=None,bottom_kwargs=None,center_class=None,bottom=True,**kwargs):
        frame = rootbc.framePane(frameCode='publicRoot',region='center', center_class=center_class or 'pbl_root_center',
                                **kwargs)
        frame.data('_clientCtx.mainBC.left?show', self.pageOptions.get('openMenu', True))
        self.public_frameTopBar(frame.top,title=title,**top_kwargs)
        if bottom:
            self.public_frameBottomBar(frame.bottom,**bottom_kwargs)
        return frame
        
    def public_frameTopBarSlots(self,baseslot):
        return baseslot
        
    def public_frameTopBar(self,pane,slots=None,title=None,**kwargs):
        pane.attributes.update(dict(_class='pbl_root_top'))
        baseslots = 'menuBtn,workdate,*,caption,*,user,logout,5'
        if self.root_page_id:
            baseslots = '10,caption,*,workdate,10'
            kwargs['margin_top'] ='2px'
        slots = slots or self.public_frameTopBarSlots(baseslots)
        if 'caption' in slots:
            kwargs['caption_title'] = title
        return pane.slotBar(slots=slots,childname='bar',
                            **kwargs)
                            
    def public_frameBottomBar(self,pane,slots=None,**kwargs):
        slots = slots or '5,dock,*,messageBox,*,devBtn,locBtn,5'
        if 'messageBox' in slots:
            pane.parent.dataController("genro.publish('pbl_bottomMsg',{message:msg});",msg="^pbl.bottomMsg") #legacy
            kwargs['messageBox_subscribeTo']=kwargs.get('messageBox_subscribeTo') or 'pbl_bottomMsg'
        return pane.slotBar(slots=slots,childname='bar',
                            _class='pbl_root_bottom',
                            **kwargs)
            
    @struct_method
    def public_rootStackContainer(self, root, title=None, height=None, width=None,selectedPage=None,**kwargs):
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
        dlg.dataRpc('gnr.workdate', self.setWorkdate, workdate='=.data.current_date',
                    _if='workdate', nodeId='changeWorkdate_saver', 
                    _onResult="FIRE .saved; PUBLISH pbl_changed_workdate = {workdate:result};")

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

    
    
class Public(PublicBase):
    """docstring for Public for common_d11: a complete restyling of Public of common_d10"""
    css_requires = 'public'
    plugin_list = 'menu_plugin,batch_monitor,chat_plugin'
    js_requires = 'public'
    py_requires = """foundation/menu:MenuLink,
                     foundation/dialogs,
                     foundation/macrowidgets,
                     public:PublicSlots,
                     gnrcomponents/batch_handler/batch_handler:BatchMonitor,
                     gnrcomponents/chat_component/chat_component:ChatComponent"""
                     

class PublicSlots(BaseComponent):
    @struct_method
    def public_slotbar_workdateBtn(self,pane,iconClass=False,**kwargs):
        pane.data('gnr.workdate', self.workdate)
        dlg = pane.dialog(title='!!New Workdate',closable=True)
        frame = dlg.framePane(height='100px',width='200px',datapath='gnr.workdatemanager')
        frame.dataRpc('gnr.workdate',self.setWorkdate,workdate='=.date',_if='workdate',_fired='^.confirm',
                        _onResult='PUBLISH pbl_changed_workdate = {workdate:result};')
        fb = frame.formbuilder(cols=1, border_spacing='5px', margin='25px', margin_top='20px')
        fb.dateTextBox(value='^.date', width='8em', lbl='!!Date')
        footer = frame.bottom.slotBar('*,confirmbtn')
        footer.confirmbtn.button('!!Confirm',action='FIRE .confirm;dlg.widget.hide();',dlg=dlg)
        btnkw = dict(connect_onclick='this.getAttributeFromDatasource("dlg").widget.show(); SET gnr.workdatemanager.date=GET gnr.workdate;',
                 _class=iconClass or 'pbl_slotbar_label buttonIcon',dlg=dlg)
        btnkw.update(kwargs)
        if not iconClass:
            pane.div('^gnr.workdate', format='short',**btnkw)
        else:
            pane.div(**btnkw)
        


#######################OLD SLOTS#######################

    @struct_method
    def public_publicRoot_workdate(self,pane,**kwargs):
        connect_onclick = None
        if self.application.checkResourcePermission(self.pbl_canChangeWorkdate(), self.userTags):
            connect_onclick = 'FIRE #changeWorkdate_dlg.open;'
        pane.div('^gnr.workdate', format='short',
                 _class='pbl_slotbar_label buttonIcon',
                 connect_onclick=connect_onclick)
        if connect_onclick:
            self.pbl_workdate_dialog()
            
    @struct_method
    def pbl_publicRoot_menuBtn(self,pane,**kwargs):
        pane.div(_class='pbl_menu_icon buttonIcon', connect_onclick="""
                                if(this.attr._inframe){
                                    genro.publish({'topic':'main_left_set_status',parent:true},'toggle');
                                }else{
                                    PUBLISH main_left_set_status= 'toggle';
                                }
                                """,_inframe=self.root_page_id)
            
    @struct_method
    def public_publicRoot_caption(self,pane,title='',**kwargs):   
        pane.div(title, _class='pbl_title_caption',
                    subscribe_setWindowTitle='this.domNode.innerHTML=$1;',
                    draggable=True,onDrag='dragValues["webpage"] = genro.page_id;',**kwargs)
                    
    @struct_method
    def public_publicRoot_pageback(self,pane,**kwargs): 
        pane.div(connect_onclick="genro.pageBack()", title="!!Back",
                 _class='icnBaseUpYellow buttonIcon', content='&nbsp;',**kwargs)
                 
    @struct_method
    def public_publicRoot_flagsLocale(self,pane,**kwargs): 
            pane.dataRpc('aux.locale_ok', 'changeLocale', locale='^aux.locale')
            pane.dataController('genro.pageReload()', _fired='^aux.locale_ok')
            pane.button(action="SET aux.locale = 'EN'", title="!!English",
                        _class='icnIntlEn buttonIcon')
            pane.button(action="SET aux.locale = 'IT'", title="!!Italian",
                        _class='icnIntlIt buttonIcon')
                        
    @struct_method
    def public_publicRoot_user(self,pane,**kwargs):
        if not self.isGuest:
            pane.div(content=self.user, float='right', _class='pbl_slotbar_label buttonIcon',
                      connect_onclick='PUBLISH preference_open="user";',**kwargs)
        else:
            pane.div()
            
    @struct_method
    def public_publicRoot_logout(self,pane,**kwargs):
        if not self.isGuest:
            pane.div(connect_onclick="genro.logout()", title="!!Logout",
                      _class='pbl_logout buttonIcon', content='&nbsp;',**kwargs)
        else:
            pane.div()
            
    @struct_method
    def public_publicRoot_dock(self,pane,**kwargs):
        pane.dock(id='default_dock', background='none', border=0)
        
    @struct_method
    def public_publicRoot_locBtn(self,pane,**kwargs):
        if self.isLocalizer():
            pane.div(connect_onclick='genro.dev.openLocalizer()', _class='^gnr.localizerClass', float='right')
            pane.dataFormula('gnr.localizerClass', """ 'localizer_'+status;""",
                            status='^gnr.localizerStatus', _init=True, 
                            _else="return 'localizer_hidden'")
        else:
            pane.div()
            
    @struct_method
    def public_publicRoot_devBtn(self,pane,**kwargs):
        if self.isDeveloper():
            pane.div(connect_onclick='genro.dev.showDebugger();',
                      _class='icnBaseEye buttonIcon', float='right', margin_right='5px')
        else:
            pane.div()


class TableHandlerMain(BaseComponent):
    py_requires = """public:Public,th/th:TableHandler"""
    plugin_list=''
    formResource = None
    viewResource = None
    formInIframe = False
    th_widget = 'stack'
    th_readOnly = False
    maintable = None
    
    def th_options(self):
        return dict()
        
    def onMain_pbl(self):
        pass
        
    def main(self,root,**kwargs):
        root.rootTableHandler(**kwargs)
    
    def rootWidget(self, root, **kwargs):
        return root.contentPane(_class='pbl_root', **kwargs)
        
    @extract_kwargs(th=True)
    @struct_method
    def pbl_rootTableHandler(self,root,th_kwargs=None,**kwargs):
        kwargs.update(self.getCallArgs('th_pkey'))
        th_options = dict(formResource=None,viewResource=None,formInIframe=False,widget='stack',readOnly=False,virtualStore=True,public=True)
        th_options.update(self.th_options())
        th_options.update(th_kwargs)
        self.root_tablehandler = self._th_main(root,th_options=th_options,**kwargs)
        return self.root_tablehandler
        
    def _th_main(self,root,th_options=None,**kwargs):
        formInIframe = th_options.get('formInIframe')
        insidePublic = th_options.get('public')
        tablecode = self.maintable.replace('.','_')
        th_options['lockable'] = th_options.get('lockable',True)
        kwargs.update(th_options)
        kwargs['extendedQuery'] = kwargs.get('extendedQuery',True)
        if insidePublic:
            root = root.rootContentPane(title=self.tblobj.name_long,datapath=tablecode)
        else:
            root.attributes.update(_class=None,datapath=tablecode)
        extras = []
        if hasattr(self,'stats_main') or hasattr(self,'hv_main'):
            tc = root.stackContainer(selectedPage='^.view.selectedPage')
            root = tc.contentPane(title='!!Main View',pageName='th_main')
            if hasattr(self,'stats_main'):
                extras.append('statisticalHandler')
                self.stats_main(tc,title='!!Statistical View')
            if hasattr(self,'hv_main'):
                extras.append('hierarchicalHandler')
                self.hv_main(tc)
        thwidget = th_options.get('widget','stack')
        th = getattr(root,'%sTableHandler' %thwidget)(table=self.maintable,datapath=tablecode,**kwargs)
        th.view.store.attributes.update(startLocked=True)
        if len(extras)>0:
            viewbar = th.view.top.bar
            viewbar.replaceSlots('resourceMails','resourceMails,5,%s' %','.join(extras))  
        if insidePublic and hasattr(self,'customizePublicFrame'):
            self.customizePublicFrame(root)

        th.attributes.update(dict(border_left='1px solid gray'))
        th.view.attributes.update(dict(border='0',margin='0', rounded=0))
        self.__th_title(th,thwidget,insidePublic)
        self.__th_moverdrop(th)
        if insidePublic and not formInIframe:
            self._usePublicBottomMessage(th.form)
        return th
        
    def __th_moverdrop(self,th):
        gridattr = th.view.grid.attributes
        currCodes = gridattr.get('dropTarget_grid','').split(',')
        tcode = 'mover_%s' %self.maintable.replace('.','_')
        if not tcode in currCodes:
            currCodes.append(tcode)
            gridattr['onDrop_%s' %tcode] = "genro.serverCall('developer.importMoverLines',{table:data.table,pkeys:data.pkeys,objtype:data.objtype});"
        gridattr.update(dropTarget_grid=','.join(currCodes))
        
    def __th_title(self,th,widget,insidePublic):
        if insidePublic:
            th.view.top.bar.replaceSlots('vtitle','')
            if widget=='stack' or widget=='dialog':
                th.dataController("""
                                     console.log(selectedPage,viewtitle,formtitle);
                                     var title = (selectedPage=='view'?viewtitle:formtitle)||currTitle;
                                     genro.setData("gnr.windowTitle",title,{selectionName:selectionName,table:table,objtype:'record'});
                            """,
                            formtitle='^.form.controller.title',viewtitle='^.view.title',
                            selectionName='^.view.store?selectionName',table='=.view.table',
                            selectedPage='^.selectedPage',currTitle='=gnr.windowTitle') 
                
            else:
                th.dataFormula('gnr.windowTitle','viewtitle',viewtitle='^.view.title',_onStart=True)
    
    @struct_method
    def public_publicRoot_caption(self,pane,title='',**kwargs):   
        pane.div(title, _class='pbl_title_caption',
                    subscribe_setWindowTitle='this.domNode.innerHTML=$1;',
                    draggable=True,
                    onDrag="""dragValues["webpage"] = genro.page_id;
                              dragValues["dbrecords"] = genro.getDataNode("gnr.windowTitle").attr;
                                """,**kwargs)
    
    @public_method                     
    def pbl_form_main(self, root,**kwargs):
        callArgs =  self.getCallArgs('th_pkg','th_table','th_pkey') 
        pkey = callArgs.pop('th_pkey',None)
        kwargs.update(pkey=pkey)
        formCb = self.th_form if hasattr(self,'th_form') else None
        self._th_prepareForm(root,formCb=formCb,**kwargs)
                
    
    @extract_kwargs(th=True)
    def _th_prepareForm(self,root,pkey=None,th_kwargs=None,store_kwargs=None,formCb=None,**kwargs):
        pkey = pkey or th_kwargs.pop('pkey','*norecord*')
        formResource = th_kwargs.pop('formResource',None)
        root.attributes.update(overflow='hidden')
        public = boolean(th_kwargs.pop('public',False))
        formId = th_kwargs.pop('formId',self.maintable.replace('.','_'))
        if  public:
            self._init_pbl()
            root.attributes.update(_class='pbl_root')
            root = root.rootContentPane(title=self.tblobj.name_long)
        else:
            root.attributes.update(tag='ContentPane',_class=None)
        root.attributes.update(datapath=self.maintable.replace('.','_'))
        formkw = kwargs
        formkw.update(th_kwargs)
        form = root.thFormHandler(table=self.maintable,formId=formId,startKey=pkey,
                                  formResource=formResource,
                                  formCb=formCb,form_isRootForm=True,**formkw)
        form.dataController("""SET gnr.windowTitle = title;
                            """,title='=.controller.title')    
        if th_kwargs.get('showfooter',True):
            self._usePublicBottomMessage(form)
        return form

    def _usePublicBottomMessage(self,form):
        form.attributes['hasBottomMessage'] = False
        form.dataController('PUBLISH pbl_bottomMsg = _subscription_kwargs;',formsubscribe_message=True)
        
    def rpc_view(self,root,**kwargs):
        pass
        
#OLD STUFF TO REMOVE
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
                                    