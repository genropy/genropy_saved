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
from gnr.sql.gnrsql_exceptions import GnrSqlException,GnrSqlSaveChangesException,GnrSqlExecutionException
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace

class TableHandlerLight(BaseComponent):
    py_requires="gnrcomponents/selectionhandler"
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

    def rpc_onLoadingSelection(self,selection):
        """ovverride if you need"""
        pass

    def rowsPerPage(self):
        return 25

    def hierarchicalViewConf(self):
        return None

    def conditionBase(self):
        return (None,None)

    def filterBase(self):
        return

    def tableRecordCount(self):
        """redefine to avoid the count query"""
        return True

    def formTitleBase(self,pane):
        pane.data('form.title',self.tblobj.attributes.get('name_long','Record'))

    def columnsBase(self):
        return ''

    def lstBase(self, struct):
        r=struct.view().rows()
        r.fields(self.columnsBase())
        return struct

    def formBaseDimension(self):
        return dict(height='400px',width='600px')

    def filterOnBase(self,struct):
        filterOn = []
        for k,cell in enumerate(struct['#0']['#0']):
            if cell.attr['dtype']=='A' or cell.attr['dtype']=='T':
                name = cell.attr['name']
                field = cell.attr['field']
                if k>0:
                    if name.startswith('!!'):
                        name = name[2:]
                filterOn.append('%s:%s' %(name,field))
        return ','.join(filterOn)

    def printActionBase(self):
        return False

    def exportActionBase(self):
        return True

    def gridLabel(self):
        return None

    def main(self, root, pkey=None, **kwargs):
        condition=self.conditionBase()
        condPars={}
        if condition:
            condPars=condition[1] or {}
            condition=condition[0]

        bc,top,bottom = self.pbl_rootBorderContainer(root,title='^list.title_bar',id='mainBC_center',margin='5px')
        bc.dataController("FIRE #maingrid.reload;",_onStart=True)
        dimension = self.formBaseDimension()
        struct = self.lstBase(self.newGridStruct())
        filterOn = self.filterOnBase(struct)
        self.selectionHandler(bc,label=self.gridLabel(),datapath="selection",
                               nodeId='maingrid',table=self.maintable,
                               print_action=self.printActionBase(),
                               export_action=self.exportActionBase(),
                               struct=struct,selectionPars=dict(where=condition,order_by=self.orderBase,**condPars),
                               dialogPars=dict(height=dimension['height'],width=dimension['width'],
                                               record_datapath='form.record',
                                               title='^form.title',formCb=self.formBase,
                                               dlgPars=dict(centerOn="mainBC_center")),
                                checkMainRecord=False,
                               footer=self.footerBase,filterOn=filterOn)
    def footerBase(self,pane,**kwargs):
        pane.data('usr.writePermission',self.userCanWrite())
        pane.data('usr.deletePermission',self.userCanDelete())
        pane.data('usr.unlockPermission',self.userCanDelete() or self.userCanWrite())
        pane.data('status.locked',True)
        pane.dataFormula('status.unlocked','!locked',locked='^status.locked',_init=True)

        pane.dataFormula('status.unlocked','!locked',locked='^status.locked',_onStart=True)
        pane.dataFormula('form.canWrite','(!locked ) && writePermission',
                        locked='^status.locked',writePermission='=usr.writePermission',_onStart=True)
        pane.dataFormula('form.canDelete','(!locked) && deletePermission',
                        locked='^status.locked',deletePermission='=usr.deletePermission',_onStart=True)
        pane.dataController("SET status.locked=true;",fire='^status.lock')
        pane.dataController("SET status.locked=false;",fire='^status.unlock',_if='unlockPermission',
                            unlockPermission='=usr.unlockPermission',
                            forbiddenMsg = '==  unlockForbiddenMsg || dfltForbiddenMsg',
                            unlockForbiddenMsg ='=usr.unlockForbiddenMsg',
                            dfltForbiddenMsg = "!!You cannot unlock this table",
                            _else='FIRE gnr.alert = forbiddenMsg') 
        pane.button('!!Unlock', position='absolute',right='5px',fire='status.unlock', 
                    iconClass="tb_button icnBaseLocked", showLabel=False,hidden='^status.unlocked')
        pane.button('!!Lock', position='absolute',right='5px',fire='status.lock', 
                    iconClass="tb_button icnBaseUnlocked", showLabel=False,hidden='^status.locked')
                            
    def listBottomPane(self,bc,**kwargs):
        """
        CALLBACK of standardTable
        """
        bottomPane_list = sorted([func_name for func_name in dir(self) if func_name.startswith('bottomPane_')])
        if not bottomPane_list:
            return
        pane = bc.contentPane(_class='listbottompane',datapath='list.bottom',overflow='hidden',**kwargs)
        fb = pane.formbuilder(cols=15,border_spacing='2px')
        for func_name in bottomPane_list:
            getattr(self,func_name)(fb.div(datapath='.%s' %func_name[11:]))

