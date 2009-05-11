# encoding: utf-8
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('project', name_short='Project', name_long='Project',
                        name_plural='Projects',pkey='id',rowcaption='$name')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('name',size=':20',name_long='!!Name',indexed='y')
        tbl.column('client_id',size='22',name_long='!!Client'
                  ).relation('client.id',mode='foreignkey',onDelete='raise')
        tbl.column('description',name_long='!!Description')
        tbl.column('project_note','X',name_long='!!Notes')
        tbl.aliasColumn('company',relation_path='@client_id.company',group='03')
