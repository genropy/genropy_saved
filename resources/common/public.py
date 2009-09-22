#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" public common11 """
import os
import time
import datetime

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

from gnr.core.gnrstring import templateReplace, splitAndStrip

from gnr.core.gnrlocale import DATEKEYWORDS
from gnr.web.gnrwebpage import BaseComponent

# --------------------------- GnrWebPage subclass ---------------------------
class Public(BaseComponent):
    """docstring for Public for common_d11: a complete restyling of Public of common_d10"""
    css_requires = 'public'
    js_requires = 'public'
        
    def userRecord(self,path=None):
        if not hasattr(self,'_userRecord' ):
            user = self.pageArgs.get('_user_')
            if not user or not( 'passpartout' in self.userTags):
                user =  self.user
            self._userRecord=self.db.table('adm.user').record(username=user).output('bag')
        return self._userRecord[path]

    def onMain_pbl(self):
        self.pageSource().data('gnr.appmenu',self.getUserMenu())
        
    def mainLeftContent(self,parentBC,**kwargs):
        leftPane = parentBC.contentPane(width='20%',_class='menupane',**kwargs)
        leftPane = leftPane.div()
        leftPane.tree(id="_gnr_main_menu_tree",storepath='gnr.appmenu',selected_file='gnr.filepath',
                       labelAttribute='label',
                       hideValues=True,
                       _class='menutree',
                       persist='site',
                       inspect='shift',
                       identifier='#p',
                       getIconClass='return node.attr.iconClass || "treeNoIcon"',
                       getLabelClass='return node.attr.labelClass',
                       openOnClick=True,
                       #connect_onClick='genro.gotoURL($1.getAttr("file"),true)',
                       #getLabel="""return "<a href='"+node.attr.file+"'>"+node.attr.label+"</a>::HTML";""",
                       getLabel="""if(node.attr.file){ return 'innerHTML:<a href="'+node.attr.file+'"><div style="width:100%;height:100%;">'+node.attr.label+'</div></a>'}else  {return node.attr.label};""",
                       nodeId='_menutree_')
        leftPane.dataController("genro.wdgById('_gnrRoot').showHideRegion('left', false);",fired='^gnr.onStart',
                                appmenu="=gnr.appmenu",_if="appmenu.len()==0")

    def getUserMenu(self):
        def userMenu(userTags,menubag,level,basepath):
            result = Bag()
            if not userTags:
                return result
            for node in menubag.nodes:
                allowed=True
                if node.getAttr('tags'):
                    allowed=self.application.checkResourcePermission(node.getAttr('tags'), userTags)
                if allowed and node.getAttr('file'):
                    allowed = self.checkPermission(node.getAttr('file'))
                if allowed:
                    value=node.getStaticValue()
                    attributes={}
                    attributes.update(node.getAttr())
                    currbasepath=basepath
                    if 'basepath' in attributes:
                        newbasepath=node.getAttr('basepath')
                        if newbasepath.startswith('/'):
                            currbasepath=[newbasepath]
                        else:
                            currbasepath=basepath+[newbasepath]
                    if isinstance(value,Bag):
                        value = userMenu(userTags,value,level+1,currbasepath)
                        labelClass = 'menu_level_%i' %level 
                    else:
                        value=None
                        labelClass = 'menu_page'
                    attributes['labelClass'] = 'menu_shape %s' %labelClass
                    filepath=attributes.get('file')
                    if filepath and not filepath.startswith('/'):
                        attributes['file'] = os.path.join(*(currbasepath+[filepath]))
                    result.setItem(node.label,value,attributes)
            return result
        result=userMenu(self.userTags,self.application.config['menu'],0,[])
        while len(result)==1:
            result=result['#0']
        return result
        
    def pageMenues(self):
        pass

    def addPageMenu(self,name,url):
        """docstring for addPageMenu"""
        if self.checkPermission(url):
            self._pageMenues.append((name,url))
            
    def pbl_linkButton(self, pane, lbl, url, **kwargs):
        if url=='BACK':
            action='genro.pageBack()'
        elif url=='LOGOUT':
            action='genro.logout()'
        elif url=='HOME':
            action='genro.gotoHome()'
        elif self.checkPermission(url):
            action= "genro.gotoURL('%s')"%url
        else:
            return
        pane.button(lbl, action=action, width='12em', **kwargs)
        
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
        pane.div('^gnr.workdate', float='left', format='short', color='white', _class='pbl_workdate buttonIcon')

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
        right.div(connect_onclick="genro.pageBack()", title="!!Back",
                  _class='icnBaseUpYellow buttonIcon', content='&nbsp;', float='right',margin_left='10px')
        if flagsLocale:
            right.dataRpc('aux.locale_ok', 'changeLocale', locale='^aux.locale')
            right.dataController('genro.pageReload()', _fired='^aux.locale_ok')
            right.div(connect_onclick="SET aux.locale = 'EN'", title="!!English",
                    _class='icnIntlEn buttonIcon', content='&nbsp;', float='right',margin_left='5px',margin_top='2px')
            right.div(connect_onclick="SET aux.locale = 'IT'", title="!!Italian",
                    _class='icnIntlIt buttonIcon', content='&nbsp;', float='right',margin_left='5px',margin_top='2px')
        if self.user:
            right.div(connect_onclick="genro.serverCall('connection.logout');genro.gotoHome()", title="!!Logout",
                  _class='icnBaseLogout buttonIcon', content='&nbsp;', float='right')
            right.div(content=self.user, float='right', _class='pbl_username buttonIcon')

        return center

    def pbl_bottomBar(self,bottom):
        """docstring for publicTitleBar"""
        left = bottom.contentPane(region='left',width='25%', overflow='hidden')
        right = bottom.contentPane(region='right', width='25%', overflow='hidden')
        center = bottom.contentPane(region='center')
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
    
    def hiddenTooltipDialog(self, pane, height='20ex',width='30em',title=None, 
                            close_action=None, dlgId=None, 
                            bottom_left=None,bottom_left_action=None,
                            bottom_right=None,bottom_right_action=None,
                            fired=None, datapath=None, onOpen=None, onEnter=None):
        onOpen = onOpen or ''
        dlgId = dlgId or self.getUuid()
        bcId = '%s_bc' % dlgId
        btnId = '%s_btn' % dlgId
        dlg = pane.dropdownbutton('', hidden=True, nodeId=btnId, datapath=datapath)
        dlg=dlg.tooltipdialog(nodeId=dlgId, connect_onOpen='genro.wdgById("%s").resize();%s' % (bcId, onOpen),
                              connect_onClose=close_action)
        pane.dataController("""genro.wdgById(btnId)._openDropDown(genro._firingNode.getDomNode());""", 
                                btnId=btnId, fired=fired) 
        container=dlg.borderContainer(height=height,width=width,nodeId=bcId, onEnter=onEnter)
        top = container.contentPane(region='top',_class='tt_dialog_top',height='18px')
        if close_action:
            top.div(_class='icnTabClose',float='right',margin='2px',connect_onclick=close_action)
        top.div(title)        
        bottom = container.contentPane(region='bottom',_class='tt_dialog_bottom')
        if bottom_left:
            bottom.button(bottom_left,float='left',baseClass='tt_bottom_btn',
                       connect_onclick=bottom_left_action)
        if bottom_right:
            bottom.button(bottom_right,float='right',baseClass='tt_bottom_btn',
                       connect_onclick=bottom_right_action)
        center=container.borderContainer(region='center',_class='tt_dialog_cnt')
        return center
        
    def confirm(self, pane, dlgId=None, title='!!Confirm',msg='!!Are you sure ?',
                    width='30em', height='20ex', fired=None, 
                    btn_ok='!!Confirm', action_ok=None, btn_cancel='!!Cancel', action_cancel=None, **kwargs):
        dlgId = dlgId or self.getUuid()
        
        pane.dataController('genro.wdgById(dlgId).show()', dlgId=dlgId, fired=fired)
        dlg = pane.dialog(title=title, nodeId=dlgId).borderContainer(width=width, height=height)
        bottom = dlg.contentPane(region='bottom', height='27px', font_size='.9em', background_color='silver',
                                    connect_onclick="""if($1.target != this.widget.domNode){genro.wdgById('%s').hide()}""" % dlgId)
        center = dlg.contentPane(region='center')
        center.div(msg, _class='dlg_msgbox')
        bottom.button(btn_ok, action=action_ok, float='right')
        bottom.button(btn_cancel, action=action_cancel, float='right')
        for btn, action in [(kwargs[k], kwargs.get('action_%s' % k[4:])) for k in kwargs.keys() if k.startswith('btn_')]:
            bottom.button(btn, action=action, float='left')
        

    def thermoDialog(self, pane, thermoid='thermo', title='', thermolines=1, fired=None, alertResult=False):
        dlgid = 'dlg_%s' % thermoid
        d = pane.dialog(nodeId=dlgid, title=title, width='27em', datapath='_thermo.%s.result' % thermoid, 
                        closable='ask', close_msg='!!Stop the batch execution ?', close_confirm='Stop', close_cancel='Continue', 
                        close_action='FIRE ^_thermo.%s.flag = "stop"' % thermoid,
                        connect_show='this.intervalRef = setInterval(function(){genro.fireEvent("_thermo.%s.flag")}, 500)' % thermoid,
                        connect_hide='clearInterval(this.intervalRef);')
                        #onAskCancel
        for x in range(thermolines):
            tl = d.div(datapath='.t%i' % (x+1, ))
            tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum', 
                          places='^.places', progress='^.progress', margin_left='auto', margin_right='auto')
            tl.div('^.message', height='1em', text_align='center')
        d.div(width='100%', height='4em').div(margin='auto').button('Stop', 
                action='genro.wdgById("%s").onAskCancel();' % dlgid)
        
        pane.dataController('genro.wdgById(dlgid).show()', dlgid=dlgid, fired=fired)
        
        pane.dataController('genro.wdgById(dlgid).hide();', dlgid=dlgid, 
                            status='^_thermo.%s.result.status' % thermoid, _if='(status=="stopped" || status=="end")')
        if alertResult:
            pane.dataFormula('gnr.alert', 'msg', msg='=_thermo.%s.result.message' % thermoid, 
                            status='^_thermo.%s.result.status' % thermoid, _if='(status=="stopped" || status=="end")')
        
        pane.dataRpc('_thermo.%s.result' % thermoid, 'app.getThermo', thermoid=thermoid,
                                                             flag='^_thermo.%s.flag' % thermoid)
                                                             
    def _pbl_datesHints(self):
        today = datetime.date.today()
        dates = []
        dates.append(str(today.year))
        dates.append(str(today.year - 1))
        
        for k,v in DATEKEYWORDS[self.locale[:2]].items():
            if k != 'to':
                if isinstance(v,tuple):
                    v = v[0]
                dates.append(v)
        dates = ','.join(dates)
        return dates
        
    def periodCombo(self, fb, period_store = None):
        if not period_store:
            period_store = '.period'
            string_store = 'vars.period_string'
        else:
            string_store = '%s.period_string' % period_store
        fb.dataRpc(period_store, 'decodeDatePeriod', datestr='^.period_input', 
                    _if='datestr', _else='SET .period=null;', _fired='^gnr.onStart')
        fb.dataScript(string_store,
                         """if(ff && tt){
                            return 'da '+ asText(ff, {format:'full'}) +' a '+ asText(tt, {format:'full'});
                         } else {
                            return '';
                         }  """,
                          ff='^%s.from' % period_store, tt='^%s.to'% period_store)
        fb.combobox(lbl='!!Period',value='^.period_input', width='16em',
                    values=self._pbl_datesHints(), margin_right='5px',padding_top='1px')
                    
                    
