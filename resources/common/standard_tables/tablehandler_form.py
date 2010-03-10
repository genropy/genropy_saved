#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrbaseclasses import BaseComponent

class TableHandlerForm(BaseComponent):
    def pageForm(self,pane,bottom):
        bc=pane.borderContainer(nodeId='formRoot',
                                sqlContextName='sql_record',
                                sqlContextRoot='form.record',
                                sqlContextTable=self.maintable)
        self.formController(bc)
        self.formToolbar(bc.contentPane(region='top',_class='sttbl_list_top'))
        self.formBase(bc,datapath='form.record',disabled='^form.locked',region='center',formId='formPane')
        if self.tblobj.logicalDeletionField:
            self.setLogicalDeletionCheckBox(bottom['left'])
            
    def formController(self,pane):
        self.formTitleBase(pane)
        pane.dataFormula('form.locked','statusLocked || recordLocked',statusLocked='^status.locked',
                                     recordLocked='=form.recordLocked',fired='^gnr.forms.formPane.loaded')
        pane.dataFormula('form.unlocked','!locked',locked='^form.locked')
        pane.dataFormula('form.canWrite','(!locked ) && writePermission',locked='^form.locked',writePermission='=usr.writePermission',_init=True)
        pane.dataFormula('form.canDelete','(!locked) && deletePermission',locked='^form.locked',deletePermission='=usr.deletePermission',_init=True)
        pane.dataFormula('form.lockAcquire','(!statusLocked) && lock',statusLocked='^status.locked',
                                     lock=self.recordLock or False)
        pane.dataController("""
                               SET form.logical_deleted = (GET form.record.__del_ts != null);
                               if (lockId){
                                   alert('lockId:'+lockId)
                               }
                               else if (username){
                                   alert('already locked by:'+username)
                                   SET status.locked=true;
                               }""",

                            lockId='=form.record?lockId',
                            username='=form.record?locking_username',
                            _fired='^form.onRecordLoaded')
        
        self.formLoader('formPane', resultPath='form.record',_fired='^form.doLoad',lock='=form.lockAcquire',
                        table=self.maintable, pkey='=list.selectedId',method='loadRecordCluster',
                        loadingParameters='=gnr.tables.maintable.loadingParameters',
                        onLoading='FIRE form.onRecordLoaded',
                        sqlContextName='sql_record')
        self.formSaver('formPane',resultPath='form.save_result',method='saveRecordCluster',
                        table=self.maintable,_fired='^form.save',_onCalling='FIRE pbl.bottomMsg=msg;',
                        msg ='!!Saving...',saveAlways=getattr(self,'saveAlways',False))
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
                                """,reason="^gnr.forms.formPane.save_failed",
                              msg_nochange='!!No change to save.', 
                              msg_invalid='!!Invalid data, please check the form.',
                              title="!!Warning")
        pane.dataRpc('form.delete_result','deleteRecordCluster', data='=form.record?=genro.getFormChanges("formPane");', _POST=True,
                        table=self.maintable,toDelete='^form.doDeleteRecord')
        pane.dataController("""genro.dlg.ask(askTitle,saveMessage,{save:saveButton,forget:cancelButton},'form.dlgAction');
                              SET form.dlgidx = newidx;
                                   """,
                                newidx='^form.newidx',changed='=gnr.forms.formPane.changed',
                                askTitle="!!Unsaved changes",
                                saveMessage='!!There are unsaved changes',saveButton='!!Save changes',
                                cancelButton='!!Forget changes',
                                _if='changed',_else='SET list.selectedIndex=newidx')
        
        pane.dataController("FIRE form.save;",newidx='=form.dlgidx',
                            result='^form.dlgAction',_if="result=='save'",
                            _else='SET list.selectedIndex=newidx')

        pane.dataFormula('form.atBegin','(idx==0)',idx='^list.selectedIndex')
        pane.dataFormula('form.atEnd','(idx==rowcount-1)',idx='^list.selectedIndex',rowcount='=list.rowcount')
        pane.dataController("""var newidx;
                               if (btn == 'add'){newidx = -1;}
                               else if (btn == 'first'){newidx = 0;}
                               else if (btn == 'last'){newidx = rowcount-1;}
                               else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                               else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                               FIRE form.newidx = newidx;
                            """,btn='^form.navbutton',idx='=list.selectedIndex',
                                rowcount='=list.rowcount')
                                
        pane.dataController(""" var currSet;
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
                               SET list.selectedId = pkey;
                               FIRE pbl.bottomMsg = msg;
                               FIRE form.doLoad;
                            """, record='=form.record',
                                 msg='!!Record saved',
                                 idx='=list.selectedIndex',
                                 pkey='^form.save_result',
                                 old_pkey='=list.selectedId',
                                 error='=form.save_result?msg',
                                 _if='!error',
                                 _else='genro.dlg.alert(error)')
          
        pane.dataController("""SET list.selectedId = null;
                               FIRE pbl.bottomMsg = msg;
                               SET selectedPage = 0;
                               FIRE list.runQuery=true;
                            """,  msg='!!Record deleted', result='^form.delete_result', 
                            _if='result=="ok"', _else='FIRE pbl.bottomMsg=result;')
                                     

    def formToolbar(self, pane):
        tb = pane.toolbar(_class='th_toolbar')
        self.confirm(pane,title='!!Confirm record deletion',width='50em',
                           msg='!!Are you sure to delete ?',
                           btn_ok='!!Delete',btn_cancel='!!Cancel',
                           action_ok='FIRE form.doDeleteRecord',
                           fired='^form.deleteRecord')
        t_l = tb.div(float='left',margin_left='4px')
        t_l.button('!!First', fire_first='form.navbutton', iconClass="tb_button icnNavFirst", disabled='^form.atBegin', showLabel=False)
        t_l.button('!!Previous', fire_prev='form.navbutton', iconClass="tb_button icnNavPrev", disabled='^form.atBegin', showLabel=False)
        t_l.button('!!Next', fire_next='form.navbutton', iconClass="tb_button icnNavNext", disabled='^form.atEnd', showLabel=False)
        t_l.button('!!Last', fire_last='form.navbutton', iconClass="tb_button icnNavLast", disabled='^form.atEnd', showLabel=False)
        t_r = tb.div(float='right')
        self.formtoolbar_right(t_r)
        #t_c = tb.div(height='25px')
        
    def formtoolbar_right(self,t_r):
        if self.userCanDelete() or self.userCanWrite():
            ph = t_r.div(_class='button_placeholder',float='right')
            ph.button('!!Unlock', float='right',fire='status.unlock', 
                        iconClass="tb_button icnBaseLocked", showLabel=False,hidden='^status.unlocked')
            ph.button('!!Lock', float='right',fire='status.lock', 
                        iconClass="tb_button icnBaseUnlocked", showLabel=False,hidden='^status.locked')
                        
        if self.tblobj.hasRecordTags() and\
            self.application.checkResourcePermission(self.canLinkTag(), self.userTags):
            ph = t_r.div(_class='button_placeholder',float='right')
            ph.button('!!Tags', float='right',action='FIRE #linktag_dlg.open={call_mode:"form"};', 
                        iconClass="icnTag",showLabel=False)
        
        t_r.div(_class='button_placeholder',float='right').button('!!List view', float='right', action='FIRE form.newidx = -2;', 
                    iconClass="tb_button tb_listview", showLabel=False)
        t_r.div(float='right',nodeId='formStatus',hidden='^status.locked',_class='semaphore')
        t_r.data('form.statusClass','greenLight')
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
                              """,isChanged="^gnr.forms.formPane.changed",
                            isValid='^gnr.forms.formPane.valid')
        if self.userCanWrite():
            t_r.div(_class='button_placeholder', float='right').button('!!Save',fire="form.save", iconClass="tb_button db_save",showLabel=False,
                                hidden='^status.locked')
            t_r.div(_class='button_placeholder', float='right').button('!!Revert',fire='form.doLoad', iconClass="tb_button db_revert",
                                        disabled='== !_changed', _changed='^gnr.forms.formPane.changed', 
                         showLabel=False, hidden='^status.locked')
            t_r.div(_class='button_placeholder', float='right').button('!!Add', fire_add='form.navbutton', iconClass="tb_button db_add",
                         disabled='^form.noAdd', showLabel=False,visible='^form.canWrite')
        if self.userCanDelete():
            t_r.div(_class='button_placeholder', float='right').button('!!Delete',fire='form.deleteRecord', iconClass="tb_button db_del",
                                   visible='^form.canDelete',disabled='^form.noDelete', showLabel=False)