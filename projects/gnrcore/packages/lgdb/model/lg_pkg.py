# encoding: utf-8

from gnr.core.gnrdecorator import public_method
from gnr.sql.gnrsql import GnrSqlDb

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('lg_pkg',pkey='code',name_long='Legacy package',name_plural='Legacy package',caption_field='code')
        self.sysFields(tbl, id=False)
        tbl.column('code',size=':15',name_long='Code')
        tbl.column('name', name_long='Name')
        tbl.column('legacy_db',name_long='Legacy db')
        tbl.column('legacy_schema',name_long='Legacy schema')
        tbl.column('description',name_long='Description')

    @public_method
    def importPackage(self, pkg_code=None,legacy_schema=None, import_mode=None,legacy_db=None):
        if legacy_db and legacy_db is not True:
            self.importFromLegacyDb(legacy_db,pkg_code=pkg_code,legacy_schema=legacy_schema)
            return
        pkg = self.db.package(pkg_code)
        lg_table = self.db.table('lgdb.lg_table')
        lg_col = self.db.table('lgdb.lg_column')
        if import_mode == 'restart':
            lg_table.deleteSelection(where='$lg_pkg=:pkg_code', pkg_code=pkg_code)
        for tblobj in pkg.tables.values():
            lg_table.importTable(pkg_code, tblobj, import_mode=import_mode)


    @public_method(caption='Update tables legacy count',topic='form_batch',_lockScreen=dict(thermo=True))
  # def actionMenu_updateTableLegacyCount(self,pkey=None,**kwargs):   
  #     #SELECT NUMBER_ROWS, DATA_SIZE FROM qsys2.systablestat 
  #     lg_table = self.db.table('lgdb.lg_table')
  #     record = self.record(pkey).output('dict')
  #     externaldb = self.getLegacyDb(record['legacy_db'])
  #     z = externaldb.execute('SELECT table_name,NUMBER_ROWS, DATA_SIZE FROM qsys2.systablestat').fetchall()
  #     print(x)

    def importFromLegacyDb(self,legacy_db,pkg_code,legacy_schema=None):
        externaldb = self.getLegacyDb(legacy_db)
        schemadata = externaldb.adapter.listElements('schemata')
        lg_table = self.db.table('lgdb.lg_table')
        
        for schema in schemadata:
            if legacy_schema!=schema:
                continue
            tables = externaldb.adapter.listElements('tables', schema=schema, comment=True)
            for tbl,comment in tables:
                primary_key = externaldb.adapter.getPkey(schema=legacy_schema, table=tbl)
                lg_table.insert(lg_table.newrecord(lg_pkg=pkg_code,primary_key=primary_key or None,
                                            description=comment,
                                            name=tbl,sqlname='{}.{}'.format(schema,tbl)))
            return

    def getLegacyDb(self,legacy_db):
        connection_params = self.db.application.config['legacy_db'].getAttr(legacy_db)
        dbname=connection_params['dbname'] or connection_params['filename']
        if connection_params['implementation']!='sqlite':
            connection_params['host'] = connection_params.get('host') or 'localhost'
        return GnrSqlDb(implementation=connection_params['implementation'],
                            dbname=dbname,application=self.db.application,
                            host=connection_params.get('host'),user=connection_params.get('user'),
                            password = connection_params.get('password'),
                            port=connection_params.get('port'))

