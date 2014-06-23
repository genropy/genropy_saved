from __future__ import with_statement
from datetime import datetime

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('locked_record', pkey='id', name_long='!!Locked Record',
                        name_plural='!!Locked records')
        tbl.column('id', size='22', name_long='!!id')
        tbl.column('lock_ts', 'DH', name_long='!!Date and Time')
        tbl.column('lock_table', size=':64', name_long='!!Table')
        tbl.column('lock_pkey', size=':64', name_long='!!locked record')
        tbl.column('page_id', size='22', name_long='!!Page_id')
        tbl.column('connection_id', size='22', name_long='!!Connection_id')
        tbl.column('username', size=':32', name_long='!!User')
        tbl.index('lock_table,lock_pkey', unique=True)

    def lockRecord(self, page, table, pkey):
        if not isinstance(pkey, basestring):
            pkey = str(pkey)
        record = dict(lock_ts=datetime.now(),
                      lock_table=table,
                      lock_pkey=pkey,
                      page_id=page.page_id,
                      username=page.user,
                      connection_id=page.connection_id
                      )
        with self.db.tempEnv(connectionName='system'):
            try:
                self.insert(record)
                self.db.commit()
                result = (True, record['id'])
            except self.db.connection.IntegrityError:
                self.db.rollback()
                result = (False, dict(self.query('$id,$lock_ts AS ts,$page_id,$connection_id,$username',
                                                 where='$lock_table=:table AND lock_pkey=:pkey',
                                                 table=table, pkey=pkey, addPkeyColumn=False).fetch()[0]))
        return result

    def existingLocks(self, lockId=None, connection_id=None, page_id=None, username=None):
        if self.db.read_only:
            return []
        where = None
        if lockId:
            where = '$id=:lockId'
        elif page_id:
            where = '$page_id = :page_id'
        elif connection_id:
            where = '$connection_id=:connection_id'
        elif username:
            where = '$username=:username'
        if where:
            query = self.query(where=where, lockId=lockId, page_id=page_id,
                               username=username, connection_id=connection_id)
        else:
            query = self.query()
        return query.fetch()

    def clearExistingLocks(self, lockId=None, connection_id=None, page_id=None, username=None):
        if self.db.read_only:
            return
        with self.db.tempEnv(connectionName='system'):
            for lock in self.existingLocks(lockId=lockId, connection_id=connection_id, page_id=page_id,
                                           username=username):
                self.delete(lock)
            self.db.commit()
