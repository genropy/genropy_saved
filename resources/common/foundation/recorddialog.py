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

    def recordDialog(self, table=None, firedPkey=None, pane=None, height=None, width=None, _class=None,
                     title=None, formCb=None, onSaved='', saveKwargs=None, loadKwargs=None,
                     savePath='', bottomCb=None, savingMethod=None,
                     loadingMethod=None, loadingParameters=None, onClosed='', onShow='',
                     validation_failed='alert', custom_table_id=None, centerOn=None,
                     dlgId=None, formId=None, datapath=None,
                     dlgPars=None,
                     # TODO is dlgPars really supported? it seems to prevent the recordDialog from working properly.
                     toolbarCb=None, toolbarPars=None,
                     record_datapath=None,form_datapath=None, disabled=None, **kwargs):
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
        toolbarPars = toolbarPars or {}

        assert not '_onResult' in saveKwargs, 'You cannot put a _onResult here'
        assert not '_onResult' in loadKwargs, 'You cannot put a _onResult here'
        assert not 'loadingParameters' in loadKwargs, 'You cannot put a loadingParameters here'

        tableId = custom_table_id or table.replace('.', '_')
        dlgId = dlgId or  'dlg_%s' % tableId
        formId = formId or  '%s_form' % tableId

        assert dlgId != formId, "formId and dlgId must not be equal"

        disabled = disabled or '^form.locked'
        sqlContextName = 'sqlcontext_%s' % tableId
        mainDatapath = datapath or 'aux_forms.%s' % tableId
        sqlContextRoot = record_datapath or '#%s.record' % dlgId
        title = title or '^.record?caption'
        page = pane
        if page is None:
            if datapath:
                assert not datapath.startswith('.'), 'pass a pane if you need to use a relative datapath'
            page = self.pageSource()
        dlgPars = dlgPars or {}
        if onShow:
            dlgPars['connect_show'] = onShow
        dlgPars['centerOn'] = '_pageRoot'
        if centerOn:
            dlgPars['centerOn'] = centerOn
        dlg = page.dialog(nodeId=dlgId, title=title,
                          datapath=mainDatapath, **dlgPars)
        dlgBC = dlg.borderContainer(height=height, nodeId='%s_layout' % dlgId,
                                    width=width, _class=_class,
                                    sqlContextName=sqlContextName,
                                    sqlContextRoot=sqlContextRoot,
                                    sqlContextTable=table)
        self._recordDialogController(dlgBC, dlgId, formId,
                                     table, saveKwargs, loadKwargs, firedPkey, sqlContextName,
                                     onSaved, onClosed, savePath, savingMethod, loadingMethod,
                                     loadingParameters, validation_failed, record_datapath, **kwargs)

        self._recordDialogLayout(dlgBC, dlgId, formId, table, formCb,
                                 bottomCb, toolbarCb, record_datapath,form_datapath, toolbarPars, disabled)

    def _recordDialogController(self, pane, dlgId, formId,
                                table, saveKwargs, loadKwargs, firedPkey, sqlContextName,
                                onSaved, onClosed, savePath, savingMethod, loadingMethod,
                                loadingParameters, validation_failed, record_datapath, **kwargs):
        onSaved = onSaved or ''
        onSaved = 'FIRE #%s.afterSaving = result; %s' % (dlgId, onSaved)
        pane.dataController(""" if(saveAndAdd){
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
                                }else if(saveAndReload){
                                    SET .closeDlg = false;
                                    SET .addRecord = false;
                                    SET .changeRecordIn = '*';
                                    FIRE .saveRecord;
                                }""", saveAndAdd="^.saveAndAdd",
                            saveAndClose="^.saveAndClose",
                            saveAndChangeIn='^.saveAndChangeIn',
                            saveAndReload='^.saveAndReload')

        pane.dataController(""" if(closeDlg){
                                    FIRE .exitAction='saved';
                                }else if(addRecord){
                                    FIRE .addNew;
                                }else if(changeRecordIn){
                                    SET .current_pkey = changeRecordIn=='*'?savedPkey:changeRecordIn;
                                    FIRE .load;
                                }""",
                            savedPkey="^.afterSaving", addRecord='=.addRecord',
                            changeRecordIn='=.changeRecordIn',
                            closeDlg='=.closeDlg')

        pane.dataController("""SET .current_pkey = "*newrecord*";
                               FIRE .load""", _fired="^.addNew")

        pane.dataController("""genro.wdgById("%s").show(); 
                               SET .isOpen = true;
                               SET .current_pkey = (!firedPkey||firedPkey===true) ? "*newrecord*" : firedPkey;
                               FIRE .load;
                            """ % dlgId, firedPkey=firedPkey)
        pane.dataController('genro.formById("%s").load();' % formId, _fired="^.load")

        pane.dataController("""var dlgNode=genro.nodeById("%s");
                               dlgNode.widget.hide();
                               SET .isOpen = false;
                               if (onClosed){
                                   funcCreate(onClosed, 'exitAction').call(dlgNode,exitAction);
                               }
                            """ % dlgId, exitAction='^.exitAction', onClosed=onClosed)

        loadingParameters = loadingParameters or '=gnr.tables.%s.loadingParameters' % table.replace('.', '_')
        loadKwargs = dict(loadKwargs)
        loadKwargs.update(**kwargs)
        self.formLoader(formId, resultPath=record_datapath or '.record',
                        table=table, pkey='=.current_pkey',
                        method=loadingMethod, loadingParameters=loadingParameters,
                        datapath='#%s' % dlgId,
                        sqlContextName=sqlContextName, **loadKwargs)

        self.formSaver(formId, resultPath=savePath or '.savingResult',
                       table=table, _fired='^.saveRecord',
                       method=savingMethod, onSaved=onSaved,
                       datapath='#%s' % dlgId,
                       **saveKwargs)
        pane.dataController("""if(save_failed == "nochange"){
                                        FIRE .exitAction='nochange';
                                }else if(save_failed == "invalid"){
                                    FIRE .validation_failed;
                                }""", save_failed='^gnr.forms.%s.save_failed' % formId)
        pane.dataController("SET .saveDisabled = saving;", saving="gnr.forms.%s.saving" % formId)

        pane.dataController("""genro.dom.setClass(dlgId,'warningForm',warning);""", warning="^.warning", dlgId=dlgId)

        if validation_failed == "alert":
            pane.dataController("genro.dlg.alert(msg,title)",
                                _fired='^.validation_failed',
                                msg='!!Not valid data. Please check the form',
                                title='!!Warning')


        elif validation_failed == "focus":
            pane.dataController("genro.formById('%s').focusFirstInvalidField()" % formId, _fired="^.validation_failed")

    def _recordDialogLayout(self, bc, dlgId, formId, table,
                            formCb, bottomCb, toolbarCb, record_datapath, form_datapath,toolbarPars, disabled):
        if callable(toolbarCb):
            toolbarCb(bc, region='top', table=table, **toolbarPars)
        bottom = bc.contentPane(region='bottom', _class='dialog_bottom')
        bottomCb = bottomCb or getattr(self, 'recordDialog_bottom')
        bottomCb(bottom)
        form_datapath = form_datapath
        record_datapath = record_datapath or '.record'
        stack = bc.stackContainer(region='center', _class='pbl_background', formId=formId,datapath=form_datapath,
                                  selected='^#%s.stackPane' % dlgId,formDatapath=record_datapath)
        formCb(stack.contentPane(datapath=record_datapath), disabled=disabled, table=table)

    #Jeff suggests that the margins be taken out of the code and put into the css
    def recordDialog_bottom(self, pane):
        pane.button('!!Save', float='right', baseClass='bottom_btn',
                    fire=".saveAndClose", margin_left='5px', width='5em',
                    disabled='^.saveDisabled')
        pane.button('!!Cancel', float='right', baseClass='bottom_btn',
                    fire_cancel='.exitAction', margin_left='5px', width='5em')
        return pane

    def rpc_deleteIncludedViewRecord(self, table, rowToDelete, **kwargs):
        tblobj = self.db.table(table)
        recordToDelete = tblobj.record(rowToDelete, for_update=True, mode='bag')
        tblobj.delete(recordToDelete)
        self.db.commit()
