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
    py_requires = 'foundation/menu:Menu,foundation/dialogs,foundation/macrowidgets'
        
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
        bc = parentBC.borderContainer(width='20%',_class='menupane',**kwargs)
        logo_pane = bc.contentPane(region='bottom',_class='menupane_pref')
        #logo_path = self.site.site_static_path('data','adm','logo.png')
       #if not os.path.isfile(logo_path):
       #    logo_path = self.getResourceUri('images/information.png')
       #logo_pane.img(src=logo_path,connect_onclick='FIRE gnr.openAppPreference;',
       #             _class='buttonIcon',float='right',width="100px",height="50px",border='1px solid white')
        logo_pane.button('!!Preferences',float='right',action='FIRE gnr.openPreference="app";')
        self.pbl_preference_main(logo_pane)
        menu_pane = bc.contentPane(region='center',_class='menutree_container',overflow='auto')
        self.menu_menuPane(menu_pane)
    
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
                             cached=False,height='400px',width='600px',centerOn='_pageRoot',datapath='gnr.preference.application')
            self.iframeDialog(pane,title='!!User Preference',dlgId='userpreference',src='/adm/user_preference',
                             cached=False,height='300px',width='400px',centerOn='_pageRoot',datapath='gnr.preference.user')
        
    def pbl_userTable(self):
        return 'adm.user'
        
    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='pbl_root',**kwargs)
        
    def _pbl_root(self, rootbc, title=None, height=None, width=None, centered=None,flagsLocale=False):
        userTable=self.pbl_userTable()
        if self.user and userTable:
            rootbc.dataRecord('gnr.user_record',userTable, username=self.user, _init=True)
        rootbc.data('gnr.workdate', self.workdate)
        if centered:
            margin = 'auto'
        else:
            margin = None
        self.pageSource('_pageRoot').setAttr(height=height, width=width, margin=margin)
        top = self.pbl_topBar(rootbc.borderContainer(region='top', _class='pbl_root_top',overflow='hidden'),title,flagsLocale=flagsLocale)
        bottom = self.pbl_bottomBar(rootbc.borderContainer(region='bottom', _class='pbl_root_bottom',overflow='hidden'))
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
        menubtn = left.div(_class='pbl_menu_icon buttonIcon', float='left',
                            connect_onclick="""SET _clientCtx.mainBC.left?show = !GET _clientCtx.mainBC.left?show;
                            """)
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
        left = bottom.contentPane(region='left',width='25%', overflow='hidden',nodeId='pbl_bottomBarLeft')
        right = bottom.contentPane(region='right', width='25%', overflow='hidden',nodeId='pbl_bottomBarRight')
        center = bottom.contentPane(region='center',nodeId='pbl_bottomBarCenter')
        center.div('^pbl.bottomMsg', _class='pbl_messageBottom', nodeId='bottomMsg')
        
        right.dataScript('gnr.localizerClass',"""return 'localizer_'+status""", 
                              status='^gnr.localizerStatus', _init=True, _else="return 'localizer_hidden'")
        if self.isDeveloper():
            right.div(connect_onclick='SET _clientCtx.mainBC.right?show = !GET _clientCtx.mainBC.right?show;', _class='icnBaseEye buttonIcon',float='right',margin_right='5px')
        if self.isLocalizer():
            right.div(connect_onclick='genro.dev.openLocalizer()', _class='^gnr.localizerClass',float='right') 
        center.dataController("genro.dom.effect('bottomMsg','fadeout',{duration:3000,delay:3000});", 
                          msg='^pbl.bottomMsg',_if='msg')
        return dict(left=left,right=right,center=center)
        
    def cssmake(self,rounded=None,shadow=None,gradient=None,style=''):
        result=[]
        if rounded:
            for x in rounded.split(','):
                side,r=x.split(':')
                side=side.lower()
                if side=='all':
                    result.append('-moz-border-radius:%spx;'%r)
                    result.append('-webkit-border-radius:%spx;'%r)
                else:
                    if side in ('tl','topleft','top','left'):
                        result.append('-moz-border-radius-topleft:%spx;'%r)
                        result.append('-webkit-border-top-left-radius:%spx;'%r)
                    if side in ('tr','topright','top','right'):
                        result.append('-moz-border-radius-topright:%spx;'%r)
                        result.append('-webkit-border-top-right-radius:%spx;'%r)
                    if side in ('bl','bottomleft','bottom','left'):    
                        result.append('-moz-border-radius-bottomleft:%spx;'%r)
                        result.append('-webkit-border-bottom-left-radius:%spx;'%r)
                    if side in ('br','bottomright','bottom','right'):
                        result.append('-moz-border-radius-bottomright:%spx;'%r)
                        result.append('-webkit-border-bottom-right-radius:%spx;'%r)
        if shadow:
            x,y,blur,color=shadow.split(',')
            result.append('-moz-box-shadow:%spx %spx %spx %s;'%(x,y,blur,color))
            result.append('-webkit-box-shadow:%spx %spx %spx %s;'%(x,y,blur,color))
       #if gradient:
       #    
       #
       # background-image:-webkit-gradient(linear, 0% 0%, 0% 90%, from(rgba(16,96,192,0.75)), to(rgba(96,192,255,0.9)));
       #    background-image:-moz-linear-gradient(top,bottom,from(rgba(16,96,192,0.75)), to(rgba(96,192,255,0.9)));
       #    result.append('background-image:-moz-linear-gradient(top,bottom,from(rgba(16,96,192,0.75)), to(rgba(96,192,255,0.9)));')
       #    result.append('-webkit-box-shadow:%spx %spx %spx %s;'%(x,y,blur,color))
       #    # -moz-linear-gradient( [<point> || <angle>,]? <stop>, <stop> [, <stop>]* )
            # -moz-radial-gradient( [<position> || <angle>,]? [<shape> || <size>,]? <stop>, <stop>[, <stop>]* )
            # 
            # -moz-linear-gradient (%(begin)s, %(from)s, %(to)s);
            # -webkit-gradient (%(mode)s, %(begin)s, %(end)s, from(%(from)s), to(%(to)s));
            # 
        return '%s\n%s' % ('\n'.join(result) ,style)         
    
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

class DynamicEditor(BaseComponent):
    py_requires='foundation/macrowidgets:DynamicEditor'
                        
class RecordToHtmlFrame(BaseComponent):
    py_requires='foundation/htmltoframe'
    
