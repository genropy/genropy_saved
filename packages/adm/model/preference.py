# encoding: utf-8
from __future__ import with_statement
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import RecordNotExistingError

MAIN_PREFERENCE = '_mainpref_'

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('preference', pkey='code', name_long='!!Preference',
                        name_plural='!!Preference')
        self.sysFields(tbl, id=False)
        tbl.column('code', size='12', name_long='!!Code')
        tbl.column('data', 'X', name_long='!!Data')

        # NOTE: these are private APIs, please use <your_package>.getPreference()

        # and <your_package>.setPreference() to get and set preferences.

    def getPreference(self, path, pkg='', dflt=None):
        result = self.loadPreference()
        # NOTE: due to the way bags work,
        #       'data.%(path)s' will be used if pkg is ''
        # 
        result = result['data']
        if result and path != '*':
            result = result['%s.%s' % (pkg, path)]
        return result or dflt


    def setPreference(self, path, value, pkg=''):
        record = self.loadPreference(for_update=True)
        record['data.%s.%s' % (pkg, path)] = value
        self.savePreference(record)

    def loadPreference(self, pkey=MAIN_PREFERENCE, for_update=False):
        with self.db.tempEnv(connectionName='system'):
            try:
                record = self.record(pkey=pkey, for_update=for_update).output('bag')
            except RecordNotExistingError:
                record = self.newrecord(code=pkey, data=Bag())
        return record

    def savePreference(self, record):
        with self.db.tempEnv(connectionName='system'):
            self.insertOrUpdate(record)
            self.db.commit()
