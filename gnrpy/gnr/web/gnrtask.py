#-*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2019 Softwell sas - Milano 
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

#Copyright (c) 2019 Softwell. All rights reserved.

from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag
from gnr.web.gnrdummysite import GnrDummySite
from datetime import datetime
from time import sleep
from random import randrange
import os

class GnrTaskScheduler(object):
    def __init__(self,instancename,interval=None):
        self.app = GnrApp(instancename)
        self.db = self.app.db
        self.interval = interval or 60
        self.pid = os.getpid()

    def start(self):
        while True:
            self.db.table('sys.task').writeTaskExecutions()
            sleep(self.interval)

class GnrTaskWorker(object):
    def __init__(self,sitename,interval=None):
        self.site = GnrDummySite(sitename)
        self.db = self.site.db
        self.tblobj = self.db.table('sys.task_execution')
        self.interval = interval or 60
        self.pid = os.getpid()
    
    def taskToExecute(self):
        f = True
        while f:
            f = self.tblobj.query(where="""$start_ts IS NULL AND $task_stopped IS NOT TRUE""",
                                    columns="""*,$task_max_workers,$task_active_workers""",
                                    limit=1,for_update=True,order_by='$__ins_ts').fetch()
            if f:
                rec = f[0]
                task_max_workers = rec['task_max_workers'] or 1
                if rec['task_active_workers']>=task_max_workers:
                    self.tblobj.delete(rec)
                    self.db.commit()
                else:
                    oldrec = dict(rec)
                    rec['start_ts'] = datetime.now()
                    rec['pid'] = self.pid
                    self.tblobj.update(rec,oldrec)
                    self.db.commit()
                    yield rec['id']

    def runTask(self, task_execution):
        page = self.site.dummyPage
        page._db=self.db
        page._db.clearCurrentEnv()
        log_record = Bag()
        start_time = datetime.now()
        log_record['start_time'] = start_time
        log_record['task_id'] =task_execution['id']
        print 'table',task_execution['task_table'],'command',task_execution['task_command']
        taskObj = self.db.table('sys.task').loadTask(table=task_execution['task_table'], command=task_execution['task_command'], page=page)
        if not taskObj:
            print 'manca task'
            return Bag()
        try:
            taskparameters = task_execution['parameters']
            with self.db.tempEnv(connectionName='execution'):
                tmp_result = taskObj(parameters=Bag(taskparameters),task_execution_record=task_execution)
            tmp_result = tmp_result or ''
            if isinstance(tmp_result, Bag):
                result = tmp_result
            elif isinstance(tmp_result, dict):
                result=Bag(tmp_result)
            else:
                result=Bag(dict(result=tmp_result))
        except Exception, e:
            self.db.table('sys.error').writeException(description='Error in task %s %s :%s' %(task_execution['table_name'],task_execution['task_command'],str(e)))
            result = Bag(dict(error=unicode(e)))
        return result
    
    def start(self):
        while True:
            for te_pkey in self.taskToExecute():
                with self.tblobj.recordToUpdate(te_pkey,virtual_columns='$task_table,$task_name.$task_parameters,$task_command') as task_execution:
                    result = self.runTask(task_execution)
                    if result['error']:
                        task_execution['is_error'] = True
                    task_execution['end_ts'] = datetime.now()
                self.db.commit()
            sleep(randrange(self.interval-10,self.interval+10))
