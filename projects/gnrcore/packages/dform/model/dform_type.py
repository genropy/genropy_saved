# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('dform_type', pkey='id', name_long='!![en]DForm type', 
                    name_plural='!![en]DForm types',caption_field='name')
        self.sysFields(tbl,hierarchical='name,code',counter=True,hierarchical_root_id=True)
        tbl.column('name', size=':40', name_long='Name')
        tbl.column('description', name_long='Description')
        tbl.column('code', size=':10', name_long='!![en]Code')