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
Component for managing  userobject:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag


class UserObject(BaseComponent):
    py_requires = 'foundation/recorddialog,foundation/dialogs:Dialogs'

    def deleteUserObjectDialog(self):
        page = self.pageSource()

        def cb_center(parentBc, **kwargs):
            pane = parentBc.contentPane(**kwargs)
            pane.div("!!You cannot undo this operation. Are you sure?")

        dlg = self.simpleDialog(page, dlgId='deleteUserObject', title='^.pars.title',
                                datapath='gnr.userobject.delete_dlg',
                                height='100px', width='300px', cb_center=cb_center, centerOn='_pageRoot')
        dlg.dataRpc('dummy', 'deleteUserObject', id='=.pars.pkey', _if='id', _fired='^.save',
                    _onResult='FIRE .close;FIRE .deleted;')

    def userObjectDialog(self):
        saveKwargs = dict(changesOnly=False, saveAlways=True)
        self.recordDialog('%s.userobject' % self.package.name, '^.pkey', dlgId='userobject_dlg',
                          datapath='gnr.userobject.create_dlg', width='28em', height='28ex',
                          title='^.pars.title', centerOn='_pageRoot',
                          formCb=self._uo_form, default_objtype='=.pars.objtype',
                          default_pkg=self.package.name, default_tbl=self.maintable,
                          default_userid=self.user, saveKwargs=saveKwargs,
                          onSaved="""FIRE .saved;""", savePath='.savedPkey')

    def _uo_form(self, parentContainer, disabled, table, **kwargs):
        pane = parentContainer.contentPane(margin_top='5px')
        pane.dataFormula(".data", "databag", _fired="^.id", databag='=.#parent.pars.data')
        fb = pane.formbuilder(cols=3, dbtable=table, width='320px', border_spacing='5px')
        fb.div(lbl='Flags', colspan=1)
        fb.field('quicklist', lbl='', label='!!Quicklist', colspan=1, tooltip='!!Available in shortcuts')
        fb.field('private', lbl='', label='!!Private', colspan=1, tooltip='!!Only for me.')
        fb.field('code', autospan=3, tooltip='!!Dotted path and name')
        fb.field('authtags', autospan=3, lbl='!!Permissions', tooltip='!!Comma separated list of auth tags.')
        fb.simpleTextarea(lbl='!!Description', value='^.description', height='3.75em',
                          width='100%', border='1px solid gray', lbl_vertical_align='top', colspan=3)

    def rpc_listUserObject(self, objtype=None, tbl=None, onlyQuicklist=False, **kwargs):
        result = Bag()
        if hasattr(self.package, 'listUserObject'):
            objectsel = self.package.listUserObject(objtype=objtype, userid=self.user, tbl=tbl,
                                                    onlyQuicklist=onlyQuicklist, authtags=self.userTags)
            if objectsel:
                for i, r in enumerate(objectsel.data):
                    attrs = dict([(str(k), v) for k, v in r.items()])
                    result.setItem(r['code'] or 'r_%i' % i, None, **attrs)
        return result

    def rpc_loadUserObject(self, userid=None, **kwargs):
        data, metadata = self.package.loadUserObject(userid=userid or self.user, **kwargs)
        return (data, metadata)

    #old stuff maintained for compatibility reasons
    def rpc_saveUserObject(self, userobject, userobject_attr):
        userobject_attr = dict([(str(k), v) for k, v in userobject_attr.items()])
        userobject_attr['userid'] = userobject_attr.get('userid') or self.user
        self.package.saveUserObject(userobject, **userobject_attr)
        self.db.commit()

    def rpc_deleteUserObject(self, id):
        self.package.deleteUserObject(id)
        self.db.commit()

######### OLD STUFF USE  userObjectDialog INSTEAD OF ########################

class UserObjectOld(BaseComponent):
    def saveUserObjectDialog(self, pane, datapath, objtype, objectdesc):
        pane.div(_class='icnBaseSave buttonIcon', connect_onclick='FIRE aux.save.%s' % objtype)
        dlgBC = self.hiddenTooltipDialog(pane, dlgId='%s_saveDlg' % objtype, title='!!Save %s' % objectdesc,
                                         width='30em', height='20ex', fired='^aux.save.%s' % objtype,
                                         datapath=datapath,
                                         bottom_left='!!Close', bottom_left_action='FIRE .close_save;',
                                         bottom_right='!!Save', bottom_right_action='FIRE .close_save; FIRE .save;')

        dlgpane = dlgBC.contentPane(region='center', _class='pbl_dialog_center')
        fb = dlgpane.formbuilder(cols=2, border_spacing='4px')
        dlgpane.dataController("genro.wdgById('%s_saveDlg').onCancel();" % objtype, _fired="^.close_save")

        fb.textBox(lbl='!!Code', value='^.resource?code', width='10em', colspan=1)
        fb.checkbox(lbl='!!Shortlist', value='^.resource?inside_shortlist')
        fb.simpleTextarea(lbl='!!Description', value='^.resource?description',
                          width='20em', lbl_vertical_align='top', rowspan=2, colspan=2)
        fb.textBox(lbl='!!Permissions', value='^.resource?auth_tags', width='10em')
        fb.checkbox(lbl='!!Private', value='^.resource?private')
        dlgpane.dataRpc('.saveResult', 'save_%s' % objtype, userobject='=.resource',
                        _fired='^.save', _POST=True, _onResult='FIRE .saved = true')

    def loadUserObjectDialog(self, pane, datapath, objtype, objectdesc):
        pane.div(_class='icnBaseFolder buttonIcon', connect_onclick='FIRE aux.load.%s' % objtype)
        dlgId = '%s_loadDlg' % objtype
        dlgBC = self.hiddenTooltipDialog(pane, dlgId=dlgId, title='!!Load %s' % objectdesc,
                                         width='30em', height='30ex', fired='^aux.load.%s' % objtype,
                                         datapath=datapath,
                                         bottom_left='!!Close', bottom_left_action='FIRE .close_load;',
                                         bottom_right='!!Load', bottom_right_action='FIRE .close_load; FIRE .load;')

        dlg = dlgBC.borderContainer(region='center', _class='pbl_dialog_center')
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

        buttons.div(connect_onclick='genro.wdgById("%s").onCancel();FIRE .new;' % dlgId, _class='icnBaseAdd buttonIcon',
                    float='left')
        buttons.div(connect_onclick='FIRE .delete', _class='icnBaseTrash buttonIcon', float='left')
        delDlgId = '%s_del_dlg' % objtype
        deleteBC = self.hiddenTooltipDialog(dlg, dlgId=delDlgId, title="!!Confirm deletion",
                                            width="18em", height="16ex", fired='^.delete',
                                            close_action='FIRE .close_del',
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
                    

