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

"""
Component for recorddialog:
"""
from gnr.web.gnrbaseclasses import BaseComponent

class RecordDialog(BaseComponent):
    """
    RecordHandler allows to Load and Save a record without passing through the mainrecord path
    it executes saving and loading in an independent way from the mainrecord of a standard table. 
    """
    def recordDialog(self,table=None,firedPkey=None,pane=None,height=None,width=None,_class=None,
                    title=None,formCb=None,onSaved='',saveKwargs=None,loadKwargs=None,
                    savePath='',bottomCb=None,savingMethod=None,
                    loadingMethod=None, loadingParameters=None,onClosed='',onShow='',
                    validation_failed='alert',custom_table_id=None,centerOn=None,
                    dlgId=None,formId=None,datapath=None,dlgPars=None,toolbarCb=None,
                    record_datapath=None,**kwargs):
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
        saveKwargs = saveKwargs or {}
        loadKwargs = loadKwargs or {}

        assert not '_onResult' in saveKwargs,'You cannot put a _onResult here'
        assert not '_onResult' in loadKwargs,'You cannot put a _onResult here'
        assert not 'loadingParameters' in loadKwargs,'You cannot put a loadingParameters here'

        tableId = custom_table_id or table.replace('.','_')
        dlgId = dlgId or  'dlg_%s' % tableId
        formId = formId or  '%s_form' % tableId
        
        sqlContextName='sqlcontext_%s' %tableId
        controllerPath = datapath or 'aux_forms.%s' % tableId
        sqlContextRoot= record_datapath or '%s.record' % controllerPath
        title = title or '^.record?caption'
        page = pane
        if page is None:
            page = self.pageSource()
        dlgPars=dlgPars or {}
        if onShow:
            dlgPars['connect_show']=onShow     
        if centerOn:
            dlgPars['centerOn']=centerOn             
        dlg = page.dialog(nodeId=dlgId,title=title,
                        datapath=controllerPath,**dlgPars)
        dlgBC = dlg.borderContainer(height=height, nodeId='%s_layout' %dlgId,
                                    width=width, _class=_class,
                                    sqlContextName=sqlContextName,
                                    sqlContextRoot=sqlContextRoot, 
                                    sqlContextTable= table)
        self._recordDialogController(dlgBC,dlgId,formId,controllerPath,
                                    table,saveKwargs,loadKwargs,firedPkey,sqlContextName,
                                    onSaved,onClosed,savePath,savingMethod,loadingMethod,
                                    loadingParameters,validation_failed,record_datapath,**kwargs)
                                    
        self._recordDialogLayout(dlgBC,dlgId,formId,controllerPath,table,formCb,bottomCb,toolbarCb,record_datapath)

    def _recordDialogController(self,pane,dlgId,formId,controllerPath,
                                table,saveKwargs,loadKwargs,firedPkey,sqlContextName,
                                onSaved,onClosed,savePath,savingMethod,loadingMethod,
                                loadingParameters,validation_failed,record_datapath,**kwargs):
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
                                }else if(saveAndChangeIn){
                                    SET .closeDlg = false;
                                    SET .addRecord = false;
                                    SET .changeRecordIn = saveAndChangeIn;
                                    FIRE .saveRecord;
                                }""",saveAndAdd="^.saveAndAdd",
                                saveAndClose="^.saveAndClose",
                                saveAndChangeIn='^.saveAndChangeIn')
                                
        pane.dataController(""" if(closeDlg){
                                    FIRE .exitAction='saved';
                                }else if(addRecord){
                                    FIRE .addNew;
                                }else if(changeRecordIn){
                                    SET .current_pkey = changeRecordIn;
                                    FIRE .load;
                                }""",
                            _fired="^.afterSaving",addRecord='=.addRecord',
                            changeRecordIn='=.changeRecordIn',
                            closeDlg='=.closeDlg')
        
        pane.dataController("""SET .current_pkey = "*newrecord*";
                               FIRE .load""",_fired="^.addNew")
                            
        pane.dataController("""genro.wdgById("%s").show(); 
                               SET .current_pkey = (!firedPkey||firedPkey===true) ? "*newrecord*" : firedPkey;
                               FIRE .load;
                            """ %dlgId,firedPkey=firedPkey)
        pane.dataController('genro.formById("%s").load();' %formId,_fired="^.load")
                            
        pane.dataController("""var dlgNode=genro.nodeById("%s");
                               dlgNode.widget.onCancel();
                               if (onClosed){
                                   funcCreate(onClosed, 'exitAction').call(dlgNode,exitAction);
                               }
                            """%dlgId, exitAction ='^.exitAction', onClosed=onClosed)
        
        loadingParameters = loadingParameters or '=gnr.tables.%s.loadingParameters' %table.replace('.','_')
        loadKwargs = dict(loadKwargs)
        loadKwargs.update(**kwargs)
        self.formLoader(formId,resultPath=record_datapath or '.record',
                        table=table,pkey='=.current_pkey',
                        method=loadingMethod,loadingParameters=loadingParameters,
                        datapath=controllerPath,
                        sqlContextName=sqlContextName,**loadKwargs)
                       
        self.formSaver(formId,resultPath= savePath or '.savingResult',
                       table=table, _fired='^.saveRecord',
                       method=savingMethod,onSaved=onSaved,datapath=controllerPath,**saveKwargs)
                       
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
        
    def _recordDialogLayout(self,bc,dlgId,formId,controllerPath,table,
                            formCb,bottomCb,toolbarCb,record_datapath):
        if callable(toolbarCb):
            toolbarCb(bc,region='top',table=table)
        bottom = bc.contentPane(region='bottom',_class='dialog_bottom')
        bottomCb = bottomCb or getattr(self,'_record_dialog_bottom')
        bottomCb(bottom)
        stack = bc.stackContainer(region='center',_class='pbl_background' ,formId=formId,
                                  selected='^%s.stackPane' %controllerPath,datapath=record_datapath or '.record')
        loading = stack.contentPane(_class='waiting')
        formCb(stack, disabled='^form.locked', table=table)

    #Jeff suggests that the margins be taken out of the code and put into the css
    def _record_dialog_bottom(self,pane):
        pane.button('!!Save',float='right',baseClass='bottom_btn',
                    fire=".saveAndClose", margin_left='5px', width='5em')
        pane.button('!!Cancel',float='right',baseClass='bottom_btn',
                    fire_cancel='.exitAction', margin_left='5px', width='5em')
        
    def rpc_deleteIncludedViewRecord(self, table, rowToDelete,**kwargs):
        tblobj = self.db.table(table)
        recordToDelete = tblobj.record(rowToDelete,for_update=True, mode='bag')
        tblobj.delete(recordToDelete)
        self.db.commit()
