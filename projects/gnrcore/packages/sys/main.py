#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='sys',
                    comment='sys',
                    name_short='System',
                    name_long='System',
                    name_full='System',_syspackage=True)
                    

    def onApplicationInited(self):
        pass
        
    def onSiteInited(self):
        db=self.application.db
        if db.package('task'):
            tasktbl = db.table('sys.task')
            new_tasks = tasktbl.query().fetch()
            if not new_tasks:
                oldtasks = db.table('task.task').query().fetch()
                if oldtasks:
                    print '******* moving task records: FROM task package to sys package *******'
                    for task in oldtasks:
                        tasktbl.insert(dict(task))
                    db.commit()

class Table(GnrDboTable):
    def isInStartupData(self):
        return False
        