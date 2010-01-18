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

class Public(BaseComponent):
    """docstring for Public for common_d11: a complete restyling of Public of common_d10"""
    css_requires = 'public,themes/blue'
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
        self.menu_menuPane(parentBC,**kwargs)

        
    def pbl_userTable(self):
        return 'adm.user'
        
    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='pbl_root', **kwargs)
        
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
        pane.div('^gnr.workdate', float='left', format='short', color='white',
                _class='pbl_workdate buttonIcon',connect_onclick='FIRE gnr.dlg_workdate.show;')

    def pbl_workdate(self,pane):
        pane.dataController('genro.wdgById("gnr_workdate_dlg").show();',
                            _fired = '^gnr.dlg_workdate.show')
        pane.dataController('genro.wdgById("gnr_workdate_dlg").hide();',
                            _fired = '^gnr.dlg_workdate.hide')
                            
        bc = pane.dialog(nodeId= 'gnr_workdate_dlg',
                               title='!!Change workdate'
                               ).borderContainer(height='64px',
                                width='240px',datapath='gnr.dlg_workdate')
        dlg_bottom = bc.contentPane(region='bottom', _class='dialog_bottom')
        dlg_bottom.button('!!Change', float='right',baseClass='bottom_btn',
                          action='FIRE .setWorkdate; FIRE .hide;')
        dlg_bottom.button('!!Cancel', float='left',fire='.hide',baseClass='bottom_btn')
        dlg_top = bc.contentPane(region='center', _class='pbl_roundedGroup')
        fld = dlg_top.div(margin_left='30px')
        fld.div("Data: ", float='left',margin='5px')
        fld.dateTextBox(value='^.workdate',width='6em', margin='5px')
                                 
        pane.dataController('.gnr.workdate','changeServerWorkdate', newdate='=.workdate',
                            _if='newdate', _fired='^.setWorkdate')
                            
    def rpc_changeServerWorkdate(self, newdate=None):
        if newdate:
            self.workdate = newdate
        return self.workdate

    def pbl_topBar(self,top,title=None,flagsLocale=False):
        """docstring for publicTitleBar"""
        left = top.contentPane(region='left',width='200px')
        menubtn = left.div(_class='pbl_logo_icon buttonIcon', float='left',
                            connect_onclick="""SET _clientCtx.mainBC.left?show = !GET _clientCtx.mainBC.left?show;
                            """)
        self.pbl_topBarLeft(left)
        right = top.contentPane(region='right', width='200px', padding_top='5px', padding_right='8px')
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
                  _class='icnBaseLogout buttonIcon', content='&nbsp;', float='right')
            right.div(content=self.user, float='right', _class='pbl_username buttonIcon')

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
                        
class ThermoDialog(BaseComponent):
    py_requires='foundation/thermo'

class UserObject(BaseComponent):
    py_requires='foundation/userobject'

class IncludedView(BaseComponent):
    py_requires='foundation/includedview'
        
class RecordHandler(BaseComponent):
    py_requires='foundation/recorddialog'

class DynamicEditor(BaseComponent):
    py_requires='foundation/dynamiceditor'
                        
class RecordToHtmlFrame(BaseComponent):
    py_requires='foundation/htmltoframe'
    
