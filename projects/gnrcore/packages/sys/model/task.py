# encoding: utf-8

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
        
        tbl.formulaColumn('active_workers',select=dict(table='sys.task_execution',
            where="$task_id=#THIS.id AND $start_ts IS NOT NULL AND $end_ts IS NULL",
            columns='COUNT(*)'
        ),dtype='N',name_long='N.Active workers')
        tbl.formulaColumn('last_execution_ts',
            select=dict(table='sys.task_result',
            columns='MAX($start_time)', where='$task_id = #THIS.id'),
            name_long='!!Last Execution')
        
    #def trigger_onInserted(self, record):
    #    self.resetTaskCache()
#
    #def trigger_onDeleted(self, record, **kwargs):
    #    self.resetTaskCache()
#
    #def trigger_onUpdated(self, record, old_record=None, **kwargs):
    #    self.resetTaskCache()
#
    #def resetTaskCache(self):
    #    with self.db.application.site.register.globalStore() as gs:
    #        gs.setItem('TASK_TS',datetime.now())

    def isTaskScheduledNow(self,task,timestamp):
        if task['run_asap']:
            return True
        if task['frequency']:
            last_scheduled_ts = task['last_scheduled_ts']
            return last_scheduled_ts is None or (timestamp-last_scheduled_ts).seconds/60.>=task['frequency']
        expandIntervals = self.expandIntervals
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

    def expandIntervals(self, string_interval,limits=None):
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

    def expandTaskPeriods(self, task):
        return dict(
            month=self.expandIntervals(task['month'],limits=(1,12)),
            day=self.expandIntervals(task['day'],limits=(1,31)),
            weekday=self.expandIntervals(task['weekday'],limits=(0,6)),
            hour=self.expandIntervals(task['hour'],limits=(0,23)),
            minute=self.expandIntervals(task['minute'],limits=(0,59))
        )

    def checkInterval(self, ts, periods):
        for k, v in periods.items():
            time_element = getattr(ts,k)
            if callable(time_element):
                time_element = time_element()
            if v and time_element not in v:
                return False
        return True

    def taskExecutions(self, task, timespan=None):
        result = []
        timestamps = rrule.rrule(rrule.MINUTELY,count=timespan,dtstart=datetime.now())
        periods = self.expandTaskPeriods(task)
        last_execution_ts = task['last_execution_ts']
        frequency = task['frequency']
        run_asap = task['run_asap']
        for ts in timestamps:
            do_run = False
            if run_asap:
                do_run = True
            elif frequency:
                if last_execution_ts is None or (ts-last_execution_ts).seconds/60.>=frequency:
                    do_run = True
            elif self.checkInterval(ts, periods):
                do_run = True
            if do_run:
                run_asap = False
                last_execution_ts = ts
                task_execution = dict(execution_ts=ts,
                    command = task['command'],
                    parameters=task['parameters'],
                    task=task)
                result.append(task_execution)
        return result

    def getNextExecutions(self, timespan=60):
        result = []
        now = datetime.now()
        def cb(task):
            result.extend(self.taskExecutions(dict(task),timespan=timespan))
            if task['run_asap']:
                task['run_asap'] = False
            else:
                return False
        self.batchUpdate(updater=cb,columns='*,$last_execution_ts', where='$stopped IS NOT TRUE', )
        self.db.commit()
        return sorted(result, key=lambda t:t.get('execution_ts'))


    def findTasks(self, timestamp=None):
        timestamp = timestamp or datetime.now()
        all_tasks = self.query('*,parameters',where='$stopped IS NOT TRUE').fetch()
        tasks_to_run = []
        for task in all_tasks:
            try:
                if self.isTaskScheduledNow(task,timestamp):
                    tasks_to_run.append(task)
            except:
                print 'build error record here interval Syntax error'
                # build error record here interval Syntax error
        return tasks_to_run

    def loadTask(self, table=None, page=None, command=None):
        pkg,tablename = table.split('.')
        command = command or 'task_%s:Main' %tablename
        if ':' not in command:
            command ='%s:Main'%command
        task_class = page.importTableResource(table,command)
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
        except Exception, e:
            self.db.table('sys.error').writeException(description='Error in task %s %s :%s' %(task['table_name'],task['command'],str(e)))
            result = Bag(error=unicode(e))
            log_result = True
        if log_result:
            log_record['end_time'] = datetime.now()
            log_record['result'] = result
            self.db.table('sys.task_result').insert(log_record)

    def runScheduled(self, page=None):
        tasks = self.findTasks()
        now =  datetime.now()
        for task in tasks:
            with self.recordToUpdate(task['id']) as task_rec:
                scheduledNow = self.isTaskScheduledNow(task_rec,now)
                if not scheduledNow:
                    continue
                try:
                    self.runTask(task_rec, page=page)
                    task_rec['last_execution_ts'] = now
                    task_rec['last_error_ts'] = None
                    task_rec['last_error_info'] = None
                except Exception, e:
                    task_rec['last_error_ts'] = now
                    result = Bag(error=unicode(e))
                    task_rec['last_error_info'] = result
                task_rec['run_asap'] = False
            with self.db.tempEnv(connectionName='system'):
                self.db.commit()

    def writeTaskExecutions(self):
        tblexecutions = self.db.table('sys.task_execution')
        now = datetime.now()
        task_to_schedule = self.findTasks()
        print 'find %i task' %len(task_to_schedule)
        def cb(row):
            tblexecutions.insert(tblexecutions.newrecord(task_id=row['id']))
            row['last_scheduled_ts'] = now
            row['run_asap'] = False
        self.batchUpdate(cb,_pkeys=[r['id'] for r in task_to_schedule])
        self.db.commit()
    
    
    
if __name__=='__main__':
    from gnr.app.gnrapp import GnrApp
    a=GnrApp('testgarden')
    a.db.table('sys.task').findTasks()