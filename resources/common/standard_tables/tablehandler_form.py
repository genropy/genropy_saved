# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 


from gnr.web.gnrbaseclasses import BaseComponent

class TableHandlerForm(BaseComponent):
    def pageForm(self, pane):
        bc = pane.borderContainer(nodeId='formRoot')
        self.formController(bc)
        self.formToolbar(bc.contentPane(region='top', _class='sttbl_list_top'))
        center = bc.borderContainer(datapath='form',formId='formPane',formDatapath='.record',region='center')
        self.formBase(center,datapath='.record',region='center', disabled='^form.locked')


    def setLogicalDeletionCheckBox(self, elem):
        box = elem.div(_class='hidden_record_checkbox')
        box.checkbox(label='!! Hidden',
                     value='^form.logical_deleted',
                     disabled='^form.locked')
        #elem.dataFormula('aux.listpage', '!selectedpage', selectedpage='^selectedPage', _onStart=True)
        elem.dataController("""if(logical_deleted){
                                   genro.dom.addClass("formPane", "logicalDeleted");
                               }else{
                                   genro.dom.removeClass("formPane", "logicalDeleted");
                               }
                               if($2.kw.reason!=true){
                                   if (delete_ts && !logical_deleted){
                                        SET form.record.__del_ts = null;
                                    }else if(logical_deleted && !delete_ts){
                                        SET form.record.__del_ts =new Date();
                                    }
                               }
                               """,
                            logical_deleted='^form.logical_deleted', delete_ts='=form.record.__del_ts')

    def formController(self, pane):
        self.formTitleBase(pane)
        pane.dataFormula('form.locked', 'statusLocked || recordLocked || false', statusLocked='^status.locked',
                         recordLocked='=form.recordLocked', fired='^gnr.forms.formPane.loaded')
        pane.dataController("",_fired="")
        pane.dataController("""window.location.hash=(pkey == '*newrecord*')?null:'pk_'+pkey;""",
                               fired='^gnr.forms.formPane.loaded', pkey='=form.record?_pkey',_if='pkey')
        pane.dataController("genro.dom.setClass(dojo.body(),'form_locked',locked)", locked="^form.locked")
        pane.dataFormula('form.canWrite', '(!locked ) && writePermission', locked='^form.locked',
                         writePermission='=usr.writePermission', _init=True)
        pane.dataFormula('form.canDelete', '(!locked) && deletePermission', locked='^form.locked',
                         deletePermission='=usr.deletePermission', _init=True)
        pane.dataFormula('form.readOnly', 'formLocked', formLocked='^status.locked')
        pane.dataFormula('form.lockAcquire', '(!statusLocked) && lock', statusLocked='^status.locked',
                         lock=self.recordLock or False)
        pane.dataController("""
                               SET form.logical_deleted = (GET form.record.__del_ts != null);
                               if (lockId){
                                   //alert('lockId:'+lockId)
                               }
                               else if (username){
                                   //alert('already locked by:'+username)
                                   //SET status.locked=true;
                               }""",

                            lockId='=form.record?lockId',
                            username='=form.record?locking_username',
                            _fired='^form.onRecordLoaded')

        pane.dataController("""if(isLocked){
                                 //if not unlockable return
                                 //placeholder 
                                }
                                SET status.locked=!isLocked;
                                genro.formById('formPane').setLocked(!isLocked);
                            """, _fired='^status.changelock',
                            isLocked='=status.locked')
        pane.dataController("""SET status.statusClass = isLocked?'tb_button icnBaseLocked':'tb_button icnBaseUnlocked';
                               SET status.lockLabel = isLocked?unlockLabel:lockLabel;
                                   """, isLocked="^status.locked", lockLabel='!!Lock',
                            unlockLabel='!!Unlock')

        self.formLoader('formPane', resultPath='form.record', _fired='^form.doLoad', lock='=form.lockAcquire',
                        readOnly='=form.readOnly',
                        table=self.maintable, pkey='=list.selectedId', method='loadRecordCluster',
                        loadingParameters='=gnr.tables.maintable.loadingParameters',
                        onLoaded='FIRE form.onRecordLoaded;', sqlContextName='sql_record')

        self.formSaver('formPane', resultPath='form.save_result', method='saveRecordCluster',
                       table=self.maintable, _fired='^form.save', _onCalling='FIRE pbl.bottomMsg=msg;',
                       onSaving=self.onSavingFormBase(),
                       msg='!!Saving...', saveAlways=getattr(self, 'saveAlways', False))

        pane.dataController(""" var msg = '';
                                if(reason=='invalid'){
                                    msg = msg_invalid;
                                }
                                else if(reason=='nochange'){
                                    msg = msg_nochange;
                                }
                                if(msg){
                                    genro.dlg.alert(msg,title);
                                }
                                """, reason="^gnr.forms.formPane.save_failed",
                            msg_nochange='!!No change to save.',
                            msg_invalid='!!Invalid data, please check the form.',
                            title="!!Warning")

        pane.dataRpc('form.delete_result', 'deleteRecordCluster', data='=form.record?=genro.getFormChanges("formPane");'
                     , _POST=True,
                     table=self.maintable, toDelete='^form.doDeleteRecord')
        pane.dataController("""genro.dlg.ask(askTitle,saveMessage,{save:saveButton,forget:cancelButton,review:reviewButton},'form.dlgAction');
                              SET form.destidx = newidx;
                                   """,
                            newidx='^form.newidx', changed='=gnr.forms.formPane.changed',
                            askTitle="!!Unsaved changes",
                            saveMessage='!!There are unsaved changes', saveButton='!!Save changes',
                            cancelButton='!!Forget changes', reviewButton='!!Review changes',
                            _if='changed', _else='SET list.selectedIndex=newidx')

        pane.dataController("""
                            if(result=='save'){
                                FIRE form.save;
                            }else if(result=='forget'){
                                SET list.selectedIndex=newidx;
                            }else{
                                SET form.destidx = null;
                            }
                            """, newidx='=form.destidx',
                            result='^form.dlgAction')

        pane.dataFormula('form.atBegin', '(idx==0)', idx='^list.selectedIndex')
        pane.dataFormula('form.atEnd', '(idx==rowcount-1)', idx='^list.selectedIndex', rowcount='=list.rowcount')
        pane.dataController("""var newidx;
                               if (btn == 'add'){newidx = -1;}
                               else if (btn == 'first'){newidx = 0;}
                               else if (btn == 'last'){newidx = rowcount-1;}
                               else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                               else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                               if (modifier=='Shift' && changed){
                                    SET form.destidx = newidx;
                                    FIRE form.save;
                               }else{
                                    FIRE form.newidx = newidx;
                               }
                               
                            """, btn='^form.navbutton', modifier='=form.navbutton?modifier', idx='=list.selectedIndex',
                            changed='=gnr.forms.formPane.changed',
                            rowcount='=list.rowcount')

        pane.dataController(""" 
                                var currSet;
                                if (old_pkey != '*newrecord*'){
                                    var newrecords = GET list.newrecords || [];
                                    if(dojo.indexOf(newrecords,pkey)<0){
                                        genro.wdgById("maingrid").rowBagNodeUpdate(idx,record,pkey);
                                        currSet = 'changedrecords';
                                    } 
                               }else{
                                    //Insert
                                        currSet = 'newrecords';
                               }
                               if(currSet){
                                   var cs = genro.getData('list.'+currSet);
                                       if (!cs){
                                            cs = [];
                                            genro.setData('list.'+currSet, cs);
                                       }
                                   cs.push(pkey);
                               }
                               FIRE pbl.bottomMsg = msg;
                               if (custom_sound){
                                    genro.playSound(custom_sound);
                               }
                               
                               if (destidx&&destidx!=idx){
                                    SET list.selectedIndex=destidx;
                                    SET form.destidx = null;
                               }else{
                                    SET list.selectedId = pkey;
                                    FIRE form.doLoad;
                               }
                            """, record='=form.record',
                            msg='!!Record saved',
                            custom_sound='=gnr.user_preference.sys.sounds.onsaved',
                            idx='=list.selectedIndex',
                            pkey='^form.save_result',
                            destidx='=form.destidx',
                            old_pkey='=list.selectedId',
                            error='=form.save_result?msg',
                            _if='!error',

                            _else='genro.dlg.alert(error)')

        pane.dataController("""SET list.selectedId = null;
                               FIRE pbl.bottomMsg = msg;
                               SET selectedPage = 0;
                               FIRE list.runQuery=true;
                            """, msg='!!Record deleted', result='^form.delete_result',
                            _if='result=="ok"', _else='FIRE pbl.bottomMsg=result;')


    def formToolbar(self, pane):
        tb = pane.toolbar(_class='th_toolbar')
        self.confirm(pane, title='!!Confirm record deletion', width='50em',
                     msg='!!Are you sure to delete?',
                     btn_ok='!!Delete', btn_cancel='!!Cancel',
                     action_ok='FIRE form.doDeleteRecord',
                     fired='^form.deleteRecord')
        t_l = tb.div(float='left', margin_left='4px')
        t_l.button('!!First', fire_first='form.navbutton', iconClass="tb_button icnNavFirst", disabled='^form.atBegin',
                   showLabel=False)
        t_l.button('!!Previous', fire_prev='form.navbutton', iconClass="tb_button icnNavPrev", disabled='^form.atBegin',
                   showLabel=False)
        t_l.button('!!Next', fire_next='form.navbutton', iconClass="tb_button icnNavNext", disabled='^form.atEnd',
                   showLabel=False)
        t_l.button('!!Last', fire_last='form.navbutton', iconClass="tb_button icnNavLast", disabled='^form.atEnd',
                   showLabel=False)
        if self.tblobj.logicalDeletionField:
            self.setLogicalDeletionCheckBox(tb.div(float='left'))

        t_r = tb.div(float='right')

        self.formtoolbar_right(t_r)
        #t_c = tb.div(height='25px')

    def formtoolbar_right(self, t_r):
        if self.userCanDelete() or self.userCanWrite():
            ph = t_r.div(_class='button_placeholder', float='right')
            ph.button(label='^status.lockLabel', fire='status.changelock', iconClass="^status.statusClass",
                      showLabel=False)

        if hasattr(self.tblobj, 'hasRecordTags') and\
           self.tblobj.hasRecordTags() and\
           self.application.checkResourcePermission(self.canLinkTag(), self.userTags):
            ph = t_r.div(_class='button_placeholder', float='right')
            ph.button('!!Tags', float='right', action='FIRE #linktag_dlg.open={call_mode:"form"};',
                      iconClass="icnTag", showLabel=False)

        t_r.div(_class='button_placeholder', float='right').button('!!List view', float='right',
                                                                   action='FIRE form.newidx = -2;',
                                                                   iconClass="tb_button tb_listview", showLabel=False)
        t_r.div(float='right', nodeId='formStatus', hidden='^status.locked', _class='semaphore')
        t_r.data('form.statusClass', 'greenLight')
        t_r.dataController("""genro.dom.removeClass('formStatus',"greenLight redLight yellowLight");
                              if(isValid){
                                 if(isChanged){
                                     genro.dom.addClass('formStatus',"yellowLight");
                                 }else{
                                     genro.dom.addClass('formStatus',"greenLight");
                                 }
                              }else{
                                    genro.dom.addClass('formStatus',"redLight");
                              }
                              """, isChanged="^gnr.forms.formPane.changed",
                           isValid='^gnr.forms.formPane.valid')
        if self.userCanWrite():
            t_r.div(_class='button_placeholder', float='right').button('!!Save', fire="form.save",
                                                                       iconClass="tb_button db_save", showLabel=False,
                                                                       hidden='^status.locked')
            t_r.div(_class='button_placeholder', float='right').button('!!Revert', fire='form.doLoad',
                                                                       iconClass="tb_button db_revert",
                                                                       disabled='== !_changed',
                                                                       _changed='^gnr.forms.formPane.changed',
                                                                       showLabel=False, hidden='^status.locked')
            t_r.div(_class='button_placeholder', float='right').button('!!Add', fire_add='form.navbutton',
                                                                       iconClass="tb_button db_add",
                                                                       disabled='^form.noAdd', showLabel=False,
                                                                       visible='^form.canWrite')
        if self.userCanDelete():
            t_r.div(_class='button_placeholder', float='right').button('!!Delete', fire='form.deleteRecord',
                                                                       iconClass="tb_button db_del",
                                                                       visible='^form.canDelete',
                                                                       disabled='^form.noDelete', showLabel=False)