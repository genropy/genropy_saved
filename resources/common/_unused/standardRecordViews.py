#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag
from gnr.web.gnrbaseclasses import BaseComponent

class RecordAndViews(BaseComponent):
    js_requires = 'standard_tables/standard_tables'
    css_requires = 'standard_tables/standard_tables'

    def userCanWrite(self):
        return self.application.checkResourcePermission(self.tableWriteTags(), self.userTags)

    def userCanDelete(self):
        return self.application.checkResourcePermission(self.tableDeleteTags(), self.userTags)

    def tableWriteTags(self):
        return 'superadmin'

    def tableDeleteTags(self):
        return 'superadmin'


    def conditionBase(self):
        #overwrite this
        return (None, None)

    def formBase(self, pane, disabled=None):
        #overwrite this
        pass

    def joinConditions(self):
        """hook to define all join conditions for retrieve records related to the current edited record"""
        pass

    def formToolbar(self, where):
        tb = where.contentPane(layoutAlign='top', height='30px', _class='toolbar').toolbar()
        t_l = tb.div(_class='toolbar_left', margin_top='5px', margin_left='4px')
        t_r = tb.div(_class='toolbar_right', margin_right='4px', margin_top='5px')
        t_c = tb.div(_class='toolbar_center', height='30px')
        trbtn = t_r.div(height='100%', width='130px', margin_right='24px', nodeId='query_buttons')
        if self.userCanDelete() or self.userCanWrite():
            trbtn.button('!!Unlock', float='right', fire='status.unlock', iconClass="tb_button db_lock", showLabel=False
                         , hidden='^status.unlocked')
            trbtn.button('!!Lock', float='right', fire='status.lock', iconClass="tb_button db_unlock", showLabel=False,
                         hidden='^status.locked')
        if self.userCanWrite():
            t_r.button('!!Save', float='right', fire='form.save', iconClass="tb_button db_save",
                       disabled='^form.modified?=!#v', showLabel=False)
            t_r.button('!!Revert', float='right', fire='form.reload', iconClass="tb_button db_revert",
                       disabled='^form.modified?=!#v', showLabel=False)

    def formController(self, pane):
        pane.data('usr.unlockPermission', self.userCanDelete() or self.userCanWrite())
        pane.data('status.locked', True)
        pane.dataFormula('status.unlocked', '!locked', locked='^status.locked', _init=True)
        pane.dataScript('dummy', "SET status.locked=false;", fire='^status.unlock',
                        _if='unlockPermission',
                        unlockPermission='=usr.unlockPermission',
                        forbiddenMsg='!!You cannot unlock this table',
                        _else='alert(forbiddenMsg)')

        #-----
        pane.dataFormula('form.locked', 'statusLocked || recordLocked', statusLocked='^status.locked',
                         recordLocked='=form.recordLocked', fired='^recordLoaded')
        pane.dataFormula('form.unlocked', '!locked', locked='^form.locked')
        pane.dataFormula('form.canWrite', '(!locked ) && writePermission', locked='^form.locked',
                         writePermission='=usr.writePermission', _init=True)
        pane.dataFormula('form.canDelete', '(!locked) && deletePermission', locked='^form.locked',
                         deletePermission='=usr.deletePermission', _init=True)

        pane.dataScript('dummy', "FIRE form.save=true", newidx='=form.newidx',
                        result='^form.dlgAction', _if="result=='save'")

        pane.dataScript('dummy', """genro.dlg.ask(askTitle,saveMessage,{save:saveButton,forget:cancelButton},'form.dlgAction');
                                   """, newidx='^form.newidx', modified='=form.modified',
                        askTitle="!!Unsaved changes",
                        saveMessage='!!There are unsaved changes', saveButton='!!Save changes',
                        cancelButton='!!Forget changes',
                        _if='modified', _else='SET list.selectedIndex=newidx;')

        pane.dataScript('form.isValid', "return true", fired='^form.save', data='=form.record',
                        _if='genro.dataValidate(data)', locked='=form.locked',
                        _else="if(!locked){genro.focusOnError(data); return false;}")

        pane.dataRpc('form.save_result', 'save', data='=form.record', _POST=True, isValid='^form.isValid',
                     _if='isValid')
        pane.dataScript('dummy', """SET gnr.message=msg;
                                   FIRE form.reload=true;
                                  """, record='=form.record',
                        msg='!!Record saved', pkey='=form.save_result',
                        result='^form.save_result', _if='result',
                        _else='SET gnr.message=result;')

    def main(self, root, pkey=None, **kwargs):
        root.script("""genro.checkBeforeUnload= function(e){
                       if (genro.getData('form.modified')){
                           return "Hai delle modifiche non salvate vuoi uscire senza salvarle?";
                       }
                }""")
        client, top = self.publicRoot(root)
        self.joinConditions()

        pkey = pkey or '2JHw7OSLEdynuQAX8t4orw'

        #--
        client.dataRecord('form.record', self.maintable,
                          pkey=pkey, _init=True, sqlContextName='sql_record',
                          _onResult='this.dataLoggerReset("form.record", "form.modified", "form.changes");FIRE recordLoaded=true;')

        self.formController(client)

        onchange_script = """function(path,changed){
                                          if(path.indexOf('form.record')==0){
                                              if(changed){alert('campo cambiato')}
                                              else{alert('campo tornato al valore iniziale')}
                                              
                                          }
        
        }
        """
        self.formToolbar(client)
        form = client.contentPane(layoutAlign='client',
                                  _class='pbl_formContainerClient tablewiew', nodeId='formPane',
                                  margin_top='0px', border_top='0px', datapath='form.record')

        self.formBase(form, disabled='^form.locked')


    def rpc_save(self, data=None, **kwargs):
        try:
            self.tblobj.insertOrUpdate(data)
            self.db.commit()

            return ('ok', dict(_pkey=data[self.tblobj.pkey]))
        except Exception:
            return 'error'

