# encoding: utf-8

from datetime import datetime
from gnr.core.gnrbag import Bag

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('task', rowcaption='task', pkey='id')
        self.sysFields(tbl)
        tbl.column('table_name',name_long='!!Table')
        tbl.column('task_name',name_long='!!Task name') # char(4)
        tbl.column('command',name_long='!!Command')
        tbl.column('month',name_long='!!Month')
        tbl.column('day',name_long='!!Day')
        tbl.column('weekday',name_long='!!Weekday')
        tbl.column('hour',name_long='!!Hour')
        tbl.column('minute',name_long='!!Minute')
        tbl.column('parameters',dtype='X',name_long='!!Parameters') # date
        tbl.column('last_execution','DH',name_long='!!Last Execution')
        tbl.column('log_result', 'B', name_long='!!Log Result')
        
    def isTaskScheduledNow(self,task,timestamp):
        def expandIntervals(string_interval,limits=None):
            inlist=string_interval and string_interval.strip().split(',') or []
            inlist = inlist or []
            outlist=[]
            for single in inlist:
                if '-' in single:
                    start,stop = single.split('-')
                    start = int(start)
                    stop = int(stop)
                    if limits:
                        start = max(start,limits[0])
                        stop = min(stop,limits[1])
                    for single_in_interval in range(start,stop+1):
                        outlist.append(single_in_interval)
                else:
                    single = int(single)
                    if limits and single>=limits[0] and single<=limits[1]:
                        outlist.append(single)
            return outlist
                    
        month=expandIntervals(task['month'],limits=(1,12))
        if month and timestamp.month not in month:
            return False
        day=expandIntervals(task['day'],limits=(1,31))
        if day and timestamp.day not in day:
            return False
        weekday=expandIntervals(task['weekday'],limits=(0,6))
        if weekday and timestamp.weekday() not in weekday:
            return False
        hour=expandIntervals(task['hour'],limits=(0,23))
        if hour and timestamp.hour not in hour:
            return False
        minute=expandIntervals(task['minute'],limits=(0,59))
        if minute and timestamp.minute not in minute:
            return False
        return True

    def findTasks(self, timestamp=None):
        timestamp = timestamp or datetime.now()
        all_tasks = self.query('*,parameters').fetch()
        tasks_to_run = []
        for task in all_tasks:
            try:
                if self.isTaskScheduledNow(task,timestamp):
                    tasks_to_run.append(task)
            except:
                pass
                # build error record here interval Syntax error
        return tasks_to_run
        
    def loadTask(self, table=None, page=None, command=None):
        pkg,tablename = table.split('.')
        command = command or 'task_%s:Main' %tablename
        if ':' not in command:
            command ='%s:Main'%command
        task_class = page.importTableResource(table,command)
        if task_class:
            return task_class(page=page)
    
    def runTask(self, task, page=None, timestamp=None):
        taskObj = self.loadTask(table=task['table_name'], command=task['command'], page=page)
        if not taskObj:
            return
        try:
            if task['parameters']:
                taskObj.batch_parameters = dict(task['parameters'])
            tmp_result = taskObj.run() or ''
            log_result = task['log_result']
            if isinstance(tmp_result, Bag):
                result = tmp_result
            elif isinstance(tmp_result, dict):
                result=Bag(tmp_result)
            else:
                result=Bag(result=tmp_result)
        except Exception, e:
            raise
            result = Bag(error=unicode(e))
            log_result = True
        if log_result:
            with self.db.tempEnv(connectionName='system'):
                self.db.table('task.result').insert(dict(task_id=task['id'],result=result, result_time=timestamp))
                self.db.commit()
        
    def runScheduled(self, page=None):
        tasks = self.findTasks()
        for task in tasks:
            self.runTask(task, page=page)
                
    
if __name__=='__main__':
    from gnr.app.gnrapp import GnrApp
    a=GnrApp('testgarden')
    a.db.table('task.task').findTasks()