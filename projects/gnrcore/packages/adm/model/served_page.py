# encoding: utf-8
from __future__ import with_statement
from datetime import datetime

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('served_page', pkey='page_id', name_long='!!Served page',
                        name_plural='!!Served pages', broadcast='old')
        tbl.column('page_id', size='22', name_long='!!Page id')
        tbl.column('pagename', name_long='!!Page name')
        tbl.column('connection_id', size='22', group='_').relation('connection.id', mode='foreignkey',
                                                                   onDelete='cascade')
        tbl.column('start_ts', 'DH', name_long='!!Start ts')
        tbl.column('end_ts', 'DH', name_long='!!Start ts')
        tbl.column('end_reason', size=':12', name_long='!!End Reason')

    def getLivePages(self, connection_id=None, current_page_id=None):
        where = ['$end_ts is null']
        if connection_id:
            where.append('$connection_id=:connection_id')
        if current_page_id:
            where.append('$page_id!=:current_page_id')
        return self.query(where=' AND '.join(where),
                          connection_id=connection_id,
                          current_page_id=current_page_id).fetch()


    def pageLog(self, event, page_id=None):
        if event == 'open':
            self.openServedPage()
        else:
            self.closeServedPage(page_id=page_id, end_ts=datetime.now(), end_reason='unload')

    def closePendingPages(self, connection_id=None, end_ts=None, end_reason=None):
        for page in self.getLivePages(connection_id=connection_id):
            self.closeServedPage(page['page_id'], end_ts=end_ts, end_reason=end_reason)

    def openServedPage(self):
        page = self.db.application.site.currentPage
        record_served_page = dict(page_id=page.page_id, end_reason=None, end_ts=None,
                                  connection_id=page.connection_id,
                                  start_ts=datetime.now(), pagename=page.basename)
        with self.db.tempEnv(connectionName='system'):
            self.insertOrUpdate(record_served_page)
            self.db.commit()

    def closeServedPage(self, page_id=None, end_ts=None, end_reason=None):
        page = self.db.application.site.currentPage
        page_id = page_id or page.page_id
        with self.db.tempEnv(connectionName='system'):
            self.batchUpdate(dict(end_ts=end_ts or datetime.now(), end_reason=end_reason),
                             where='$page_id=:page_id', page_id=page_id)
            self.db.commit()

    def closeOrphans(self):
        with self.db.tempEnv(connectionName='system'):
            self.batchUpdate(dict(end_reason='expired', end_ts=datetime.now()),
                             where='@connection_id.end_ts IS NOT NULL')
            self.db.commit()

            