class ThermoDialog(object):
    def thermoNewDialog(self, pane, thermoid='thermo', title='', thermolines=1, fired=None, pollingFreq=1):
        dlgid = 'dlg_%s' % thermoid
        d = pane.dialog(nodeId=dlgid, title=title, width='27em', datapath='_thermo.%s' % thermoid, 
                        closable='ask', close_msg='!!Stop the batch execution ?', close_confirm='Stop', close_cancel='Continue', 
                        close_action='genro.setInServer("thermo.%s.stop", true);' % thermoid)
        for x in range(thermolines):
            tl = d.div(datapath='.t.t%i' % (x, ))
            tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum', 
                          places='^.places', progress='^.progress', margin_left='auto', margin_right='auto')
            tl.div('^.message', height='1em', text_align='center')
        d.div(width='100%', height='4em').div(margin='auto').button('Stop', 
                                                    action='genro.wdgById("%s").onAskCancel();' % dlgid)
        
        pane.dataController('genro.wdgById(dlgid).show();genro.rpc.managePolling(%s);' % pollingFreq, dlgid=dlgid, fired=fired)
        pane.dataController('genro.wdgById(dlgid).hide();genro.rpc.managePolling();', dlgid=dlgid, _fired='^_thermo.%s.c.end' % thermoid)
        
        
    def setNewThermo(self, thermoid, level, progress, maximum, message='', indeterminate=False, lazy=True):
        #lazy: send to client at most 1 value change per second. 
        #Subsequent calls to setNewThermo in the next second are ignored
        end = (level==-1 or (level==0 and progress >= maximum))
        if end:
            self.setInClientData('_thermo.%s.c.end' % thermoid, True, fired=True, save=True)
            if self.session.pagedata['thermo.%s.stop' % thermoid]:
                self.session.modifyPageData('thermo.%s.stop' % thermoid, None)
            return
            
        now = time.time()
        
        if not hasattr(self, 'lastThermoUpdTime'):
            self.lastThermoUpdLevel = None
            self.lastThermoUpdTime = 0
                        
        if lazy and level == self.lastThermoUpdLevel and now - self.lastThermoUpdTime < 1:
            return
        self.lastThermoUpdTime = now
        self.lastThermoUpdLevel = level
        
            
        tbag = Bag(dict(progress=progress, maximum=maximum, message=message, indeterminate=indeterminate))
        self.setInClientData('_thermo.%s.t.t%s' % (thermoid, level), tbag, save=True)
        
        if self.session.pagedata['thermo.%s.stop' % thermoid]:
            return True
        else:
            return False
            
