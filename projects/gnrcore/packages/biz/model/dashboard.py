# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('dashboard', pkey='dashboard_key', name_long='!!Dashboard', 
                    name_plural='!!Dashboards',caption_field='dashboard_key',pkey_columns='pkgid,code')
        self.sysFields(tbl,id=False)
        tbl.column('dashboard_key', size=':100', name_long='!!Dashboard key',notnull=True)
        tbl.column('pkgid', size=':15', name_long='!!Package',validate_notnull=True)
        tbl.column('code', size=':50', name_short='!!Code',validate_notnull=True)
        tbl.column('description', size=':40', name_long='!!Description')
        tbl.column('widget', size=':30', name_long='!!Widget',default='tabContainer',
                    values='tabContainer:Tabs,stackContainer:Buttons')  
        tbl.column('data', dtype='X', name_long='!!Data',_sendback=True)
        tbl.column('private', dtype='B', name_long='!!Private')
        
    def defaultValues(self):
        data = Bag()
        data['dashboards'] = Bag()
        data['items'] = Bag()
        return dict(data=data)

    def trigger_onUpdating(self,record=None,old_record=None):
        if self.fieldsChanged('data',record,old_record):
            self.db.table('biz.dashboard_config').deleteSelection(where='$dashboard_key=:dk',dk=record['dashboard_key'])
