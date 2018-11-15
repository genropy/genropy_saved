# encoding: utf-8
from datetime import datetime
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('external_token', pkey='id', name_long='!!Messages',
                        name_plural='!!Messages')
        tbl.column('id', size='22', name_long='!!id')
        tbl.column('datetime', 'DH', name_long='!!Date and Time')
        tbl.column('expiry', 'DH', name_long='!!Expiry')
        tbl.column('allowed_user', size=':32', name_long='!!Destination user')
        tbl.column('connection_id', size='22', name_long='!!Connection Id', indexed=True).relation('adm.connection.id')
        tbl.column('max_usages', 'I', name_long='!!Max uses')
        tbl.column('allowed_host', name_long='!!Allowed host')
        tbl.column('page_path', name_long='!!Page path')
        tbl.column('method', name_long='!!Method')
        tbl.column('parameters', dtype='X', name_long='!!Parameters')
        tbl.column('exec_user', size=':32', name_long='!!Execute as user').relation('adm.user.username')


    def create_token(self, page_path=None, expiry=None, allowed_host=None, allowed_user=None,
                     connection_id=None, max_usages=None, method=None, parameters=None, exec_user=None):
        record = dict(
                page_path=page_path,
                expiry=expiry,
                allowed_host=allowed_host,
                allowed_user=allowed_user,
                connection_id=connection_id,
                max_usages=max_usages,
                method=method,
                exec_user=exec_user,
                parameters=Bag(parameters))
        self.insert(record)
        return record['id']

    def use_token(self, token, host=None, commit=False):
        record = self.record(id=token, ignoreMissing=True).output('bag')
        record = self.check_token(record, host)
        if record:
            if record['max_usages']:
                self.db.table('sys.external_token_use').insert(
                        dict(external_token_id=record['id'], host=host, datetime=datetime.now()))
                if commit:
                    self.db.commit()
            user = record['exec_user']
            return record['method'], [], dict(record['parameters'] or {}), user
        return None, None, None, None

    def check_token(self, record, host=None):
        record = self.recordAs(record,'dict')
        if not record:
            return False
        if host:
            pass
        if record['expiry'] and record['expiry'] >= datetime.now():
            return False
        if record['max_usages']:
            uses = self.db.table('sys.external_token_use').query(where='external_token_id =:cid',
                                                                 cid=record['id']).count()
            if uses >= record['max_usages']:
                return False
        return record
        

    def authenticatedUser(self,token):
        token_record = self.check_token(token)
        if token_record and token_record.get('exec_user'):
            user = token_record.get('exec_user')
            if not user:
                return None
            if token_record['max_usages']:
                self.use_token(token_record['id'])
            return user