class UserObject(object):
    def saveUserObjectDialog(self, pane, datapath, objtype, objectdesc):
        pane.div(_class='icnBaseSave buttonIcon',connect_onclick='FIRE aux.save.%s' %objtype)
        dlgBC = self.hiddenTooltipDialog(pane, dlgId='%s_saveDlg' %objtype, title='!!Save %s' %objectdesc,
                                         width='30em',height='20ex',fired='^aux.save.%s' % objtype, 
                                         datapath=datapath,
                                         bottom_left='!!Close',bottom_left_action='FIRE .close_save;',
                                         bottom_right='!!Save',bottom_right_action='FIRE .close_save; FIRE .save;')
                                         
        dlgpane = dlgBC.contentPane(region='center',_class='pbl_dialog_center')
        fb = dlgpane.formbuilder(cols=2, border_spacing='4px')
        dlgpane.dataController("genro.wdgById('%s_saveDlg').onCancel();" %objtype, _fired="^.close_save")
                                         
        fb.textBox(lbl='!!Code' ,value='^.resource?code', width='10em',colspan=2)
        fb.simpleTextarea(lbl='!!Description' ,value='^.resource?description',
                          width='20em',lbl_vertical_align='top',rowspan=2,colspan=2)
        fb.textBox(lbl='!!Permissions' ,value='^.resource?auth_tags', width='10em')        
        fb.checkbox(lbl='!!Private' ,value='^.resource?private')
        dlgpane.dataRpc('.saveResult', 'save_%s' % objtype, userobject='=.resource',
                       _fired='^.save', _POST=True, _onResult='FIRE .saved = true')
        
    def loadUserObjectDialog(self, pane, datapath, objtype, objectdesc):
        pane.div(_class='icnBaseFolder buttonIcon',connect_onclick='FIRE aux.load.%s' %objtype)
        dlgId = '%s_loadDlg' % objtype
        dlgBC = self.hiddenTooltipDialog(pane, dlgId = dlgId, title='!!Load %s' %objectdesc,
                                         width='30em',height='30ex',fired='^aux.load.%s'  %objtype, 
                                         datapath=datapath,
                                         bottom_left='!!Close',bottom_left_action='FIRE .close_load;',
                                         bottom_right='!!Load',bottom_right_action='FIRE .close_load; FIRE .load;')
        

        dlg = dlgBC.borderContainer(region='center',_class='pbl_dialog_center')
        dlg.dataController("genro.wdgById(dlgId).onCancel();", dlgId=dlgId, _fired='^.close_load')
        dlg.dataRemote('.savedResources', 'list_%s' % objtype, cacheTime=1)
        
        #self.deleteStatDialog(pane, datapath)
        buttons = dlg.contentPane(region='right', width='30', font_size='0.9em')
        
        treepane = dlg.contentPane(region='center').div(_class='treeContainer')
        treepane.tree(storepath='.savedResources', persist=False, inspect='shift',
                       labelAttribute='caption', connect_ondblclick='FIRE .close_load; FIRE .load;',
                       selected_code='.selectedCode',
                       selected_pkey='.selectedId', _class='queryTree', 
                       _fsaved='^.saved', _fdeleted='^.deleted')
        
        buttons.div(connect_onclick='genro.wdgById("%s").onCancel();FIRE .new;' % dlgId, _class='icnBaseAdd buttonIcon', float='left')
        buttons.div(connect_onclick='FIRE .delete',_class='icnBaseTrash buttonIcon', float='left')
        delDlgId='%s_del_dlg' % objtype
        deleteBC = self.hiddenTooltipDialog(dlg, dlgId=delDlgId, title="!!Confirm deletion",
                                 width="18em",height="16ex",fired='^.delete', close_action='FIRE .close_del',
                                 bottom_left='!!Yes', bottom_left_action='FIRE .delete_ok;FIRE .close_del;',
                                 bottom_right='!!No', bottom_right_action='FIRE .close_del')
        msg = deleteBC.contentPane(region='center')
        msg.div("!!The selected object will be permanently deleted:")
        msg.div("^.selectedCode", font_weight='bold')
        dlg.dataController("genro.wdgById(dialogId).onCancel();", dialogId=delDlgId, _fired='^.close_del')
        
        dlg.dataRpc('.resource', 'load_%s' % objtype, id='=.selectedId',
                    _onCalling='FIRE .loading', _onResult='FIRE .loaded', _fired='^.load')      
        dlg.dataRpc('.resource', 'new_%s' % objtype, 
                    _onCalling='FIRE .loading', _onResult='FIRE .loaded', _fired='^.new', _onstart='^gnr.onStart')
        dlg.dataRpc('dummy', 'delete_%s' % objtype, id='=.selectedId',
                    _onResult='FIRE .deleted', _fired='^.delete_ok')
                    
class StandardIndex(object):
    #to change
    def main(self, root, **kwargs):
        self._pageMenues = []
        self.pageMenues()
        height='%iex' % ((int((len(self._pageMenues)+1)/2) * 6) + 8, )
        client, top, bottom=self.pbl_rootContentPane(root, self.indexTitle(), width='40em', height=height, centered=True)          
        fb = client.formbuilder(cols=2, border_spacing='10px', margin='auto')
        for name,url in self._pageMenues:
            self.pbl_linkButton(fb, name, url)
    def indexTitle(self):
        return self.windowTitle()

