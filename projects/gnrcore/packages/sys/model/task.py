# encoding: utf-8

from datetime import datetime
from gnr.core.gnrbag import Bag

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('task', rowcaption='$task_name',caption_field='$task_name', pkey='id',name_long='!!Task',name_plural='!!Tasks')
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
        tbl.column('last_execution_ts','DH',name_long='!!Last Execution')
        tbl.column('last_error_ts','DH',name_long='!!Last Error')
        tbl.column('last_error_info','X',name_long='!!Last Error Info')
        tbl.column('run_asap','B',name_long='!!Run ASAP')
        tbl.column('log_result', 'B', name_long='!!Log Task')
        tbl.column('user_id',size='22',group='_',name_long='User id').relation('adm.user.id', mode='foreignkey', onDelete='raise')
        tbl.column('date_start','D',name_long='!!Start Date')
        tbl.column('date_end','D',name_long='!!End Date')
        tbl.column('stopped','B',name_long='!!Stopped')



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

        if task['run_asap']:
            return True
        if task['frequency']:
            last_execution_ts = task['last_execution_ts']
            return last_execution_ts is None or (timestamp-last_execution_ts).seconds/60.>=task['frequency']

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
            tmp_result = taskObj(parameters=Bag(taskparameters)) or ''
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
                if not self.isTaskScheduledNow(task_rec,now):
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
            self.db.commit()
                
    
if __name__=='__main__':
    from gnr.app.gnrapp import GnrApp
    a=GnrApp('testgarden')
    a.db.table('sys.task').findTasks()