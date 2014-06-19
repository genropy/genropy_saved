# encoding: utf-8
class Table(object):
    #deprecated: records inside this table must be moved inside table sys.task

    def config_db(self, pkg):
        tbl =  pkg.table('task', rowcaption='$task_name',caption_field='$task_name', pkey='id',name_long='!!Task',name_plural='!!Tasks')
        self.sysFields(tbl)
        tbl.column('table_name',name_long='!!Table')
        tbl.column('task_name',name_long='!!Task name') # char(4)
        tbl.column('command',name_long='!!Command')
        tbl.column('month',name_long='!!Month',values='!!1:Jan,2:Feb,3:Mar,4:Apr,5:May,6:Jun,7:Jul,8:Aug,9:Sep,10:Oct,11:Nov,12:Dec')
        tbl.column('day',name_long='!!Day',values=','.join([str(x+1) for x in range(31)]))
        tbl.column('weekday',name_long='!!Weekday',values='!!0:Sun,1:Mon,2:Tue,3:Wed,4:Thu,5:Fri,6:Sat')
        tbl.column('hour',name_long='!!Hour',values=','.join([str(x) for x in range(24)]))
        tbl.column('minute',name_long='!!Minute',values=','.join([str(x) for x in range(60)]))
        tbl.column('parameters',dtype='X',name_long='!!Parameters') # date
        tbl.column('last_execution','DH',name_long='!!Last Execution')
        tbl.column('log_result', 'B', name_long='!!Log Result')
        tbl.column('user_id',size='22',group='_',name_long='User id').relation('adm.user.id', mode='foreignkey', onDelete='raise')
        tbl.column('date_start','D',name_long='!!Start Date')
        tbl.column('date_end','D',name_long='!!End Date')
        tbl.column('stopped','B',name_long='!!Stopped')
                