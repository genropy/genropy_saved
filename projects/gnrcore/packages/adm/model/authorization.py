# encoding: utf-8
import random
import string
from datetime import datetime, date
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('authorization', pkey='code', name_long='!!Authorization',
                        name_plural='!!Authorizations')
        self.sysFields(tbl, id=False, user_ins=True)
        tbl.column('code', size=':8', validate_case='U', name_long='!!Code', unmodifiable=True)
        tbl.column('user_id', size='22', name_long='!!User id').relation('user.id', mode='foreignkey') #Not used DEPRECATED
        tbl.column('use_ts', 'DH', name_long='!!Used datetime')
        tbl.column('used_by', name_long='!!Used by')
        tbl.column('note', name_long='!!Note')
        tbl.column('usage_scope', name_long='!!Use Scope')
        tbl.column('remaining_usages', 'L', name_long='!!Remaining usages', default=1)
        tbl.column('expiry_date', 'D', name_long='!!Expire Date')

    def generate_code(self):
        code = ''.join(random.Random().sample(string.letters + string.digits, 8)).upper()
        for c in (('0', 'M'), ('1', 'N'), ('O', 'X'), ('L', 'Y'), ('I', 'Z')):
            code = code.replace(c[0], c[1])
        return code
    
    #@public_method #(tags='admin')
    def authorize(self, reason=None,commit=True, **kwargs):
        return self.new_authorization(reason=reason, commit=commit, **kwargs)

    def new_authorization(self, reason=None, usage_scope=None, commit=True, **kwargs):
        record = dict(note=reason, usage_scope=usage_scope)
        record.update(kwargs)
        self.insert(record)
        print record
        if commit:
            self.db.commit()
        return record['code']

    def getUsageScopes(self):
        return ','.join(['%s:%s' %(k[6:], getattr(self,k)()) for k in dir(self) if k.startswith('scope_')])

    def use_auth(self, code, usage_scope=None, username=None):
        record = self.query(where='$code=:code AND $usage_scope=:usage_scope', code=code, usage_scope=usage_scope,
                            for_update=True).fetch()
        if not record:
            raise self.exception('Authoriziation %s not found for scope %s' % (code, usage_scope))
        record= record[0]
        record['use_ts'] = datetime.now()
        record['used_by'] = username or self.db.currentEnv.get('user')
        record['remaining_usages'] = record['remaining_usages'] - 1
        self.update(record)
    
    @public_method     
    def validate_auth_code(self, value=None, usage_scope=None, **kwargs):
        if not value:
            return
        return self.check_auth(value, usage_scope=usage_scope)
        
    def check_auth(self, code, usage_scope=None):
        exists = self.query(where='$code=:code AND $usage_scope=:s', code=code, s=usage_scope).fetch()
        if not exists:
            return False
        coupon = exists[0]
        if coupon['expiry_date'] and coupon['expiry_date'] < date.today():
            return False
        remaining_usages = coupon['remaining_usages']
        if remaining_usages <= 0:
            return False
        return True
        
    def newPkeyValue(self):
        toassign=True
        record_data = dict()
        while toassign:
            record_data['code'] = self.generate_code()
            toassign = self.existsRecord(record_data)
        return record_data['code']


    def trigger_onInserting(self, record_data):
        if not record_data.get('remaining_usages'):
            record_data['remaining_usages']=1
        if not record_data.get('expiry_date'):
            record_data['expiry_date']=self.db.workdate
        
            