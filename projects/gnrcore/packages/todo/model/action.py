# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('action',pkey='id',name_long='Action',name_plural='Action',caption_field='id')
        self.sysFields(tbl)
        tbl.column('action_type_id',size='22',name_long='!!Action type',group='_').relation('action_type.id',mode='foreignkey', onDelete='raise')
        tbl.column('action_fields',dtype='X',name_long='!!Fields',subfields='action_type_id')
        tbl.column('assigned_to',size=':50',name_long='!!Assigned to',indexed=True)
        tbl.column('priority',size=':2',name_long='!!Priority',values='NW:Now,UR:Urgent,HG:High,LW:Low')
        tbl.column('days_before',dtype='I',name_long='!!Days before')
        tbl.column('done_ts',dtype='DH',name_long='!!Done ts',indexed=True)

        tbl.aliasColumn('typename',relation_path='@action_type_id.name')
