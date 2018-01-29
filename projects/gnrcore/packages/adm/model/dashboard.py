# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('dashboard', pkey='dashboard_key', name_long='!!Dashboard', 
                    name_plural='!!Dashboards',caption_field='dashboard_key',pkey_values='pkgid,code')
        self.sysFields(tbl,id=False)
        tbl.column('dashboard_key', size=':40', name_long='!!Dashboard key')
        tbl.column('pkgid', size=':15', name_long='!!Package')
        tbl.column('code', size=':15', name_short='!!Code')
        tbl.column('description', size=':40', name_long='!!Description')
        tbl.column('widget', size=':30', name_long='!!Widget',default='tabContainer',
                    values='tabContainer:Tabs,stackContainer:Buttons')  
        tbl.column('data', dtype='X', name_long='!!Data')