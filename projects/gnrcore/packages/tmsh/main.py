#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrlang import instanceMixin

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Timesheet utilities',sqlschema='tmsh',sqlprefix=True,
                    name_short='Tmsh', name_long='Tmsh', name_full='Tmsh')
                    

    def onBuildingDbobj(self):
        for pkgNode in self.db.model.src['packages']:
            if not pkgNode.value:
                continue
            tables = pkgNode.value['tables']
            for tblNode in tables:
                if f'{tblNode.label}_tmsh' in tables:
                    self._plugResourceTable(tblNode) 

    def _plugResourceTable(self,tblNode):
        tblNode.attr['tmsh_resource'] = True
        pkeyColNode = tblNode.value.getNode(f"columns.{tblNode.attr['pkey']}")
        pkeyColNode.attr['onInserted'] = 'onInsertedResource'

    def onApplicationInited(self):
        self.mixinMultidbMethods()

    def mixinMultidbMethods(self):
        db = self.application.db
        for pkg,pkgobj in db.packages.items():
            for tbl,tblobj in pkgobj.tables.items():
                if tblobj.attributes.get('tmsh_resource'):
                    instanceMixin(tblobj.dbtable, TmshResourceTable)


class TmshResourceTable(object):
    def timesheetTable(self):
        return self.db.table(f'{self.fullname}_tmsh')

    def onInsertedResource(self,record):
        self.initializeTimesheet(record)
    
    def initializeTimesheet(self,record):
        tstable = self.timesheetTable()
        tsrec = tstable.newrecord(resource_id=record[self.pkey])
        tstable.insert(tsrec)

    def touch_timesheet(self,record,old_record=None):
        self.initializeTimesheet(record)
    
                

class Table(GnrDboTable):
    pass
