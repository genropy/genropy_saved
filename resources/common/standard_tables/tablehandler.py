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
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent

class TableHandler(BaseComponent):
    _legacy=True
    py_requires = """standard_tables/tablehandler_core,
                     standard_tables/tablehandler_form,
                     standard_tables/tablehandler_list,
                     standard_tables/tablehandler_extra:TagsHandler,
                     standard_tables/tablehandler_extra:QueryHelper,
                     standard_tables/tablehandler_extra:FiltersHandler,
                     standard_tables/tablehandler_extra:HierarchicalViewHandler,
                    foundation/userobject:UserObject,foundation/dialogs"""
    css_requires = 'standard_tables/tablehandler'
    js_requires = 'standard_tables/tablehandler'

    def userCanWrite(self):
        return self.application.checkResourcePermission(self.tableWriteTags(), self.userTags)

    def userCanDelete(self):
        return self.application.checkResourcePermission(self.tableDeleteTags(), self.userTags)

    def tableWriteTags(self):
        return 'superadmin'

    def tableDeleteTags(self):
        return 'superadmin'

    def rpc_onLoadingSelection(self, selection):
        """ovverride if you need"""
        pass

    def rowsPerPage(self):
        return 25

    def hiddencolumnsBase(self):
        return

    def hierarchicalViewConf(self):
        return None

    def hierarchicalEdit(self):
        return None

    def conditionBase(self):
        return (None, None)

    def enableFilter(self):
        #to deprecate
        return True

    def tableRecordCount(self):
        """redefine to avoid the count query"""
        return True

    def formTitleBase(self, pane):
        pane.data('form.title', self.tblobj.attributes.get('name_long', 'Record'))

    def columnsBase(self):
        return ''

    def orderBase(self):
        return ''

    def onSavingFormBase(self):
        """JS ONCALLING OF RPCSAVING PROCESS
           params inside js:
           data: what you send
           form: the formBase js object
           if you return false the rpc is not called;
        """
        return None

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fields(self.columnsBase())
        return struct

    def main(self, root, **kwargs):
        root.data('selectedPage', 0)
        root.data('gnr.maintable', self.maintable)
        root.dataController("genro.dom.setClass(dojo.body(),'form_edit',selectedPage==1)", selectedPage="^selectedPage")
        self.userObjectDialog()
        self.deleteUserObjectDialog()
        self.parsePageParameters(root, **kwargs)
        self.joinConditions()

        if hasattr(self.tblobj, 'hasRecordTags') and self.tblobj.hasRecordTags():
            self.tags_main(root)
        self.setOnBeforeUnload(root, cb="genro.getData('gnr.forms.formPane.changed')",
                               msg="!!There are unsaved changes, do you want to close the page without saving?")

        pages = root.rootStackContainer(title='^list.title_bar', selected='^selectedPage',
                                                         _class='pbl_mainstack', nodeId='tablehandler_mainstack')
        self.pageList(pages)
        self.pageForm(pages)


    def parsePageParameters(self, root, pkey=None, **kwargs):
        if pkey == '*newrecord*':
            self.startWithNewRecord(root)
        elif pkey and self.db.table(self.maintable).existsRecord(pkey):
            self.startWithExistingRecord(root, pkey)

    def startWithNewRecord(self, root):
        root.dataController('FIRE list.newRecord; FIRE status.unlock', _fired='^gnr.onStart', _delay=4000)

    def startWithExistingRecord(self, root, pkey):
        root.data('initialPkey', pkey)

    def joinConditions(self):
        """hook to define all join conditions for retrieve records related to the current edited record
           using method self.setJoinCondition
        """
        pass

    def pluralRecordName(self):
        return self.tblobj.attributes.get('name_plural', 'Records')

    def getSelection_filters(self):
        return self.clientContext['filter.%s' % self.pagename]

    def _infoGridStruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('lbl', name='Field', width='10em', headerStyles='display:none;', cellClasses='infoLabels', odd=False)
        r.cell('val', name='Value', width='10em', headerStyles='display:none;', cellClasses='infoValues', odd=False)
        return struct

    def selectionBatchRunner(self, pane, title='', resultpath='aux.cmd.result', fired=None, batchFactory=None,
                             rpc=None, thermofield=None, thermoId=None, endScript=None,
                             stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        """Prepare a batch action on the maintable with a thermometer
           @param pane: it MUST NOT BE a container. Is the pane where selectionBatchRunner
                  append dataController and dialog.
           @param resultpath: the path into the datastore where the result is stored.
           @param fired: the path where you fire the event that launch the dataRpc of selectionBatchRunner.
           @param batchFactory: is used instead of rpc. Name of the Factory Class, used as
                                plugin of table, which executes the standard batch action.
           @param rpc: is used instead of batchFactory. The name of the custum rpc you can use for the batch
                       for every selected row.
        """
        thermoId = None
        if thermofield:
            thermoId = self.getUuid()
            self.thermoDialog(pane, thermoId=thermoId, title=title, fired=fired, alertResult=True)
        pane.dataRpc(resultpath, rpc or 'app.runSelectionBatch',
                     table=self.maintable, selectionName='=list.selectionName',
                     batchFactory=batchFactory, thermoId=thermoId,
                     thermofield=thermofield,
                     pkeys='==genro.wdgById("maingrid").getSelectedPkeys()',
                     fired=fired, _onResult=endScript,
                     stopOnError=stopOnError, forUpdate=forUpdate, onRow=onRow, **kwargs)

        dlgid = self.getUuid()
        pane.dataController('genro.wdgById(dlgid).show()', _if='errors',
                            dlgid=dlgid, errors='^%s.errors' % resultpath)
        d = pane.dialog(nodeId=dlgid, title="!!Errors in batch execution", width='27em', height='27em')
        struct = self.newGridStruct()
        rows = struct.view().rows()
        rows.cell('caption', width='8em', name='!!Caption')
        rows.cell('error', name='!!Error')
        d.div(position='absolute', top='28px', right='4px',
              bottom='4px', left='4px').includedView(storepath='%s.errors' % resultpath, struct=struct)

    def xmlDebug(self, bag, filename):
        bag.toXml(self.pageLocalDocument('%s.xml' % filename))

    