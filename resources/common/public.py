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
        pane = self.pageSource()
        userTable = self.pbl_userTable()
        if not self.isGuest and userTable:
            pane.dataRecord('gnr.user_record', userTable, username=self.user, _init=True)
        pane.data('gnr.workdate', self.workdate)
        
                              
    def pbl_userTable(self):
        return 'adm.user'
        
    def rootWidget(self, root, **kwargs):
        return root.contentPane(_class='pbl_root', **kwargs)
        
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
        self.root_publicframe = frame
        return frame
        
    def public_frameTopBarSlots(self,baseslot):
        return baseslot
        
    def public_frameTopBar(self,pane,slots=None,title=None,**kwargs):
        pane.attributes.update(dict(_class='pbl_root_top'))
        baseslots = '10,caption,*,avatar,10'
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
    def public_publicRoot_avatar(self,pane,frameCode=None,**kwargs):
        pane.div(datasource='^gnr.rootenv',template=self.pbl_avatarTemplate(),**kwargs)
    
    def pbl_avatarTemplate(self):
        return '<div class="pbl_slotbar_label buttonIcon">$workdate<div>'

#######################OLD SLOTS#######################

            
    @struct_method
    def public_publicRoot_caption(self,pane,title='',**kwargs):  
        if title:
            pane.data('gnr.publicTitle',title) 
        pane.div('^gnr.publicTitle', _class='pbl_title_caption',
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
    
    def mainLeftContent(self,pane,**kwargs):
        return
    
    #DA RIVEDERE
    @struct_method
    def th_slotbar_mainFilter(self,pane,**kwargs):
        pane.slotButton(tip='!!Set Filter', iconClass='iconbox th_filterButton',
                        action='SET .query.activeFilter = !GET .query.activeFilter')
        pane.dataController(""" var filter;
                                if (activeFilter==true){
                                    filter = query.deepCopy();
                                    console.log(filter);
                                }else if(activeFilter==false){
                                    filter = null;
                                }
                                 SET .query.currentFilter = filter;
                            """, currentFilter='=.query.currentFilter',
                            query='=.query.where',
                            pagename=self.pagename,activeFilter="^.query.activeFilter")
        pane.dataController("genro.dom.setClass(pane,'th_filterActive',activeFilter)",
                activeFilter='^.query.activeFilter', _onStart=True,pane=pane.parent.parent.parent)
                
    def th_options(self):
        return dict()

    def main(self,root,**kwargs):
        root.rootTableHandler(**kwargs)
    
    def rootWidget(self, root, **kwargs):
        return root.contentPane(_class='pbl_root', **kwargs)
        
    @extract_kwargs(th=True)
    @struct_method
    def pbl_rootTableHandler(self,root,th_kwargs=None,**kwargs):
        self.th_iframeContainerId = kwargs.pop('th_iframeContainerId',None)
        th_options = dict(formResource=None,viewResource=None,formInIframe=False,widget='stack',
                        readOnly=False,virtualStore=True,public=True)
        viewResource = th_kwargs.get('viewResource',None) or self.th_options().get('viewResource',None)
        resource = self._th_getResClass(table=self.maintable,resourceName=viewResource,defaultClass='View')()
        resource_options = resource.th_options() if hasattr(resource,'th_options') else dict()
        th_options.update(self.th_options())
        th_options.update(resource_options)
        th_options.update(th_kwargs)
        return self._th_main(root,th_options=th_options,**kwargs)
        
    def _th_main(self,root,th_options=None,**kwargs):
        formInIframe = boolean(th_options.get('formInIframe'))
        th_public = th_options.get('public',True)
        publicCollapse = th_public=='collapse'
        insidePublic = False
        if not publicCollapse:
            insidePublic = boolean(th_public) is True
        tablecode = self.maintable.replace('.','_')
        kwargs.update(th_options)
        extendedQuery = kwargs.pop('extendedQuery','*') 
        lockable = kwargs.pop('lockable',True)           
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
        th = getattr(root,'%sTableHandler' %thwidget)(table=self.maintable,datapath=tablecode,lockable=lockable,
                                                      extendedQuery=extendedQuery,**kwargs)
        self.root_tablehandler = th
        vstore = th.view.store
        viewbar = th.view.top.bar

        if publicCollapse:
            th.view.attributes.update(_class='pbl_root')
            viewbar.attributes.update(toolbar=False,_class='slotbar_toolbar pbl_root_top',height='22px')
            if not hasattr(th.view.bottom,'bar'):
                self.public_frameBottomBar(th.view.bottom)
            else:
                th.view.bottom.bar.attributes.update(_class='slotbar_toolbar pbl_root_bottom')
            viewbar.replaceSlots('#','#,avatarslot,10')
            viewbar.replaceSlots('5,vtitle','10,captioslot')
            viewbar.avatarslot.publicRoot_avatar(margin_top='-2px')
            viewbar.captioslot.publicRoot_caption()
        storeupd = dict(startLocked=lockable)
        if not extendedQuery:
            storeupd['_onStart'] = True
        vstore.attributes.update(storeupd)
        if len(extras)>0:
            viewbar.replaceSlots('resourceMails','resourceMails,5,%s' %','.join(extras))  
        if insidePublic and hasattr(self,'customizePublicFrame'):
            self.customizePublicFrame(root)
        th.view.attributes.update(dict(border='0',margin='0', rounded=0))
        self.__th_title(th,thwidget,insidePublic or publicCollapse,extendedQuery=extendedQuery)
        self.__th_moverdrop(th)
        if hasattr(th,'form') and insidePublic and not formInIframe:
            self._usePublicBottomMessage(th.form)
        if th_options.get('filterSlot'):
            th.view.top.bar.replaceSlots('queryMenu','queryMenu,2,mainFilter')
        return th
        
    def __th_moverdrop(self,th):
        gridattr = th.view.grid.attributes
        currCodes = gridattr.get('dropTarget_grid')
        currCodes = currCodes.split(',') if currCodes else []
        tcode = 'mover_%s' %self.maintable.replace('.','_')
        if not tcode in currCodes:
            currCodes.append(tcode)
            gridattr['onDrop_%s' %tcode] = "genro.serverCall('developer.importMoverLines',{table:data.table,pkeys:data.pkeys,objtype:data.objtype});"
        gridattr.update(dropTarget_grid=','.join(currCodes))
        

    def __th_title(self,th,widget,insidePublic,extendedQuery=None):
        if insidePublic:
            th.view.top.bar.replaceSlots('vtitle','')
            if widget=='stack' or widget=='dialog':
                th.dataController("""var title = (selectedPage!='form'?viewtitle:formtitle)||currTitle;
                                     genro.setData("gnr.publicTitle",title,{selectionName:selectionName,table:table,objtype:'record'});
                            """,
                            formtitle='^.form.controller.title',viewtitle='^.view.title',
                            selectionName='^.view.store?selectionName',table='=.view.table',
                            selectedPage='^.selectedPage',currTitle='=gnr.publicTitle') 
                if not extendedQuery:
                    th.view.top.bar.replaceSlots('count','')
                    th.view.top.bar.replaceSlots('searchOn','')
                    th.view.top.bar.replaceSlots('#','5,searchOn,count,#')                
            else:
                th.dataFormula('gnr.publicTitle','viewtitle',viewtitle='^.view.title',_onStart=True)
    
  # @struct_method
  # def public_publicRoot_caption(self,pane,title='',**kwargs):  
  #     if title:
  #         pane.data('gnr.publicTitle',title) 
  #     pane.div('^gnr.publicTitle', _class='pbl_title_caption',
  #                 draggable=True,onDrag='dragValues["webpage"] = genro.page_id;',**kwargs)           

    @extract_kwargs(th=True)
    def _th_prepareForm(self,root,pkey=None,th_kwargs=None,store_kwargs=None,formCb=None,**kwargs):
        pkey = pkey or th_kwargs.pop('pkey',None)
        formResource = th_kwargs.pop('formResource',None)
        root.attributes.update(overflow='hidden')
        public = boolean(th_kwargs.pop('public',False))
        formId = th_kwargs.pop('formId',self.maintable.replace('.','_'))
        if  public:
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
        if public:
            form.dataController("""
                            SET gnr.publicTitle = title;
                            """,title='^#FORM.controller.title')  

        if th_kwargs.get('showfooter',True):
            self._usePublicBottomMessage(form)
        return form

    def _usePublicBottomMessage(self,form):
        form.attributes['hasBottomMessage'] = False
        form.dataController('PUBLISH pbl_bottomMsg = _subscription_kwargs;',formsubscribe_message=True)
        
    @public_method                     
    def main_form(self, root,**kwargs):
        """ALTERNATIVE MAIN CALL"""
        callArgs =  self.getCallArgs('th_pkg','th_table','th_pkey') 
        pkey = callArgs.pop('th_pkey',None)
        formCb = self.th_form if hasattr(self,'th_form') else None
        self._th_prepareForm(root,formCb=formCb,pkey=pkey,**kwargs)
    
        
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
                                    