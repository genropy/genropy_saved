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

"""""" # don't delete this line! MANDATORY for Sphinx autodoc

from gnr.web.gnrbaseclasses import BaseComponent
import warnings

class SelectionHandler(BaseComponent):
    """To use it you should include py_requires="selectionhandler"
    
    SelectionHandler is a new component that is used as a replacement for includedView and recordDialog. 
    It adds a navigation toolbar for first, previous, next and last.
    It adds a "+" button to add new records from within the dialog
    It manages automatically:
    
    * all the dataControllers for add and delete .
    * the add_action and del_action.
    * the connect_onRowDblClick parameter.
    
    To replace an includedView and recordDialog do the following:
    
    #. Replace the call to includedView with a call to recordHandler
    #. Comment out:
       
       * add_action
       * del_action
       * addOnCb
       * connect_onRowDblClick="FIRE .firedPkey = this.widget.rowIdByIndex($1.rowIndex);"
       * all the controllers that manage delete or add
       
    #. Add a new parameter to replace the recordDialog function, having all parameters of the
       recordDialog passed into a dictionary, except for: onSaved='FIRE #contact_logGrid.reload;',
       dialogPars=dict(...)
    """
    py_requires = 'foundation/includedview:IncludedView,foundation/recorddialog'

    def selectionHandler(self, bc, nodeId=None, table=None, datapath=None, struct=None, label=None,
                         selectionPars=None, dialogPars=None, reloader=None, externalChanges=None,
                         hiddencolumns=None, custom_addCondition=None, custom_delCondition=None,
                         askBeforeDelete=True, checkMainRecord=True, onDeleting=None, dialogAddRecord=True,
                         onDeleted=None, add_enable=True, del_enable=True,add_action=True,del_action=True,
                         parentSave=False, parentId=None, parentLock='^status.locked', reload_onSaved=True,
                         footer=None,**kwargs):
        # --------------------------------------------------------------------------------------------- Mandatory param checks
        #assert dialogPars,'dialogPars are Mandatory'

        if dialogPars:
            assert not 'table' in dialogPars, 'take the table of the grid'
            assert not 'firedPkey' in dialogPars, 'auto firedPkey'
            assert not 'savePath' in dialogPars, 'toolbarCb calculated'
            assert not 'toolbarCb' in dialogPars, 'toolbarCb calculated'
        assert not 'toolbarPars' in kwargs, 'remove toolbarPars par'
        assert 'order_by' in selectionPars, 'add order_by to selectionPars'
        assert not 'connect_onRowDblClick' in kwargs, 'remove connect_onRowDblClick par'

        # --------------------------------------------------------------------------------------------- Suggested param checks
        # 
        # These warnings can be disabled by the calling code (see the 'warnings' module in Python Standard Library Reference)

        if selectionPars:
            for k, p in selectionPars.items():
                if isinstance(p, basestring):
                    if p.startswith('^'):
                        warnings.warn("[selectionhandler] use '=' and not '^' in selectionPars: %s=%s" % (k, repr(p)),
                                      stacklevel=2)

        if dialogPars:
            for k, p in dialogPars.items():
                if isinstance(p, basestring):
                    if p.startswith('^'):
                        warnings.warn("[selectionhandler] use '=' and not '^' in dialogPars: %s=%s" % (k, repr(p)),
                                      stacklevel=2)

            dialogPars['table'] = table
            dlgId = dialogPars.get('dlgId', "%s_dlg" % nodeId)
            dialogPars['dlgId'] = dlgId
            dialogPars['formId'] = dialogPars.get('formId', "%s_form" % nodeId)
            dialogPars['datapath'] = dialogPars.get('datapath', '#%s.dlg' % nodeId)
            if reload_onSaved:
                dialogPars['onSaved'] = 'FIRE #%s.reload; %s' % (nodeId, dialogPars.get('onSaved', ''))
            dialogPars['firedPkey'] = '^.pkey'
            dialogPars['disabled'] = '^#%s.status.locked' % nodeId
            dialogPars['toolbarCb'] = self._sh_toolbar
            defaultDialogPars = dict(add_action=True, del_action=False, save_action=False, lock_action=True,
                                     nodeId=nodeId)
            defaultDialogPars.update(dialogPars.get('toolbarPars', {}))
            dialogPars['toolbarPars'] = defaultDialogPars
            self.recordDialog(**dialogPars)

        if reloader and isinstance(reloader, basestring) and not reloader.startswith('^'):
            warnings.warn("[selectionhandler] reloader should start with '^': %s" % repr(reloader), stacklevel=2)
            
        # --------------------------------------------------------------------------------------------- Implementation
        
        add_action = 'FIRE .dlg.pkey="*newrecord*";' if add_action is True else add_action
        del_action = 'FIRE .delete_record;' if del_action is True else del_action
        if parentSave:
            add_action = 'FIRE .checkForAdd;'
            bc.dataController("""
                                 if(mainformId){
                                     var mainForm = genro.formById(mainformId);  
                                     if (mainForm.getInvalidFields().len()>0){
                                            genro.dlg.alert(invalidFieldsMsg,invalidFieldsTitle);
                                            return;
                                     }
                                     if(mainForm.changed){
                                         if (parentSave!=true && action!="confirmed"){
                                            genro.dlg.ask(title,msg,null,
                                                        {confirm:"genro.fireEvent('%s.checkForAdd','confirmed')"});
                                            return;
                                         }
                                         var onSavedCb = function(){
                                            genro.fireEvent('%s.dlg.pkey','*newrecord*');
                                         }
                                         var deferred = mainForm.save(false);
                                         deferred.addCallback(onSavedCb);
                                         return;
                                     }
                                }
                                FIRE .dlg.pkey = "*newrecord*";
                                
                                """ % (datapath, datapath), action="^.checkForAdd",
                              datapath=datapath, mainformId='==this.getInheritedAttributes().formId;',
                              parentSave=parentSave, title='!!Unsaved changes',
                              msg='!!The main record has some changes. Do you want to save them?',
                              invalidFieldsMsg='!!The main record contains some invalid field. Please check before adding new sub-records'
                              ,
                              invalidFieldsTitle='!!Warning', newrecordTitle='!!Warning',
                              newrecordMsg='!!You have to save the main record before. Do you want to save?')
        
        self.includedViewBox(bc, label=label, datapath=datapath,
                             add_action=add_action,
                             add_enable='^.can_add', del_enable='^.can_del',
                             del_action=del_action,
                             nodeId=nodeId, table=table, struct=struct, hiddencolumns=hiddencolumns,
                             reloader=reloader, externalChanges=externalChanges,
                             #connect_onRowDblClick='this.widget.editCurrentRow($1.rowIndex);',
                             linkedForm='%s_form' % nodeId, openFormEvent='onRowDblClick',
                             selectionPars=selectionPars, askBeforeDelete=True, footer=footer,**kwargs)        
        controller = bc.dataController(datapath=datapath)
        controller.dataController("FIRE .dlg.pkey = pkey;", pkey='^gnr.forms.%s_form.openFormPkey' % nodeId)
        if checkMainRecord:
            if parentId:
                main_record_id = parentId
            else:
                main_record_id = '^form.record.%s' % self.db.table(self.maintable).pkey
        else:
            main_record_id = True
            
            
        if parentLock:
            controller.dataController("""
                                        if(_reason=='node'){
                                            parentLock = parentLock;
                                        }else{
                                            parentLock = locked;
                                        }
                                        SET .status.locked=parentLock;
                                        """,
                                      parentLock=parentLock,formsubscribe_onLockChange=True)
            controller.dataController("""
                                        SET %s=isLocked;""" % parentLock[1:],
                                      parentLock=parentLock, isLocked='^.status.locked',
                                      _if='parentLock!=isLocked')
        controller.dataController("""
                                if(isLocked){
                                //if not unlockable return
                                    isLocked = isLocked //if unlocable 
                                }
                                SET .status.locked=!isLocked
                                """,
                                  _fired='^.status.changelock',
                                  isLocked='=.status.locked')
                                  
        controller.dataController("""
                                SET .status.statusClass = isLocked?'tb_button icnBaseLocked':'tb_button icnBaseUnlocked';
                                SET .status.lockLabel = isLocked?unlockLabel:lockLabel;
                               """, isLocked="^.status.locked", lockLabel='!!Lock',
                                  unlockLabel='!!Unlock')

        controller.dataFormula(".can_add", "add_enable?(main_record_id!=null)&&custom_condition:false",
                               add_enable=add_enable, main_record_id=main_record_id, isLocked='^.status.locked',
                               _if='!isLocked',
                               _else='false;', custom_condition=custom_addCondition or True)
        controller.dataFormula(".can_del", "del_enable?(main_record_id!=null)&&custom_condition:false",
                               del_enable=del_enable, selectedId='^.selectedId', _if='!isLocked&&selectedId',
                               _else='false',
                               isLocked='^.status.locked', main_record_id=main_record_id or True,
                               custom_condition=custom_delCondition or True)

        controller.dataController("""
                                    genro.dlg.ask(title, msg, null, '#%s.confirm_delete')""" % nodeId,
                                  _fired="^.delete_record", title='!!Warning',
                                  msg='!!You cannot undo this operation. Do you want to proceed?',
                                  _if=askBeforeDelete)
        onDeleted = onDeleted or ''
        onDeleting = onDeleting or ''
        controller.dataRpc('.deletedPkey', 'deleteDbRow', pkey='=.selectedId', table=table,
                           _confirmed='^.confirm_delete', _if='_confirmed=="confirm"',
                           _onResult='FIRE .afterDeleting;FIRE .reload; %s' % onDeleted, _openDlg='=.dlg.isOpen',
                           _onCalling="""
                                        if(_openDlg){
                                            $1.pkey = GET .dlg.current_pkey;
                                            FIRE .dlg.exitAction='deleted';
                                        } %s
                                        """ % onDeleting)

        controller.dataController("""
                                 var form = genro.formById(gridId+'_form');
                                 if(!form.changed){
                                    FIRE .changeAnyway= btn;
                                 }else{
                                    var saveAction = "genro.fireEvent('#"+gridId+".saveAndChange','"+btn+"');";
                                    var noSaveAction = "genro.fireEvent('#"+gridId+".changeAnyway','"+btn+"');";
                                    genro.dlg.ask(title,msg,
                                                 {save:save,dont_save:dont_save,cancel:cancel},
                                                 {save:saveAction,dont_save:noSaveAction});
                                 }
                             
                              """, btn='^.navbutton',
                                  title='!!Warning',
                                  msg='!!There are unsaved changes',
                                  save='!!Save', save_act='FIRE .dlg.saveAndChangeIn',
                                  dont_save='!!Do not save',
                                  cancel='!!Cancel', gridId=nodeId)
        controller.dataController("""
                                    var btn = changeAnyway||saveAndChange;
                                    var grid = genro.wdgById(gridId);
                                    var rowcount = grid.rowCount;
                                    var newidx;
                                    if (btn == 'first' || btn=='new'){newidx = 0;} 
                                    else if (btn == 'last'){newidx = rowcount-1;}
                                    else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                                    else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                                    SET .selectedIndex = newidx;
                                    var selectedId = btn=='new'?'*newrecord*':genro.wdgById(gridId).rowIdByIndex(newidx);
                                    if(changeAnyway){
                                        SET .dlg.current_pkey = selectedId;
                                        FIRE .dlg.load;
                                    }else if(saveAndChange){
                                        FIRE .dlg.saveAndChangeIn = selectedId;
                                    }
                                    """, saveAndChange="^.saveAndChange",
                                  changeAnyway='^.changeAnyway', gridId=nodeId,
                                  idx='=.selectedIndex')
        controller.data(".dialogAddDisabled", not dialogAddRecord)
        controller.data('.atBegin', True)
        controller.data('.atEnd', True)
        controller.dataFormula('.atBegin', '(idx==0||idx==-1)', idx='^.selectedIndex')
        controller.dataFormula('.atEnd', '(idx==genro.wdgById(gridId).rowCount-1)||idx==-1', idx='^.selectedIndex',
                               gridId=nodeId)

    def _sh_toolbar(self, parentBC, add_action=None, lock_action=None,
                    save_action=None, del_action=None, nodeId=None, **kwargs):
        pane = parentBC.contentPane(padding='2px', overflow='hidden', **kwargs)
        tb = pane.toolbar(datapath='.#parent') #referred to the grid
        tb.button('!!First', fire_first='.navbutton', iconClass="tb_button icnNavFirst",
                  disabled='^.atBegin', showLabel=False)
        tb.button('!!Previous', fire_prev='.navbutton', iconClass="tb_button icnNavPrev",
                  disabled='^.atBegin', showLabel=False)
        tb.button('!!Next', fire_next='.navbutton', iconClass="tb_button icnNavNext",
                  disabled='^.atEnd', showLabel=False)
        tb.button('!!Last', fire_last='.navbutton', iconClass="tb_button icnNavLast",
                  disabled='^.atEnd', showLabel=False)

        if lock_action:
            spacer = tb.div(float='right', _class='button_placeholder')
            spacer.button(label='^.status.lockLabel', fire='.status.changelock', iconClass="^.status.statusClass",
                          showLabel=False)
        if save_action:
            spacer = tb.div(float='right', _class='button_placeholder')
            spacer.button('!!Save changes', fire=".dlg.saveAndReload",
                          iconClass="tb_button db_save", showLabel=False, hidden='^.status.locked')
            spacer = tb.div(float='right', _class='button_placeholder')
            spacer.button('!!Revert', fire=".dlg.load", iconClass="tb_button db_revert",
                          showLabel=False, hidden='^.status.locked')

        if add_action:
            spacer = tb.div(float='right', _class='button_placeholder')
            spacer.button('!!Add', action='FIRE .navbutton="new";', hidden='^.status.locked',
                          iconClass='tb_button db_add', showLabel=False)
        if del_action:
            spacer = tb.div(float='right', _class='button_placeholder')
            spacer.button('!!Delete', action='FIRE .delete_record;', hidden='^.status.locked',
                          iconClass='tb_button db_del', showLabel=False, disabled='==_curr_pkey=="*newrecord*"',
                          _curr_pkey='^.dlg.current_pkey')
                          