class IncludedView(BaseComponent):
    css_requires = 'public'
    js_requires = 'public'
    """IncludedView allows you to manage data of the table
       in relation many to many. includedViewBox is the method that return some
       custom widgets those allow all these operations"""
       
    def includedViewBox(self, parentBC, nodeId=None,table=None,datapath=None,
                        storepath=None,selectionPars=None,formPars=None,label=None,
                        add_action=None, add_class='buttonIcon icnBaseAdd',add_enable='^form.canWrite',
                        del_action=None, del_class='buttonIcon icnBaseDelete', del_enable='^form.canWrite',
                        close_action=None, close_class='buttonIcon icnTabClose', 
                        print_action=None, print_class='buttonIcon icnBasePrinter', 
                        export_action=None, export_class='buttonIcon icnBaseExport', 
                        tools_action=None, tools_class='buttonIcon icnBaseAction', 
                        tools_menu=None,upd_action=False,
                        filterOn=None,  pickerPars=None,centerPaneCb=None,
                        editorEnabled=None,reloader=None,externalChanges=None,**kwargs):
        """
        This method returns a grid (includedView) for, viewing and selecting
        rows from a many to many table related to the main table,
        and the widget that hosts the editing the data. You can edit the data 
        of a single row (record) using a form(formPars), or pick some rows from another table
        with the picker widget(pickerPars).
        The form can be contained inside a dialog or a contentPane and is useful
        for editing a single record. If the data is stored inside another table 
        you should use the picker to select the rows from that table.
        
        @param parentBC: MANDATORY this is a border container you have to pass
                         to includedViewBox for containing the the includedView
                         and its label.
        @param table:
        @param storepath:
        @param selectionPars:
        @param datapath:
        @param formPars:(dict) contains all the param of the widget that host the form:
                        these can be:
                        - mode: "dialog"/"pane", the default is "dialog"
                        - height = height of the dialog
                        - width = width of the dialog
                        - formCb = MANDATORY callback method for creating form.
                                   this method receive as param: 
                                             - formBorderCont: a borderContainer widget as root for construction
                                             - datapath the right datapath for the data inside the form.
                                             - region: 'center' of the pane/borderContainer you place into 
                        - toolbarHandler = OPTIONAL a callback for the form toolbar
                        - title: MANDATORY for mode dialog
                        - pane: OPTIONAL pane of the input form
                        - parentDialog: OPTIONAL. if mode dialog, this is another 
-                          dialog that must be closed in order to avoid bugs
        @param label: (string) adding this kwparam you put a label to the includedView
        
        @param add_action: (boolean) adding this kwparam you allow the inserting 
                           of a row inside the includedView
        @param add_class: css class of add button
        @param add_enable: a path to enable/disable add action 
        @param del_action: (boolean) adding this kwparam you allow the deleting 
                           of a row inside the includedView
        @param del_class: css class of delete button
        @param del_enable: a path to enable/disable del action 
        @param close_action: (boolean) adding closing button on tooltipDialog
        @param close_class: css class of close button adding closing button on tooltipDialog
        @param filterOn: (boolean only for picker) adding this kwparam you allow the filtering
                         inside the pickers grid.
        @param pickerPars:(dict) contains all the param of the tooltip dialog
                           which host the picker grid. 
                           these can be: 
                            - height : eight of the tooltipdialog
                            - width : width of the tooltipdialog
                            - label :of the tooltipdialog
                            - table : MANDATORY the table of the picker grid. From
                                     these table you can pick the row for the many to many table you handle.
                            - columns: MANDATORY columsn of the picker grid
                            - nodeId: MANDATORY id for the picker.
                            - storepath,autowidth etc grid params
                            - filterOn: the columns on you can apply the filter
        @param fromPicker_target_fields: for bind the picker's table
                          columns to the includedView columns of the many to many table.
        @param fromPicker_nodup_field: if this column value is present in the includedView
                                       replace that row instead of adding a duplicate row
        @params kwargs: you have to put the includedView params: autoWidth, storepath etc
        """
        viewPars = dict(kwargs)
        gridId = nodeId or self.getUuid()
        viewPars['nodeId'] = gridId        
        controllerPath = datapath or 'grids.%s' %gridId
        storepath = storepath or '%s.selection' %controllerPath
        viewPars['storepath'] = storepath
        viewPars['controllerPath']= controllerPath
        controller = parentBC.dataController(datapath=controllerPath)
        assert not 'selectedIndex' in viewPars
        viewPars['selectedIndex'] = '^%s.selectedIndex' % controllerPath
        assert not 'selectedLabel' in viewPars
        if not viewPars.get('selectedId'):
            viewPars['selectedId'] = '^%s.selectedId' % controllerPath
        viewPars['selectedLabel'] = '^%s.selectedLabel' % controllerPath
        label_pars = dict([(k[6:], kwargs.pop(k)) for k in kwargs.keys() if k.startswith('label_')])
        label_pars['_class'] = label_pars.pop('class', None) or 'pbl_viewBoxLabel'
        box_pars = dict([(k[4:], kwargs.pop(k)) for k in kwargs.keys() if k.startswith('box_')])
        box_pars['_class'] = (box_pars.pop('class', None) or 'pbl_viewBox')
        gridtop = parentBC.contentPane(region='top', **label_pars)
        if close_action:
            if close_action is True:
                close_action = 'FIRE %s.closeSelection;' % controllerPath
            gridtop.div(float='left', _class=close_class, connect_onclick=close_action)
        if print_action:
            if print_action is True:
                print_action = 'FIRE %s.print;' % controllerPath
            gridtop.div(float='left', _class=print_class, connect_onclick=print_action)
        if export_action:
            if export_action is True:
                #export_action = 'FIRE %s.export' % controllerPath
                export_action = 'FIRE %s.export="xls";' % controllerPath # TEST todo: different buttons ?
            gridtop.div(float='left', _class=export_class, connect_onclick=export_action)
        if tools_menu:
            btn = gridtop.div(float='left', _class = tools_class,margin_right='5px')
            btn.menu(storepath=tools_menu, modifiers='*')
        elif tools_action:
            if tools_action is True:
                tools_action = 'FIRE %s.reload' % controllerPath            
            gridtop.div(float='left', _class=tools_class, connect_onclick=tools_action)
        if del_action:
            if del_action is True:
                del_action = 'FIRE %s.delSelection' % controllerPath
            gridtop.div(float='right', _class=del_class, connect_onclick=del_action,
                        margin_right='2px',visible=del_enable)
        if add_action:
            if add_action is True:
                if pickerPars:
                    add_action='FIRE %s.showPicker' % controllerPath
                elif formPars:
                    add_action = 'FIRE %s.showRecord; FIRE %s.addRecord =$1;' % (controllerPath, controllerPath) #invertiti showrecord e addrecord
                else:
                    add_action = 'FIRE %s.addRecord =$1;FIRE %s.editRow;' % (controllerPath, controllerPath)     
            gridtop.div(float='right', _class=add_class,connect_onclick=add_action,
                        margin_right='2px',visible=add_enable)
                        
        if upd_action:
            if upd_action is True:
                upd_action = 'FIRE %s.showRecord' %controllerPath
            gridtop.div(float='right', _class='icnBaseEdit buttonIcon', connect_onclick=upd_action,
                        margin_right='2px',visible=add_enable)            
        self._iv_IncludedViewController(controller, gridId,controllerPath)
        
        if filterOn:
            self._iv_gridFilter(gridId, gridtop, controller, controllerPath, filterOn, kwargs)        
        if callable(label):
            label(gridtop)
        else:
            gridtop.div(label,margin_top='2px',float='left')
        if centerPaneCb:
            gridcenter = getattr(self,centerPaneCb)(parentBC, region='center', **box_pars)
        else:
            gridcenter = parentBC.contentPane(region='center', **box_pars)
        if not 'columns' in viewPars:
            struct =  viewPars.get('struct',None)
            if struct and callable(struct) and not isinstance(struct,Bag):
                viewPars['struct'] = struct(self.newGridStruct(table))
        view = gridcenter.includedView(extension='includedViewPicker',table=table,
                                       editorEnabled=editorEnabled or '^form.canWrite',
                                       reloader=reloader,**viewPars)
        if externalChanges:
            externalChangesTypes=''
            if isinstance(externalChanges,basestring):
                if ':' in externalChanges:
                    externalChanges,externalChangesTypes=externalChanges.split(':')
                    if externalChanges=='*':
                        externalChanges=True
            subscribed_tables = [t for t in self.pageOptions.get('subscribed_tables','').split(',') if t]
            if not table in subscribed_tables:
                subscribed_tables.append(table)
                self.pageOptions['subscribed_tables'] = ','.join(subscribed_tables)
            event_path = 'gnr.dbevent.%s' %table.replace('.','_')
            pars = dict()
            conditions = list()
            if isinstance(externalChanges,basestring):
                for fld in externalChanges.split(','):
                    fldname,fldpath=fld.split('=')
                    conditions.append('curr_%s==event_%s' %(fldname,fldname))
                    pars['event_%s' %fldname] = '=%s.%s' %(event_path,fldname)
                    pars['curr_%s' %fldname] = '=%s' %fldpath  
            if externalChangesTypes:
                conditions.append('evtypes.indexOf(evtype)')
                pars['evtypes'] = externalChangesTypes
                pars['evtype'] = '=%s?dbevent' %event_path
            print ' && '.join(conditions),
            print str(pars)
            parentBC.dataController("FIRE %s.reload" %controllerPath,_if=' && '.join(conditions),
                                     _fired='^%s' %event_path,**pars)
            
        if selectionPars:
            self._iv_includedViewSelection(gridcenter,gridId,table,storepath,selectionPars,controllerPath)
            
        if formPars:
            formPars.setdefault('pane', gridcenter)
            self._includedViewForm(controller, controllerPath, view, formPars)
        if pickerPars:
            pickerPars.setdefault('pane', gridcenter)
            self._iv_Picker(controller, controllerPath, view, pickerPars)
        return view
        
    def _iv_includedViewSelection(self,pane,gridId,table,storepath,selectionPars,controllerPath):
        assert table
        assert not 'columnsFromView' in selectionPars
        assert not 'nodeId' in selectionPars
        assert 'where' in selectionPars
        
        selectionPars['nodeId'] = "%s_selection" %gridId
        selectionPars['columns'] = selectionPars.get('columns') or '=%s.columns' %controllerPath
        print selectionPars['columns']
        pane.dataSelection(storepath,table,**selectionPars)
        
    def _iv_IncludedViewController(self, controller, gridId ,controllerPath):
        controller.dataController("""var grid = genro.wdgById(gridId);
                                     grid.addBagRow('#id', '*', grid.newBagRow(),event);
                                     """ , 
                                     event='^.addRecord',
                                     gridId=gridId)
        delScript = """PUT .selectedLabel= null;
                       var grid = genro.wdgById(gridId);
                       var nodesToDel = grid.delBagRow('*', delSelection);
                       FIRE %s.%s""" % (controllerPath,'onDeletedRow')
        controller.dataController(delScript, _fired='^.delRecord', delSelection='^.delSelection',
                                idx='=.selectedIndex', gridId=gridId)
        controller.dataController("""genro.wdgById(gridId).editBagRow();
                                     """,fired='^.editRow',gridId=gridId)
        controller.dataController("genro.wdgById(gridId).printData();" ,fired='^.print',gridId=gridId)
        controller.dataController("genro.wdgById(gridId).exportData(mode);" ,mode='^.export',gridId=gridId)
        controller.dataController("genro.wdgById(gridId).reload(true);" ,_fired='^.reload',gridId=gridId)
        controller.dataController("""SET .selectedIndex = null;
                                     PUT .selectedLabel= null;""",
                                  _fired="^gnr.forms.formPane.saving") 
        
    def _iv_gridFilter(self, gridId, gridtop, controller, controllerPath, filterOn, kwargs):
        colsMenu = Bag()
        fltList = splitAndStrip(filterOn, ',')
        for col in fltList:
            caption = None
            if ':' in col:
                caption, col = col.split(':')
            if not caption: # ask the caption to the table: table has to be specified in kwargs and the col has to be a single real db column (not list of columns)
                caption = self.db.table(kwargs['table']).column(col).name_long
            colList = splitAndStrip(col, '+')
            col = '+'.join([self.db.colToAs(c) for c in colList])
            colsMenu.child('r', col=col, caption=caption,childcontent='')
            
        controller.data('.flt.selected.col', colsMenu['#0?col'])
        controller.data('.flt.selected.caption', colsMenu['#0?caption'])
        
        gridtop.input(float='right', _class='searchInput searchWidth', margin_right='5px', font_size='.9em',
            connect_onkeyup='genro.wdgById("%s").applyFilter($1.target.value);' % gridId)
            
        search = gridtop.div(float='right', datapath=controllerPath, margin_right='4px')
        search.span('!!Search ')
        controller.dataController("""var grid = genro.wdgById(gridId);
                                        grid.filterColumn = col;
                                        grid.applyFilter(true);""", 
                                        col='^.flt.selected.col', 
                                        gridId=gridId, _onStart=True)
        if len(colsMenu) > 1:
            controller.data('.flt.colsMenu', colsMenu)
            search.span(value='^.flt.selected.caption')
            search.menu(modifiers='*', _class='smallmenu', storepath='.flt.colsMenu',
                        selected_col='.flt.selected.col',
                        selected_caption='.flt.selected.caption')
                
    def _includedViewForm(self, controller, controllerPath, view, formPars):
        viewPars = view.attributes
        gridId = viewPars['nodeId']
        storepath = viewPars['storepath']
        assert not 'connect_onCellDblClick' in viewPars
        viewPars['connect_onCellDblClick'] = """var grid = this.widget;
                                                var cell = grid.getCell($1.cellIndex);
                                                if (!genro.nodeById(grid.editorId + '_' + cell.field)){
                                                    FIRE %s.showRecord = true;
                                                }
                                                """ % controllerPath
                
        formHandler = getattr(self, '_iv_Form_%s' % formPars.get('mode', 'dialog'))
        
        toolbarPars = dict([(k, formPars.pop(k, None)) for k in ('add_action', 'add_class', 'add_enable','del_action', 'del_class','del_enable',)])
        toolbarPars['controllerHandler'] = formPars.pop('controllerHandler', '_iv_FormStaticController')
        formHandler(formPars, storepath, controller, controllerPath, gridId, toolbarPars)
    
    def _iv_Form_inline(self, formPars, storepath, controller, controllerPath, gridId, toolbarPars):
        getattr(self,toolbarPars['controllerHandler'])(controller, gridId)
        
    def _iv_FormToolbar(self, parentBC, controller, controllerPath, controllerHandler, gridId, 
                        add_action=None, add_class=None,add_enable=None,
                        del_action=None, del_class=None,del_enable=None,):
                                    
        pane = parentBC.contentPane(region='top', height='28px', datapath=controllerPath,overflow='hidden')
        getattr(self, controllerHandler)(controller, gridId)
        tb = pane.toolbar()
        if del_action:
            if del_action is True:
                del_action = 'FIRE %s.delRecord=true' % controllerPath
            del_class = del_class or 'buttonIcon icnBaseDelete'
            del_enable = del_enable or '^form.canWrite'
            tb.button('!!Delete', float='right',action=del_action, iconClass=del_class, 
                                showLabel=False,visible=del_enable)
        if add_action:
            if add_action is True:
                add_action = 'FIRE %s.addRecord=true' % controllerPath
            add_class = add_class or 'buttonIcon icnBaseAdd'
            add_enable = add_enable or '^form.canWrite'
            tb.button('!!Add', float='right',action=add_action,visible=add_enable,
                            iconClass=add_class, showLabel=False)
        
        
        tb.button('!!First', fire_first='.navbutton', iconClass="tb_button icnNavFirst", disabled='^.atBegin', showLabel=False)
        tb.button('!!Previous', fire_prev='.navbutton', iconClass="tb_button icnNavPrev", disabled='^.atBegin', showLabel=False)
        tb.button('!!Next', fire_next='.navbutton', iconClass="tb_button icnNavNext", disabled='^.atEnd', showLabel=False)
        tb.button('!!Last', fire_last='.navbutton', iconClass="tb_button icnNavLast", disabled='^.atEnd', showLabel=False)
        
        controller.dataFormula('.atBegin','(idx==0)',idx='^.selectedIndex')
        controller.dataFormula('.atEnd','(idx==genro.wdgById(gridId).rowCount-1)',idx='^.selectedIndex',gridId=gridId)

    def _iv_FormStaticController(self, controller, gridId):
        #controller.dataController("""var recordpath,selId;
        #                             var node=(idx!=null)? genro.wdgById(gridId).dataNodeByIndex(idx) : null
        #                           if(node){
        #                                recordpath = '.'+node.label;
        #                                selId = node.attr._pkey;
        #                            }
        #                            else{
        #                                recordpath = 'vars.'+gridId+'.unselected'
        #                                selId = null
        #                            }
        #                        
        #                            //SET .recordpath = recordpath;
        #                            console.log(selId);
        #                            //SET .selectedId = selId;
        #                            console.log('settato selectedId - 773');""", 
        #                            idx='^.selectedIndex',
        #                            gridId=gridId)
        #                                                                    
        controller.dataController("""var newidx;
                                 var rowcount = genro.wdgById(gridId).rowCount;
                                 if (btn == 'first'){newidx = 0;} 
                                 else if (btn == 'last'){newidx = rowcount-1;}
                                 else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                                 else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                                 SET .selectedIndex = newidx;
                              """, btn='^.navbutton',idx='=.selectedIndex', gridId=gridId)
                              
    def _includedViewFormBody(self, recordBC, controller, controllerPath, formPars):
        bottom_left = formPars.pop('bottom_left',None)
        bottom_right = formPars.pop('bottom_right','!!Close')
        bottom_left_action = formPars.pop('bottom_left_action',None)
        bottom_right_action = formPars.pop('bottom_right_action','FIRE %s.close' %controllerPath)
        disabled=formPars.pop('disabled','^form.locked')
        if formPars.get('mode', 'dialog') == 'dialog':
            bottom = recordBC.contentPane(region='bottom',_class='dialog_bottom')
            if bottom_left:
                bottom.button(bottom_left,float='left',baseClass='bottom_btn',
                           connect_onclick=bottom_left_action)
            if bottom_right:
                bottom.button(bottom_right,float='right',baseClass='bottom_btn',
                           connect_onclick=bottom_right_action)
        st = recordBC.stackContainer(region='center',selected='^%s.dlgpage' % controllerPath)
        st.dataController("if(idx!=null){SET .dlgpage=0;}else{SET .dlgpage=1;}", 
                                            idx='^.selectedIndex', datapath=controllerPath, _fired='^gnr.onStart')
        _classBC = formPars.pop('_classBC','pbl_dialog_center') #aggiunto da fporcari
        formBorderCont = st.borderContainer(datapath='^%s.selectedLabel?=if(#v){"."+#v}else{"emptypath"}' % controllerPath, _class=_classBC) #aggiunto il _classBC da fporcari
        emptypane = st.contentPane()
        emptypane.div("No record selected",_class='dlg_msgbox')
        formPars['formCb'](formBorderCont,region='center',disabled=disabled)

    def _iv_Picker(self, controller, controllerPath, view, pickerPars):
        pickerId = pickerPars.setdefault('nodeId', self.getUuid())
        gridId = view.attributes['nodeId']
        nodup_field = view.attributes.get('fromPicker_nodup_field')
        dialogId = '%s_picker' % gridId
        height = pickerPars.pop('height', '40ex')
        width = pickerPars.pop('width', '40em')
        mainPane = pickerPars.pop('pane')
        title = pickerPars.pop('label', None)
        onOpen = pickerPars.pop('onOpen', None)
        if nodup_field:
            onOpen = onOpen or ''
            onOpen = 'genro.wdgById("'+pickerId+'").applyFilter();%s' % onOpen
        dlgBC = self.hiddenTooltipDialog(mainPane, dlgId=dialogId, title=title,
                                         width=width,height=height,fired='^%s.showPicker' % controllerPath, 
                                         datapath=controllerPath,close_action="FIRE .close" ,
                                         bottom_left='!!Add',bottom_left_action='FIRE .pickerAdd;',
                                         bottom_right='!!Add and Close',bottom_right_action='FIRE .close;FIRE_AFTER .pickerAdd;',
                                         onOpen=onOpen, onEnter='FIRE .close;FIRE_AFTER .pickerAdd;')
        gridBC = dlgBC.borderContainer(region='center')

        selector_cb = pickerPars.pop('selector_cb', None)
        selector_storepath = pickerPars.pop('selector_storepath', None)
        selector_result = pickerPars.pop('selector_result', None)
        if selector_cb or selector_storepath:
            if selector_storepath:
                top = dlgBC.contentPane(region='top', height='26px').toolbar()
                top.filteringSelect(value=selector_result, storepath=selector_storepath)
            else:
                selector_cb(dlgBC)
                
        if nodup_field:
            pickerPars['excludeListCb'] = 'return genro.wdgById("'+gridId+'").getColumnValues("'+nodup_field+'")'
            target_fields = view.attributes.get('fromPicker_target_fields').split(',')
            for fld in target_fields:
                tfld,pfld = fld.split('=')
                if tfld.strip() == nodup_field:
                    pickerPars['excludeCol'] = pfld.strip()
                    break
        
        self.includedViewBox(gridBC, **pickerPars)        
        controller.dataController("genro.wdgById(dialogId).onCancel();", dialogId=dialogId, _fired='^.close')
        controller.dataController("""var nodelist = genro.wdgById(pickerId).getSelectedNodes();
                                    genro.nodeById(gridId).includedViewPicker.fromPicker(nodelist);
                                    """, 
                                    pickerId=pickerId,
                                    gridId=gridId, _fired='^.pickerAdd')


    def _iv_Form_dialog(self, formPars, storepath, controller, controllerPath, gridId, toolbarPars):
        dialogId = '%s_dialog' % gridId
        height = formPars.pop('height', '40ex')
        width = formPars.pop('width', '40em')
        mainPane = formPars.pop('pane')
        if 'onOpen' in formPars:
            formPars['connect_show'] = '%s' %formPars.pop('onOpen')
        controller.dataController("genro.wdgById('%s').show();" %dialogId, _fired='^.showRecord')
        controller.dataController("genro.wdgById('%s').onCancel()" %dialogId ,_fired='^.close')
                                    
        toolbarHandler = formPars.pop('toolbarHandler', '_iv_FormToolbar')
        
        recordBC = mainPane.dialog(nodeId=dialogId,**formPars).borderContainer(nodeId='%s_bc' %gridId,datapath=storepath, 
                                                                               height=height, width=width)
        
        getattr(self, toolbarHandler)(recordBC, controller, controllerPath=controllerPath,
                                                gridId=gridId, **toolbarPars)
        self._includedViewFormBody(recordBC, controller, controllerPath, formPars)
        
    def _iv_Form_pane(self, formPars, storepath, controller, controllerPath, gridId, toolbarPars):
        mainPane = formPars.pop('pane')
        toolbarHandler = formPars.pop('toolbarHandler', '_iv_FormToolbar')
        recordBC = mainPane.borderContainer(datapath=storepath, **formPars)
        getattr(self, toolbarHandler)(recordBC, controller, controllerPath=controllerPath,
                                                gridId=gridId, **toolbarPars)
        self._includedViewFormBody(recordBC, controller, controllerPath, formPars)
        
