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

from psutil import pid_exists
from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag
from gnr.web.gnrwsgisite import GnrWsgiSite

from datetime import datetime
from time import sleep
from random import randrange
import os

class GnrTaskScheduler(object):
    def __init__(self,instancename,interval=None):
        self.app = GnrApp(instancename,enabled_packages=['gnrcore:sys'])
        self.db = self.app.db
        self.interval = interval or 60
        self.pid = os.getpid()
        self.tasktbl = self.db.table('sys.task')
        self.exectbl = self.db.table('sys.task_execution')

    def start(self):
        while True:
            self.writeTaskExecutions()
            self.db.closeConnection()
            sleep(self.interval)
    
    def writeTaskExecutions(self):
        now = datetime.now()
        task_to_schedule = self.tasktbl.findTasks()
        existing_executions = self.exectbl.query(columns='$reasonkey,$status',
                                                where='$reasonkey IN :reasonkeys',
                                                reasonkeys=['%s_%s' %t for t in task_to_schedule if t[1]!='*']).fetchAsDict('reasonkey')
        taskToUpdate = []
        for t,reason in task_to_schedule:
            reasonkey = None
            if reason!='*':
                reasonkey = '%s_%s' %(t,reason)
            if reasonkey not in existing_executions:
                self.exectbl.insert(self.exectbl.newrecord(task_id=t,exec_reason=reason,reasonkey=reasonkey))
                taskToUpdate.append(t)

        self.tasktbl.batchUpdate(dict(last_scheduled_ts=now,run_asap=None),_pkeys=taskToUpdate)
        self.checkAlive()
        self.db.commit()
    
    def checkAlive(self):
        f = self.exectbl.query(columns='$pid',distinct=True,where='$start_ts IS NOT NULL AND $end_ts IS NULL').fetch()
        deadpid = [r['pid'] for r in f if not pid_exists(r['pid'])]
        self.exectbl.batchUpdate(dict(pid=None,start_ts=None),where='$pid IN :deadpid AND $end_ts IS NULL',deadpid=deadpid)

class GnrTaskWorker(object):
    def __init__(self,sitename,interval=None,code=None):
        self.site = GnrWsgiSite(sitename)
        self.db = self.site.db
        self.tblobj = self.db.table('sys.task_execution')
        self.interval = interval or 60
        self.code = code
        self.pid = os.getpid()
        wherelist = ["$start_ts IS NULL","$task_stopped IS NOT TRUE","$task_active_workers<COALESCE($task_max_workers,1)"]
        if self.code:
            wherelist.append('$task_worker_code=:wcode')
        self.where = ' AND '.join(['( %s )' %c for c in wherelist])
        print('inited')
    
    def taskToExecute(self):
        f = True
        while f:
            f = self.tblobj.query(where=self.where,wcode=self.code,for_update='SKIP LOCKED',
                                    limit=1,order_by='$__ins_ts').fetch()
            if f:
                print('.')
                rec = f[0]
                oldrec = dict(rec)
                rec['start_ts'] = datetime.now()
                rec['pid'] = self.pid
                self.tblobj.update(rec,oldrec)
                self.db.commit()
                yield rec['id']

    def runTask(self, task_execution):
        page = self.site.dummyPage
        self.site.currentPage = page
        page._db = None
        page.db
        log_record = Bag()
        start_time = datetime.now()
        log_record['start_time'] = start_time
        log_record['task_id'] =task_execution['id']
        taskObj = self.db.table('sys.task').loadTask(table=task_execution['task_table'], command=task_execution['task_command'], page=page)
        if not taskObj:
            return Bag()
        taskparameters = task_execution['parameters']
        with self.db.tempEnv(connectionName='execution'):
            taskObj(parameters=Bag(taskparameters),task_execution_record=task_execution)
    
    def start(self):
        while True:
            for te_pkey in self.taskToExecute():
                print('eseguo task', te_pkey)
                with self.tblobj.recordToUpdate(te_pkey,for_update='SKIP LOCKED',
                                                virtual_columns='$task_table,$task_name.$task_parameters,$task_command') as task_execution:
                    self.runTask(task_execution)
                    task_execution['end_ts'] = datetime.now()
                self.db.commit()
            self.db.closeConnection()
            sleep(randrange(self.interval-10,self.interval+10))
