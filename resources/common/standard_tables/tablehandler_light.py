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
import sys
from gnr.web.gnrbaseclasses import BaseComponent


class TableHandlerLight(BaseComponent):
    py_requires = "gnrcomponents/selectionhandler"
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

    def hierarchicalViewConf(self):
        return None

    def conditionBase(self):
        return (None, None)

    def filterBase(self):
        return

    def tableRecordCount(self):
        """redefine to avoid the count query"""
        return True

    def formTitleBase(self, pane):
        pane.data('form.title', self.tblobj.attributes.get('name_long', 'Record'))

    def columnsBase(self):
        return ''

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fields(self.columnsBase())
        return struct

    def formBaseDimension(self):
        return dict(height='400px', width='600px')

    def filterOnBase(self, struct):
        try:
            default_field = self.queryBase().get('column', None) # default to the standard_table's queryBase()
        except:
            default_field = None
        filterOn = []
        for k, cell in enumerate(struct['#0']['#0']):
            if cell.attr['dtype'] == 'A' or cell.attr['dtype'] == 'T':
                name = cell.attr['name']
                field = cell.attr['field']
                if k > 0:
                    if name.startswith('!!'):
                        name = name[2:]
                filter_ = '%s:%s' % (name, field)
                if field == default_field:
                    filterOn.insert(0, filter_)
                else:
                    filterOn.append(filter_)
        return ','.join(filterOn)

    def printActionBase(self):
        return False

    def exportActionBase(self):
        return 'xlwt' in sys.modules

    def gridLabel(self):
        return None

    def defaultsBase(self):
        return dict()

    def main(self, root, pkey=None, **kwargs):
        self.formTitleBase(root)
        condition = self.conditionBase()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        bc, top, bottom = self.pbl_rootBorderContainer(root, title=self.tblobj.attributes.get('name_plural', 'Records'),
                                                       id='mainBC_center')
        bc.dataController("FIRE #maingrid.reload;", _onStart=True)
        dimension = self.formBaseDimension()
        struct = self.lstBase(self.newGridStruct(maintable=self.maintable))
        filterOn = self.filterOnBase(struct)
        defaults = self.defaultsBase()
        self.selectionHandler(bc, label=self.gridLabel(), datapath="list",
                              nodeId='maingrid', table=self.maintable,
                              print_action=self.printActionBase(),
                              export_action=self.exportActionBase(),
                              box_class='tablehandler_light_body',
                              struct=struct, selectionPars=dict(where=condition, order_by=self.orderBase(), **condPars),
                              dialogPars=dict(height=dimension['height'], width=dimension['width'],
                                              toolbarPars=dict(lock_action=True, add_action=self.userCanWrite(),
                                                               del_action=self.userCanDelete(),
                                                               save_action=self.userCanWrite()),
                                              form_datapath='form',
                                              record_datapath='form.record', title='^form.title', formCb=self.formBase,
                                              dlgPars=dict(centerOn="mainBC_center"), **defaults), lock_action=True,
                              checkMainRecord=False, hasToolbar=True, filterOn=filterOn)
        controller = bc.dataController(datapath="selection")
        controller.data('usr.writePermission', self.userCanWrite())
        controller.data('usr.deletePermission', self.userCanDelete())
        controller.data('usr.unlockPermission', self.userCanDelete() or self.userCanWrite())
        controller.dataFormula('status.locked', True, _onStart=True)
        controller.dataFormula('form.canWrite', '(!locked ) && writePermission',
                               locked='^status.locked', writePermission='=usr.writePermission')
        controller.dataFormula('form.canDelete', '(!locked) && deletePermission',
                               locked='^status.locked', deletePermission='=usr.deletePermission')


    def listBottomPane(self, bc, **kwargs):
        """
        CALLBACK of standardTable
        """
        bottomPane_list = sorted([func_name for func_name in dir(self) if func_name.startswith('bottomPane_')])
        if not bottomPane_list:
            return
        pane = bc.contentPane(_class='listbottompane', datapath='list.bottom', overflow='hidden', **kwargs)
        fb = pane.formbuilder(cols=15, border_spacing='2px')
        for func_name in bottomPane_list:
            getattr(self, func_name)(fb.div(datapath='.%s' % func_name[11:]))