class RecordHandler(object):
    """
    RecordHandler allows to Load and Save a record without passing through the mainrecord path
    it executes saving and loading in an independent way from the mainrecord of a standard table. 
    """
    def recordDialog(self,table,firedPkey=None,height=None,width=None,_class=None,
                    title=None,formCb=None,onSaved='',saveKwargs={},loadKwargs={},
                    savePath='',parentDialog=None,bottomCb=None,savingMethod=None,
                    loadingMethod=None, onClosed='',validation_failed='alert',custom_table_id=None):
        """
        Allow to manage a form into a dialog for editing and saving a single RecordHandler.
        * `table`: The table where the record is saved.
        * `firedPkey`: a pointer where the pkey of the record is. (eg: firedPkey = '^aux.selectedPkey')
        * `height`,`width`,`_class`,`title`: Form parameters. Dimension, 
                                             title and cssclass of the dialog and its content.
        * `formCb`: a method to define for creating the editing form inside the dialog.
        * `onSaved`: a string with JS evaluated after the saving.
        * `saveKwargs`: optional kwargs for the rpc saving method.
        * `loadKwargs`: optional kwargs for the rpc loading method.
        * `validation_failed`: can be "alert" or "focus"
        """
        assert not '_onResult' in saveKwargs
        assert not '_onResult' in loadKwargs
        tableId = custom_table_id or table.replace('.','_')
        sqlContextName='sqlcontext_%s' %tableId
        controllerPath = 'aux_forms.%s' % tableId
        sqlContextRoot= 'aux_forms.%s.record' % tableId
        page = self.pageSource()
        dlg = page.dialog(nodeId='dlg_%s' % tableId,title=title,
                          parentDialog=parentDialog)
        dlgBC = dlg.borderContainer(datapath=controllerPath, height=height, 
                                    width=width, _class=_class,
                                    sqlContextName=sqlContextName,
                                    sqlContextRoot=sqlContextRoot, 
                                    sqlContextTable= table)
        self._recordDialogController(dlgBC,table,tableId,saveKwargs,
                                    loadKwargs,controllerPath,firedPkey,sqlContextName,
                                    onSaved,onClosed, savePath,savingMethod,loadingMethod,
                                    validation_failed)
        self._recordDialogLayout(dlgBC,tableId,formCb,controllerPath,table,bottomCb)

    def _recordDialogController(self,pane,table,tableId,saveKwargs,
                                loadKwargs,controllerPath,firedPkey,sqlContextName,
                                onSaved,onClosed,savePath,savingMethod,loadingMethod,
                                validation_failed):
        formId = "%s_form" %tableId
        dlgId = "dlg_%s" %tableId
        onSaved = onSaved or ''
        onSaved = 'FIRE %s.afterSaving; %s' %(controllerPath,onSaved)
        
        pane.dataController("""if(saveAndAdd){
                                    SET .closeDlg = false;
                                    SET .addRecord = true;
                                    FIRE .saveRecord = saveAndAdd;
                                }else if(saveAndClose){
                                    SET .addRecord = false;
                                    SET .closeDlg = true; 
                                    FIRE .saveRecord = saveAndClose;
                                }""",saveAndAdd="^.saveAndAdd",saveAndClose="^.saveAndClose")
                                
        pane.dataController(""" if(closeDlg){
                                    FIRE .exitAction='saved';
                                }else if(addRecord){
                                    FIRE .addNew;
                                }""",
                            _fired="^.afterSaving",addRecord='=.addRecord',
                            closeDlg='=.closeDlg')
        
        pane.dataController("""SET .current_pkey = "*newrecord*";
                               genro.formById("%s").load();"""%formId,
                            _fired="^.addNew")
                            
        pane.dataController("""genro.wdgById("%s").show(); 
                               SET .current_pkey = (!firedPkey||firedPkey==true) ? "*newrecord*" : firedPkey;
                               genro.formById("%s").load();
                            """ %(dlgId,formId),firedPkey=firedPkey)
                            
        pane.dataController("""var dlgNode=genro.nodeById("%s");
                               dlgNode.widget.onCancel();
                               if (onClosed){
                                   funcCreate(onClosed, 'exitAction').call(dlgNode,exitAction);
                               } 
                            """%dlgId, exitAction ='^.exitAction', onClosed=onClosed)
        
        self.formLoader(formId,resultPath= '%s.record'%controllerPath,
                        table=table,pkey='=%s.current_pkey' %controllerPath,
                        method=loadingMethod,loadingParameters='=gnr.tables.%s.loadingParameters' %tableId,
                        sqlContextName=sqlContextName,**loadKwargs)
                       
        self.formSaver(formId,resultPath= savePath or '%s.savingResult' %controllerPath,
                       table=table, _fired='^%s.saveRecord' %controllerPath,
                       method=savingMethod,onSaved=onSaved,**saveKwargs)
                       
        pane.dataController("""if(loading){
                                    SET .stackPane = 0;
                                }else{
                                    SET .stackPane = 1;
                            }""",
                            loading='^gnr.forms.%s.loading' %formId)
        pane.dataController("""if(save_failed == "nochange"){
                                        FIRE .exitAction='nochange';
                                }else if(save_failed == "invalid"){
                                    FIRE .validation_failed;
                                }""",save_failed='^gnr.forms.%s.save_failed' %formId)
                                  
        if validation_failed == "alert":
            pane.dataController("genro.dlg.alert(msg,title)",
                                  _fired='^.validation_failed',
                                  msg='!!Not valid data. Please check the form',
                                  title='!!Warning')
                                  
        elif validation_failed == "focus":
            pane.dataController("genro.formById('%s').focusFirstInvalidField()" %formId,_fired="^.validation_failed")
        
    def _recordDialogLayout(self,bc,tableId,formCb,controllerPath,table,bottomCb):
        dlgId = "dlg_%s" %tableId
        formId = "%s_form" %tableId
        bottom = bc.contentPane(region='bottom',_class='dialog_bottom')
        bottomCb = bottomCb or getattr(self,'_record_dialog_bottom')
        bottomCb(bottom)
        stack = bc.stackContainer(region='center',_class='pbl_background' ,formId=formId,
                                  selected='^%s.stackPane' %controllerPath,datapath='.record')
        loading = stack.contentPane(_class='waiting')
        formCb(stack, disabled='^form.locked', table=table)
        
    def _record_dialog_bottom(self,pane):
        pane.button('!!Cancel',float='left',baseClass='bottom_btn',
                    fire_cancel='.exitAction')
        pane.button('!!Save',float='right',baseClass='bottom_btn',
                    fire=".saveAndClose")
                        
    def rpc_deleteIncludedViewRecord(self, table, rowToDelete,**kwargs):
        tblobj = self.db.table(table)
        recordToDelete = tblobj.record(rowToDelete,for_update=True, mode='bag')
        tblobj.delete(recordToDelete)
        self.db.commit()

