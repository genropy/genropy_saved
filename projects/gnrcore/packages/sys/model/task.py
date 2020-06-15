# encoding: utf-8

from __future__ import print_function
from builtins import range
from builtins import object
from datetime import datetime
from dateutil import rrule
from gnr.core.gnrbag import Bag

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('task', rowcaption='$task_name',caption_field='task_name', pkey='id',name_long='!!Task',name_plural='!!Tasks')
        self.sysFields(tbl)
        tbl.column('table_name',name_long='!!Table')
        tbl.column('task_name',name_long='!!Task name',name_short='!!Name') # char(4)
        tbl.column('command',name_long='!!Command')
        tbl.column('month',name_long='!!Month',values='1:[!!Jan],2:[!!Feb],3:[!!Mar],4:[!!Apr],5:[!!May],6:[!!Jun],7:[!!Jul],8:[!!Aug],9:[!!Sep],10:[!!Oct],11:[!!Nov],12:[!!Dec]')
        tbl.column('day',name_long='!!Day',values=','.join([str(x+1) for x in range(31)]))
        tbl.column('weekday',name_long='!!Weekday',values='0:[!!Sun],1:[!!Mon],2:[!!Tue],3:[!!Wed],4:[!!Thu],5:[!!Fri],6:[!!Sat]')
        tbl.column('hour',name_long='!!Hour',values=','.join([str(x) for x in range(24)]))
        tbl.column('minute',name_long='!!Minute',values=','.join([str(x) for x in range(60)]))
        tbl.column('frequency', dtype='L', name_long='!!Freq.(min)')
        tbl.column('parameters',dtype='X',name_long='!!Parameters') # date
        tbl.column('last_scheduled_ts','DH',name_long='!!Last scheduled',indexed=True)
        tbl.column('last_execution_ts','DH',name_long='!!Last Execution')
        tbl.column('last_error_ts','DH',name_long='!!Last Error')
        tbl.column('last_error_info','X',name_long='!!Last Error Info')
        tbl.column('run_asap','B',name_long='!!Run ASAP')
        tbl.column('max_workers','L',name_long='!!Max workers') # Allows concurrent execution of the same task
        tbl.column('log_result', 'B', name_long='!!Log Task')
        tbl.column('user_id',size='22',group='_',name_long='User id').relation('adm.user.id', mode='foreignkey', onDelete='raise')
        tbl.column('date_start','D',name_long='!!Start Date')
        tbl.column('date_end','D',name_long='!!End Date')
        tbl.column('stopped','B',name_long='!!Stopped')
        tbl.column('worker_code',size=':10',name_long="Worker code",indexed=True)
        tbl.column('saved_query_code',size=':40',name_long="!![en]Query")
        tbl.formulaColumn('active_workers',select=dict(table='sys.task_execution',
            where="$task_id=#THIS.id AND $start_ts IS NOT NULL AND $end_ts IS NULL",
            columns='COUNT(*)'
        ),dtype='N',name_long='N.Active workers')
        tbl.formulaColumn('last_result_ts',
            select=dict(table='sys.task_result',
            columns='MAX($start_time)', where='$task_id = #THIS.id'),
            name_long='!!Last Execution')

    def isTaskScheduledNow(self,task,timestamp):
        result = []
        if task['run_asap']:
            return '*'
        if task['frequency']:
            last_scheduled_ts = task['last_scheduled_ts']
            if last_scheduled_ts is None or (timestamp-last_scheduled_ts).seconds/60.>=task['frequency']:
                return '*'
            else:
                return False
        months =  [int(x.strip()) for x in task['month'].split(',')] if task['month'] else range(1,13)
        days = [int(x.strip()) for x in task['day'].split(',')] if task['day'] else range(1,32)
        hours = [int(x.strip()) for x in task['hour'].split(',')] if task['hour'] else range(0,24)
        minutes = [int(x.strip()) for x in task['minute'].split(',')] if task['minute'] else range(0,60)
        hm = []
        for h in hours:
            for m in minutes:
                hm.append(h*60+m)
        y,m,d,h,minutes = timestamp.year,timestamp.month,timestamp.day,timestamp.hour,timestamp.minute
        if m not in months or d not in days:
            return False
        curr_hm = h*60+minutes
        hmlist = [g for g in hm if g<=curr_hm]
        if not hmlist:
            return False
        key_hm = max(hmlist)
        result = '-'.join([str(y),str(m),str(d),str(int(key_hm/60)),str(key_hm%60)])
        return result

    def findTasks(self, timestamp=None):
        timestamp = timestamp or datetime.now()
        all_tasks = self.query(where='$stopped IS NOT TRUE').fetch()
        tasks_to_run = []
        for task in all_tasks:
            reason = self.isTaskScheduledNow(task,timestamp)
            if reason:
                tasks_to_run.append((task['id'],reason))
        return tasks_to_run

    def getBtcClass(self, table=None, page=None, command=None):
        pkg,tablename = table.split('.')
        command = command or 'task_%s:Main' %tablename
        if ':' not in command:
            command ='%s:Main'%command
        return page.importTableResource(table,command)
        
    def loadTask(self, table=None, page=None, command=None):
        task_class = self.getBtcClass(table=table, page=page, command=command)
        if task_class:
            return task_class(page=page,resource_table=page.db.table(table))

    def runTask(self, task, page=None, timestamp=None):
        log_record = Bag()
        start_time = datetime.now()
        log_record['start_time'] = start_time
        log_record['task_id'] =task['id']
        taskObj = self.loadTask(table=task['table_name'], command=task['command'], page=page)
        if not taskObj:
            return
        try:
            taskparameters = task['parameters']
            tmp_result = taskObj(parameters=Bag(taskparameters))
            tmp_result = tmp_result or ''
            log_result = task['log_result']
            if isinstance(tmp_result, Bag):
                result = tmp_result
            elif isinstance(tmp_result, dict):
                result=Bag(tmp_result)
            else:
                result=Bag(result=tmp_result)
        except Exception as e:
            self.db.table('sys.error').writeException(description='Error in task %s %s :%s' %(task['table_name'],task['command'],str(e)))
            result = Bag(error=str(e))
            log_result = True
        if log_result:
            log_record['end_time'] = datetime.now()
            log_record['result'] = result
            self.db.table('sys.task_result').insert(log_record)
