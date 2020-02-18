# encoding: utf-8

from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('lg_pkg',pkey='code',name_long='Legacy package',name_plural='Legacy package',caption_field='code')
        self.sysFields(tbl, id=False)
        tbl.column('code',size=':15',name_long='Code')
        tbl.column('name', name_long='Name')
        tbl.column('description',name_long='Description')

    @public_method
    def importPackage(self, pkg_code, import_mode=None):
        pkg = self.db.package(pkg_code)
        lg_table = self.db.table('lgdb.lg_table')
        lg_col = self.db.table('lgdb.lg_column')
        if import_mode == 'restart':
            lg_table.deleteSelection(where='$lg_pkg=:pkg_code', pkg_code=pkg_code)
        for tblobj in pkg.tables.values():
            lg_table.importTable(pkg_code, tblobj, import_mode=import_mode)