class DynamicEditor(object):
    def dynamicEditor(self, container, value,contentPars=None,disabled=None,
                      nodeId=None,editorHeight='',**kwargs):
        nodeId = nodeId or self.getUuid()
        stackId = "%s_stack"%nodeId
        editorId = "%s_editor"%nodeId
        st = container.stackContainer(nodeId=stackId,**contentPars)
        viewPane = st.contentPane(_class='pbl_viewBox')
        viewPane.div(innerHTML=value,_class='formattedBox')
        editPane = st.contentPane(overflow='hidden',connect_resize="""var editor = genro.wdgById('%s');
                                                   var height = this.widget.domNode.clientHeight-30+'px';
                                                   dojo.style(editor.iframe,{height:height});"""%editorId)
        editPane.editor(value=value,nodeId=editorId,**kwargs)
        st.dataController('genro.wdgById("%s").setSelected(disabled?0:1)'%stackId,
                        disabled=disabled,fired='^gnr.onStart')
                        
class RecordToHtmlFrame(BaseComponent):
    def _custom_print_toolbar(self,toolbar):
        pass
        
    def recordToHtmlFrame(self, bc, frameId='', table='',
                          respath=None, pkeyPath='',background_color='white',
                          enableConditionPath='',docNamePath='', customToolbarCb=None,**kwargs):
        
        table = table or self.maintable
        frameId = frameId or self.getUuid()
        controllerPath = 'aux_frames.%s' % frameId
        top=bc.contentPane(region='top', height='32px')
        toolbar = top.toolbar(height='23px',margin_top='2px')
        custom_toolbarCb = customToolbarCb or getattr(self,'_custom_print_toolbar')
        custom_toolbarCb(toolbar)
        toolbar.button('!!PDF',fire='%s.downloadPdf' % controllerPath,iconClass='icnBasePdf',
                        position='absolute',right='10px',top='5px',showLabel=False,)
        toolbar.button('!!Print', fire='%s.print' % controllerPath,showLabel=False,
                       position='absolute',right='40px',top='5px',iconClass='icnBasePrinter')

        #top.checkbox("Don't cache", value='%s.noCache' % controllerPath,)
        
        top.dataController("""
                             var docName = docName || record;
                             var docName=docName.replace('.', '');
                             var downloadAs =docName +'.pdf';
                             var parameters = {'record':record,
                                               'table':'%s',
                                               'downloadAs':downloadAs,
                                               'pdf':true,
                                               'respath':'%s',
                                               'rebuild':rebuild}
                             objectUpdate(parameters,moreargs);
                             genro.rpcDownload("callTableScript",parameters);
                             """ % (table,respath),
                    _fired='^%s.downloadPdf' % controllerPath,
                    record = '=%s' % pkeyPath,
                    docName ='=%s' % docNamePath,
                    moreargs=kwargs,
                    rebuild=True)
                    #rebuild='=%s.noCache' % controllerPath)
        rpc_args={}
        for k,v in kwargs.items():
            rpc_args['rpc_%s'%k]=v
        center = bc.borderContainer(region='center', background_color=background_color)
        if enableConditionPath:
            enableCondition = '^%s' % enableConditionPath
        else:
            enableCondition  = None
        frame = center.iframe(nodeId=frameId,
                              border='0px',
                              height='100%',
                              width='100%',
                              rpcCall='callTableScript',
                              rpc_record = '=%s' % pkeyPath,
                              rpc_table = table,
                              rpc_respath=respath,
                              #rpc_rebuild='=%s.noCache' % controllerPath,
                              rpc_rebuild=True,
                              _print='^%s.print' % controllerPath,
                              _reloader='^%s' % pkeyPath,
                              _if=enableCondition,
                              **rpc_args)
        