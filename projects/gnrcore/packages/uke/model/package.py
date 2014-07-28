# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('package',pkey='package_identifier',name_long='!!Package',
                      name_plural='!!Packages',rowcaption='$package_identifier',caption_field='package_identifier')
        self.sysFields(tbl,id=False)
        tbl.column('code',name_long='!!Code',validate_notnull=True,validate_notnull_error='!!Required',_sendback=True,unmodifiable=True)
        tbl.column('project_code',name_long='Project code',validate_notnull=True,validate_notnull_error='!!Required',_sendback=True,unmodifiable=True).relation('project.code', mode='foreignkey', 
                                                                                        onDelete='raise',
                                                                                        relation_name='packages')
        tbl.column('description',name_long='!!Description')
        tbl.column('package_identifier',unique=True)

    def trigger_onInserting(self, record_data):
        record_data['package_identifier'] = "%s/%s" %(record_data['project_code'],record_data['code'])