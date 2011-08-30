# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrtask : gnr task controller
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari
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

from gnr.core.gnrbaseservice import GnrBaseService
import warnings

class TaskHandler(GnrBaseService):
    """A class for mail management."""
    service_name = 'mail'
    
    def __init__(self, parent=None):
        self.site = parent
        #if not 'task' in self.site.gnrapp.packages:
        #    warnings.warn("[task] task package missing",
        #                  stacklevel=2)
        self.db = self.site.gnrapp.db
    
    def addTask(self, tableName=None,taskName=None,command=None,month=None,day=None,
                    weekday=None,hour=None,minute=None,parameters=None):
        if not 'task' in self.site.gnrapp.packages:
            warnings.warn("[task] trying to use taskHandler but task package is missing",
                          stacklevel=2)
            return
        new_task=dict()
        new_task['table_name']=tableName
        new_task['task_name']=taskName
        new_task['command']=command
        new_task['month']=month
        new_task['day']=day
        new_task['weekday']=weekday
        new_task['hour']=hour
        new_task['minute']=minute
        new_task['parameters']=parameters
        with self.db.tempEnv(connectionName='system'):
            self.db.table('task.task').insert(new_task)
            self.db.commit()
    
    def listTask(self, table=None):
        return self.db.table('task.task').query(where='$table_name ILIKE :tbl_name',tbl_name='"%%%s%%"'%table)
        