# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('task_execution', pkey='id', name_long='!!Task execution', name_plural='!!Task executions')
        self.sysFields(tbl)
        tbl.column('task_id',size='22',name_long='!!Task ID').relation('sys.task.id', mode='foreignkey',
                                                                        relation_name='executions',onDelete='cascade')
        tbl.column('result','X',name_long='!!result') # varchar(40)
        tbl.column('logbag','X',name_long='!!Logbag')
        tbl.column('errorbag','X',name_long='!!Errors')

        tbl.column('pid', dtype='L', name_long='!!Process id', name_short='!!PID')
        tbl.column('start_ts',dtype='DH',name_long='!!Start Time',indexed=True) # date
        tbl.column('end_ts',dtype='DH',name_long='!!End Time',indexed=True) # date
        tbl.column('is_error','B',name_long='!!Is Error',indexed=True)
        tbl.column('exec_reason', size=':20', name_long='!!Exec reason')
        tbl.column('reasonkey',size=':60',indexed=True)


        tbl.aliasColumn('task_table','@task_id.table_name',name_long='!!Table')
        tbl.aliasColumn('task_name','@task_id.task_name',name_long='!!Task name',name_short='!!Name') # char(4)
        tbl.aliasColumn('task_command','@task_id.command',name_long='!!Task command',name_short='!!Command') # char(4)

        tbl.aliasColumn('task_stopped','@task_id.stopped',dtype='B',name_long='!!Stopped')
        tbl.aliasColumn('task_parameters','@task_id.parameters',dtype='X',name_long='!!Parameters')
        tbl.aliasColumn('task_saved_query','@task_id.saved_query_code',dtype='B',name_long='!!Saved query')

        tbl.aliasColumn('task_worker_code','@task_id.worker_code',dtype='L',name_long='!!Task worker code')

        tbl.aliasColumn('task_max_workers','@task_id.max_workers',dtype='L',name_long='!!Task Max workers')
        tbl.aliasColumn('task_active_workers','@task_id.active_workers',dtype='L',name_long='!!Task Active workers')

        tbl.formulaColumn('status',"""
            (CASE WHEN $is_error IS TRUE THEN 'error'
                 WHEN $end_ts IS NOT NULL THEN 'completed'
                 WHEN $start_ts IS NOT NULL THEN 'running'
                 ELSE 'waiting'
            END)
        """,name_long='Status')